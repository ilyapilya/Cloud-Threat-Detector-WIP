import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .database import Base


class Scan(Base):
    __tablename__ = "scans"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), nullable=True)   # populated after auth (Day 4)
    provider     = Column(String(10), nullable=False)
    status       = Column(String(20), nullable=False, default="pending")
    score        = Column(Integer, nullable=True)
    grade        = Column(String(1), nullable=True)
    error_msg    = Column(Text, nullable=True)
    created_at   = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class Finding(Base):
    __tablename__ = "findings"

    id                 = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id            = Column(UUID(as_uuid=True), nullable=False)
    resource_id        = Column(String(255), nullable=True)
    resource_type      = Column(String(100), nullable=True)
    region             = Column(String(50), nullable=True)
    severity           = Column(String(20), nullable=False)
    title              = Column(String(255), nullable=False)
    description        = Column(Text, nullable=True)
    remediation_cached = Column(JSONB, nullable=True)
    created_at         = Column(DateTime, nullable=False, default=datetime.utcnow)
