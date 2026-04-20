"""
Schedule Routes
POST /api/v1/scan/{id}/schedule  — opt a scan into weekly email digest
DELETE /api/v1/scan/{id}/schedule — opt out
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps import get_db
from ..models import Scan
from ..schemas import ScheduleRequest

router = APIRouter(prefix="/api/v1")


@router.post("/scan/{scan_id}/schedule", status_code=200)
def set_schedule(
    scan_id: UUID,
    body: ScheduleRequest,
    db: Session = Depends(get_db),
):
    """
    Opt a completed scan into (or out of) the weekly email digest.
    Stores notify_email + notify_weekly on the scan row.
    """
    scan = db.query(Scan).filter(Scan.id == str(scan_id)).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    if scan.status != "completed":
        raise HTTPException(status_code=409, detail="Can only schedule completed scans.")

    scan.notify_weekly = body.notify_weekly
    scan.notify_email  = body.notify_email if body.notify_weekly else None
    db.commit()

    return {"scheduled": body.notify_weekly, "email": scan.notify_email}


@router.delete("/scan/{scan_id}/schedule", status_code=200)
def remove_schedule(
    scan_id: UUID,
    db: Session = Depends(get_db),
):
    scan = db.query(Scan).filter(Scan.id == str(scan_id)).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")

    scan.notify_weekly = False
    scan.notify_email  = None
    db.commit()

    return {"scheduled": False}
