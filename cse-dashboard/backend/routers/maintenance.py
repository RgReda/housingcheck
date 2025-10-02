from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from services.daily_close import DailyCloseService

router = APIRouter()


def get_daily_service() -> DailyCloseService:
    return DailyCloseService()


@router.post("/refresh/daily-close", status_code=status.HTTP_202_ACCEPTED)
def refresh_daily_close(service: DailyCloseService = Depends(get_daily_service)):
    try:
        report = service.run()
    except FileNotFoundError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok", "report": report}
