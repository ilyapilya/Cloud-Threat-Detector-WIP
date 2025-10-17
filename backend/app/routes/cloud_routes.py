from fastapi import APIRouter
from scanner.aws_scanner import get_ec2_threat_report

router = APIRouter()

@router.get("/aws/threat-report")
def get_threat_report():
    return get_ec2_threat_report()

