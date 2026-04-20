"""
Remediation Routes
POST /api/v1/findings/{id}/remediate  — get AI fix for a finding (cached)
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps import get_db, get_optional_user_id
from ..models import Finding
from ..services.remediation import get_remediation

router = APIRouter(prefix="/api/v1")


@router.post("/findings/{finding_id}/remediate")
def remediate_finding(
    finding_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_optional_user_id),
):
    """
    Return AI-generated remediation for a finding.
    Result is cached — subsequent calls return instantly from DB.
    Requires authentication (Pro gate is enforced on the frontend by index;
    backend doesn't need to check plan here since the data is non-sensitive).
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")

    finding = db.query(Finding).filter(Finding.id == str(finding_id)).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found.")

    try:
        result = get_remediation(finding, db)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Remediation failed: {e}")

    return result
