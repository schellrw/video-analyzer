"""
Case Model
Represents legal cases and associated metadata.
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY, ENUM
from sqlalchemy.orm import relationship

from ..extensions import db


class CaseStatus(Enum):
    """Case status enumeration."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CLOSED = "closed"


class CasePriority(Enum):
    """Case priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Case(db.Model):
    """
    Legal case model for organizing video evidence.
    """
    __tablename__ = 'cases'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Case Information
    name = Column(String(200), nullable=False)
    description = Column(Text)
    case_number = Column(String(100), index=True)  # Optional user-provided case number
    
    # Incident Details
    incident_date = Column(DateTime)
    incident_location = Column(String(500))
    incident_description = Column(Text)
    
    # Classification
    status = Column(ENUM(CaseStatus), default=CaseStatus.PENDING, nullable=False)
    priority = Column(ENUM(CasePriority), default=CasePriority.MEDIUM, nullable=False)
    tags = Column(ARRAY(String), default=list)
    
    # Legal Information
    court_jurisdiction = Column(String(200))
    opposing_party = Column(String(200))
    legal_theory = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)
    
    # Relationships
    videos = relationship('Video', backref='case', cascade='all, delete-orphan', lazy='dynamic')
    reports = relationship('Report', backref='case', cascade='all, delete-orphan', lazy='dynamic')
    
    @property
    def video_count(self) -> int:
        """Get total number of videos in this case."""
        return self.videos.count()
    
    @property
    def analysis_progress(self) -> dict:
        """Get analysis progress statistics."""
        total_videos = self.video_count
        if total_videos == 0:
            return {'total': 0, 'completed': 0, 'percentage': 0}
        
        completed_analyses = sum(1 for video in self.videos if video.analysis_status == 'completed')
        percentage = (completed_analyses / total_videos) * 100
        
        return {
            'total': total_videos,
            'completed': completed_analyses,
            'percentage': round(percentage, 2)
        }
    

    
    def to_dict(self, include_videos: bool = False) -> dict:
        """Convert case to dictionary."""
        result = {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'name': self.name,
            'description': self.description,
            'case_number': self.case_number,
            'incident_date': self.incident_date.isoformat() if self.incident_date else None,
            'incident_location': self.incident_location,
            'incident_description': self.incident_description,
            'status': self.status.value if self.status else None,
            'priority': self.priority.value if self.priority else None,
            'tags': self.tags or [],
            'court_jurisdiction': self.court_jurisdiction,
            'opposing_party': self.opposing_party,
            'legal_theory': self.legal_theory,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'video_count': self.video_count,
            'analysis_progress': self.analysis_progress
        }
        
        if include_videos:
            result['videos'] = [video.to_dict() for video in self.videos]
        
        return result
    
    def __repr__(self) -> str:
        return f'<Case {self.case_number}: {self.name}>' 