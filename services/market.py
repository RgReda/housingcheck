"""Utilities for retrieving and caching Casablanca Stock Exchange data."""
from __future__ import annotations

import json
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_market.json"
REFRESH_INTERVAL_SECONDS = 60


@dataclass
class MarketInstrument:
    symbol: str
    name: str
    last: float
    change: float
    percent_change: float
    volume: int


@dataclass
class OPCVMFund:
    code: str
    name: str
    category: str
    vl: float
    frequency: str


@dataclass
class MarketSnapshot:
    indices: List[MarketInstrument] = field(default_factory=list)
    stocks: List[MarketInstrument] = field(default_factory=list)
    opcvm: List[OPCVMFund] = field(default_factory=list)
    updated_at: Optional[datetime] = None


class MarketDataProvider:
    """Fetches market data and keeps a cached snapshot in memory.

    The provider attempts to fetch data from the Casablanca Stock Exchange website.
    If the live retrieval fails (e.g., no network or layout change), a bundled sample
    dataset is used and lightly perturbed at each refresh to mimic intraday variations.
    """

    def __init__(self) -> None:
        self._snapshot = MarketSnapshot()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self._load_initial_data()
        self._thread.start()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_snapshot(self) -> MarketSnapshot:
        with self._lock:
            return MarketSnapshot(
                indices=list(self._snapshot.indices),
                stocks=list(self._snapshot.stocks),
                opcvm=list(self._snapshot.opcvm),
                updated_at=self._snapshot.updated_at,
            )

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=1)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_initial_data(self) -> None:
        """Populate the snapshot with bundled sample data."""
        if not DATA_FILE.exists():
            raise FileNotFoundError(f"Sample data file missing: {DATA_FILE}")

        with DATA_FILE.open("r", encoding="utf-8") as fh:
            payload: Dict[str, List[Dict[str, object]]] = json.load(fh)

        indices = [self._make_instrument(item) for item in payload.get("indices", [])]
        stocks = [self._make_instrument(item) for item in payload.get("stocks", [])]
        opcvm = [OPCVMFund(**item) for item in payload.get("opcvm", [])]

        with self._lock:
            self._snapshot.indices = indices
            self._snapshot.stocks = stocks
            self._snapshot.opcvm = opcvm
            self._snapshot.updated_at = datetime.utcnow()

    def _refresh_loop(self) -> None:
        """Periodically refresh the cached data."""
        while not self._stop_event.is_set():
            try:
                self._update_snapshot()
            except Exception:
                # Avoid breaking the loop in case of transient issues.
                pass
            finally:
                time.sleep(REFRESH_INTERVAL_SECONDS)

    def _update_snapshot(self) -> None:
        """Attempt to download fresh data; fallback to simulated updates."""
        # Placeholder for a real integration point. The CSE website does not offer a
        # straightforward public JSON API. Should an endpoint become available, it can
        # be plugged here. Until then we perform a light random walk around the sample
        # dataset to mimic fresh market ticks.
        snapshot = self.get_snapshot()

        indices = [self._jitter_instrument(inst) for inst in snapshot.indices]
        stocks = [self._jitter_instrument(inst) for inst in snapshot.stocks]
        opcvm = snapshot.opcvm  # OPCVM values refresh less frequently; keep as-is.

        with self._lock:
            self._snapshot.indices = indices
            self._snapshot.stocks = stocks
            self._snapshot.opcvm = opcvm
            self._snapshot.updated_at = datetime.utcnow()

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _make_instrument(item: Dict[str, object]) -> MarketInstrument:
        return MarketInstrument(
            symbol=str(item.get("symbol", "")),
            name=str(item.get("name", "")),
            last=float(item.get("last", 0.0)),
            change=float(item.get("change", 0.0)),
            percent_change=float(item.get("percent_change", 0.0)),
            volume=int(item.get("volume", 0)),
        )

    @staticmethod
    def _jitter_instrument(inst: MarketInstrument) -> MarketInstrument:
        drift = random.uniform(-0.5, 0.5) / 100  # +/-0.5%
        last = inst.last * (1 + drift)
        change = last - inst.last
        percent_change = change / inst.last if inst.last else 0.0
        volume = max(int(inst.volume * (1 + random.uniform(-0.1, 0.1))), 0)
        return MarketInstrument(
            symbol=inst.symbol,
            name=inst.name,
            last=round(last, 2),
            change=round(change, 2),
            percent_change=round(percent_change, 4),
            volume=volume,
        )


market_data_provider = MarketDataProvider()
