"""Casablanca Stock Exchange personal dashboard built with Flask."""
from __future__ import annotations

import threading
import time
from dataclasses import asdict
from typing import List

from flask import Flask, jsonify, render_template, request

from services.alerts import Alert, alert_manager
from services.market import MarketInstrument, market_data_provider
from services.news import news_aggregator

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"  # Required for session-based features like flash messages.


# ---------------------------------------------------------------------------
# Background jobs
# ---------------------------------------------------------------------------
def _start_alert_worker(interval: int = 30) -> None:
    """Continuously evaluate alerts against the latest market snapshot."""

    def worker() -> None:
        while True:
            snapshot = market_data_provider.get_snapshot()
            instruments: List[MarketInstrument] = snapshot.indices + snapshot.stocks
            alert_manager.evaluate(instruments)
            time.sleep(interval)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()


_start_alert_worker()


# ---------------------------------------------------------------------------
# Routes rendering HTML pages
# ---------------------------------------------------------------------------
@app.route("/")
def dashboard():
    snapshot = market_data_provider.get_snapshot()
    news = news_aggregator.fetch(limit=8)
    alerts = alert_manager.list()
    triggered = alert_manager.triggered()
    return render_template(
        "dashboard.html",
        snapshot=snapshot,
        news_items=news,
        alerts=alerts,
        triggered_alerts=triggered,
    )


@app.route("/action/<symbol>")
def action_detail(symbol: str):
    symbol = symbol.upper()
    snapshot = market_data_provider.get_snapshot()
    instrument = next((inst for inst in snapshot.stocks if inst.symbol == symbol), None)
    if instrument is None:
        instrument = next((inst for inst in snapshot.indices if inst.symbol == symbol), None)
    return render_template("instrument.html", instrument=instrument, symbol=symbol)


@app.route("/opcvm")
def opcvm():
    snapshot = market_data_provider.get_snapshot()
    return render_template("opcvm.html", funds=snapshot.opcvm)


@app.route("/news")
def news():
    news_items = news_aggregator.fetch(limit=20)
    return render_template("news.html", news_items=news_items)


@app.route("/education")
def education():
    return render_template("education.html")


# ---------------------------------------------------------------------------
# API endpoints returning JSON payloads
# ---------------------------------------------------------------------------
@app.route("/api/market")
def api_market():
    snapshot = market_data_provider.get_snapshot()
    return jsonify(
        {
            "indices": [asdict(inst) for inst in snapshot.indices],
            "stocks": [asdict(inst) for inst in snapshot.stocks],
            "opcvm": [asdict(fund) for fund in snapshot.opcvm],
            "updated_at": snapshot.updated_at.isoformat() if snapshot.updated_at else None,
        }
    )


@app.route("/api/news")
def api_news():
    news_items = news_aggregator.fetch(limit=20)
    return jsonify(
        [
            {
                "source": item.source,
                "title": item.title,
                "link": item.link,
                "published": item.published.isoformat() if item.published else None,
            }
            for item in news_items
        ]
    )


@app.route("/api/alerts", methods=["GET", "POST"])
def api_alerts():
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        symbol = payload.get("symbol", "").upper()
        condition = payload.get("condition", "above")
        threshold = payload.get("threshold")
        if not symbol or threshold is None:
            return jsonify({"error": "symbol and threshold are required"}), 400
        try:
            threshold_value = float(threshold)
        except (TypeError, ValueError):
            return jsonify({"error": "threshold must be numeric"}), 400
        if condition not in {"above", "below"}:
            return jsonify({"error": "condition must be 'above' or 'below'"}), 400
        alert = alert_manager.create(symbol=symbol, condition=condition, threshold=threshold_value)
        return jsonify(_serialize_alert(alert)), 201

    alerts = [_serialize_alert(alert) for alert in alert_manager.list()]
    return jsonify(alerts)


@app.route("/api/alerts/<int:alert_id>", methods=["DELETE"])
def api_delete_alert(alert_id: int):
    alert_manager.delete(alert_id)
    return ("", 204)


@app.route("/api/alerts/triggered", methods=["GET", "POST"])
def api_triggered_alerts():
    if request.method == "POST":
        alert_manager.clear_trigger_log()
        return ("", 204)
    triggered = [_serialize_alert(alert) for alert in alert_manager.triggered()]
    return jsonify(triggered)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def _serialize_alert(alert: Alert) -> dict:
    return {
        "id": alert.id,
        "symbol": alert.symbol,
        "condition": alert.condition,
        "threshold": alert.threshold,
        "created_at": alert.created_at.isoformat(),
        "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None,
    }


# ---------------------------------------------------------------------------
# Entry point for local execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
