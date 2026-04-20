"""
APScheduler — weekly digest job.

Runs every Monday at 09:00 UTC.
Finds all completed scans with notify_weekly=True, sends each user
a digest email with their latest scan's grade and top findings.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from ..database import SessionLocal
from ..models import Scan, Finding
from .email import send_weekly_digest

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="UTC")


def _weekly_digest_job() -> None:
    logger.info("Running weekly digest job…")
    db = SessionLocal()
    sent = 0
    try:
        # Get the most recent completed scan per email address for users who opted in
        from sqlalchemy import func

        subq = (
            db.query(func.max(Scan.created_at).label("latest"), Scan.notify_email)
            .filter(
                Scan.notify_weekly == True,
                Scan.notify_email  != None,
                Scan.status        == "completed",
            )
            .group_by(Scan.notify_email)
            .subquery()
        )

        scans = (
            db.query(Scan)
            .join(subq, (Scan.notify_email == subq.c.notify_email) &
                        (Scan.created_at   == subq.c.latest))
            .all()
        )

        for scan in scans:
            findings = (
                db.query(Finding)
                .filter(Finding.scan_id == str(scan.id))
                .order_by(Finding.severity)
                .limit(3)
                .all()
            )
            findings_summary = [
                {"title": f.title, "severity": f.severity} for f in findings
            ]
            ok = send_weekly_digest(
                to_email=scan.notify_email,
                grade=scan.grade or "F",
                score=scan.score or 0,
                findings_summary=findings_summary,
                scan_id=str(scan.id),
            )
            if ok:
                sent += 1

    except Exception as exc:
        logger.exception("Weekly digest job failed: %s", exc)
    finally:
        db.close()

    logger.info("Weekly digest job complete — sent %d emails", sent)


def start_scheduler() -> None:
    scheduler.add_job(
        _weekly_digest_job,
        trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
        id="weekly_digest",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info("Scheduler started — weekly digest runs Monday 09:00 UTC")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
