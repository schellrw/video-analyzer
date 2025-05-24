"""Report Model"""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, ENUM
from ..extensions import db

class ReportStatus(Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class ReportType(Enum):
    STANDARD = "standard"
    DETAILED = "detailed"
    SUMMARY = "summary"

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey('cases.id'), nullable=False)
    title = Column(String(200), nullable=False)
    report_type = Column(ENUM(ReportType), default=ReportType.STANDARD)
    status = Column(ENUM(ReportStatus), default=ReportStatus.PENDING)
    content = Column(Text)
    file_path = Column(String(500))
    include_evidence = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'case_id': str(self.case_id),
            'title': self.title,
            'report_type': self.report_type.value,
            'status': self.status.value,
            'include_evidence': self.include_evidence,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        } 