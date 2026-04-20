from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ── Request schemas ──────────────────────────────────────────────────────────

class AWSCredentials(BaseModel):
    access_key_id:     str = Field(..., min_length=16, max_length=128)
    secret_access_key: str = Field(..., min_length=1)
    region:            str = Field(default="us-east-1")


class ScanRequest(BaseModel):
    provider:    str            = Field(default="aws")
    credentials: AWSCredentials


# ── Response schemas ─────────────────────────────────────────────────────────

class FindingOut(BaseModel):
    id:            UUID
    resource_id:   Optional[str]
    resource_type: Optional[str]
    region:        Optional[str]
    severity:      str
    title:         str
    description:   Optional[str]
    created_at:    datetime

    model_config = {"from_attributes": True}


class ScanOut(BaseModel):
    id:             UUID
    provider:       str
    status:         str
    score:          Optional[int]
    grade:          Optional[str]
    error_msg:      Optional[str]
    created_at:     datetime
    completed_at:   Optional[datetime]
    findings_count: Optional[int] = None

    model_config = {"from_attributes": True}


class ScanWithFindings(ScanOut):
    findings: List[FindingOut] = []


class ScheduleRequest(BaseModel):
    notify_weekly: bool
    notify_email:  str = Field(..., min_length=3)


class ScanListOut(BaseModel):
    scans: List[ScanOut]
    total: int
