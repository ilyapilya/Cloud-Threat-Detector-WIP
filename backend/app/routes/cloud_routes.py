from fastapi import APIRouter, HTTPException
from scanner.aws_scanner import get_ec2_threat_report

router = APIRouter(prefix="/api/v1")

@router.get("/aws/threat-report")
def get_threat_report():
    try:
        return get_ec2_threat_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



