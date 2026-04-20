"""
Scan API Routes
POST /api/v1/scan           — validate credentials, create scan, start background job
GET  /api/v1/scan/{id}      — poll scan status + score
GET  /api/v1/scan/{id}/findings — paginated findings list
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..deps import get_db, get_optional_user_id
from ..models import Scan, Finding
from ..schemas import ScanRequest, ScanOut, ScanWithFindings, FindingOut, ScanListOut
from ..scanner.aws_checks import validate_credentials, run_aws_checks, calculate_score

router = APIRouter(prefix="/api/v1")


# ── Background task ───────────────────────────────────────────────────────────

def _execute_scan(scan_id: str, creds: dict, region: str) -> None:
    """
    Runs in a thread (FastAPI BackgroundTasks).
    Creates its own DB session — the request session is already closed.
    """
    db = SessionLocal()
    scan = None
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return

        scan.status = "running"
        db.commit()

        findings = run_aws_checks(creds, region)
        score, grade = calculate_score(findings)

        for f in findings:
            db.add(Finding(scan_id=scan_id, **f))

        scan.status       = "completed"
        scan.score        = score
        scan.grade        = grade
        scan.completed_at = datetime.utcnow()
        db.commit()

    except Exception as exc:
        if scan:
            scan.status    = "failed"
            scan.error_msg = str(exc)
            db.commit()
    finally:
        db.close()


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/scans", response_model=ScanListOut)
def list_scans(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_optional_user_id),
):
    """Return all scans for the authenticated user, newest first."""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")

    scans = (
        db.query(Scan)
        .filter(Scan.user_id == user_id)
        .order_by(Scan.created_at.desc())
        .all()
    )

    scan_outs = []
    for scan in scans:
        findings_count = (
            db.query(Finding).filter(Finding.scan_id == str(scan.id)).count()
            if scan.status == "completed" else None
        )
        out = ScanOut.model_validate(scan)
        out.findings_count = findings_count
        scan_outs.append(out)

    return ScanListOut(scans=scan_outs, total=len(scan_outs))


@router.post("/scan", response_model=ScanOut, status_code=202)
def create_scan(
    body: ScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_optional_user_id),
):
    """
    Validate AWS credentials, create a scan record, kick off async checks.
    Returns immediately with scan_id — poll GET /scan/{id} for results.
    """
    if body.provider != "aws":
        raise HTTPException(status_code=400, detail="Only 'aws' provider is supported right now.")

    # Fast credential check before queuing work
    valid, arn_or_err = validate_credentials(body.credentials.model_dump())
    if not valid:
        raise HTTPException(
            status_code=400,
            detail=f"AWS credential validation failed: {arn_or_err}",
        )

    scan = Scan(provider=body.provider, user_id=user_id)
    db.add(scan)
    db.commit()
    db.refresh(scan)

    background_tasks.add_task(
        _execute_scan,
        str(scan.id),
        body.credentials.model_dump(),
        body.credentials.region,
    )

    return scan


@router.get("/scan/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: UUID, db: Session = Depends(get_db)):
    """Poll scan status. Includes findings_count once completed."""
    scan = db.query(Scan).filter(Scan.id == str(scan_id)).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")

    findings_count = (
        db.query(Finding).filter(Finding.scan_id == str(scan_id)).count()
        if scan.status == "completed"
        else None
    )

    result = ScanOut.model_validate(scan)
    result.findings_count = findings_count
    return result


@router.get("/scan/{scan_id}/findings", response_model=ScanWithFindings)
def get_scan_findings(
    scan_id: UUID,
    severity: str = None,
    db: Session = Depends(get_db),
):
    """
    Return scan + its findings. Optionally filter by severity=critical|high|medium|low.
    Free tier enforcement happens on the frontend (blur findings > 5).
    """
    scan = db.query(Scan).filter(Scan.id == str(scan_id)).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    if scan.status != "completed":
        raise HTTPException(status_code=409, detail=f"Scan is still {scan.status}.")

    query = db.query(Finding).filter(Finding.scan_id == str(scan_id))

    if severity:
        allowed = {"critical", "high", "medium", "low", "info"}
        if severity not in allowed:
            raise HTTPException(status_code=400, detail=f"severity must be one of {allowed}")
        query = query.filter(Finding.severity == severity)

    # Sort: critical first
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    findings = sorted(query.all(), key=lambda f: severity_order.get(f.severity, 5))

    result = ScanWithFindings.model_validate(scan)
    result.findings_count = len(findings)
    result.findings = [FindingOut.model_validate(f) for f in findings]
    return result
