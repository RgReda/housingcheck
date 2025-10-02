"""In-memory alert management for market instruments."""
from __future__ import annotations

import itertools
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from services.market import MarketInstrument


@dataclass
class Alert:
    id: int
    symbol: str
    condition: str  # 'above' or 'below'
    threshold: float
    created_at: datetime
    triggered_at: datetime | None = None


class AlertManager:
    """Stores user-defined alerts in memory.

    This implementation is intentionally simple to keep the focus on the analytics
    logic. For production, alerts should be persisted in a database and tied to
    authenticated users.
    """

    def __init__(self) -> None:
        self._alerts: Dict[int, Alert] = {}
        self._lock = threading.Lock()
        self._ids = itertools.count(1)
        self._trigger_log: List[Alert] = []

    def create(self, symbol: str, condition: str, threshold: float) -> Alert:
        with self._lock:
            alert = Alert(
                id=next(self._ids),
                symbol=symbol.upper(),
                condition=condition,
                threshold=threshold,
                created_at=datetime.utcnow(),
            )
            self._alerts[alert.id] = alert
            return alert

    def delete(self, alert_id: int) -> None:
        with self._lock:
            self._alerts.pop(alert_id, None)

    def list(self) -> List[Alert]:
        with self._lock:
            return list(self._alerts.values())

    def evaluate(self, instruments: List[MarketInstrument]) -> List[Alert]:
        """Update alerts that meet their trigger condition."""
        instrument_map = {instrument.symbol.upper(): instrument for instrument in instruments}
        triggered: List[Alert] = []
        with self._lock:
            for alert in self._alerts.values():
                instrument = instrument_map.get(alert.symbol)
                if not instrument:
                    continue
                if alert.condition == "above" and instrument.last >= alert.threshold:
                    if alert.triggered_at is None:
                        alert.triggered_at = datetime.utcnow()
                        triggered.append(alert)
                elif alert.condition == "below" and instrument.last <= alert.threshold:
                    if alert.triggered_at is None:
                        alert.triggered_at = datetime.utcnow()
                        triggered.append(alert)
            if triggered:
                self._trigger_log.extend(triggered)
        return triggered

    def triggered(self) -> List[Alert]:
        with self._lock:
            return list(self._trigger_log)

    def clear_trigger_log(self) -> None:
        with self._lock:
            self._trigger_log.clear()


alert_manager = AlertManager()
