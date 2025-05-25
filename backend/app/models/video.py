"""
Video Model
Represents video files and their metadata.
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship

from ..extensions import db


class VideoStatus(Enum):
    """Video processing status."""
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class AnalysisStatus(Enum):
    """Analysis status for videos."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Video(db.Model):
    """
    Video file model with metadata and processing status.
    """
    __tablename__ = 'videos'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey('cases.id'), nullable=False, index=True)
    
    # File Information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer)  # bytes
    file_path = Column(String(500))  # path in storage
    storage_url = Column(String(500))
    
    # Video Metadata
    duration = Column(Float)  # seconds
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Float)
    format = Column(String(50))
    codec = Column(String(50))
    bitrate = Column(Integer)
    
    # Processing Status
    status = Column(ENUM(VideoStatus), default=VideoStatus.UPLOADING, nullable=False)
    analysis_status = Column(ENUM(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    
    # Upload Information
    upload_progress = Column(Float, default=0.0)  # percentage
    upload_error = Column(Text)
    
    # Processing Information
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    processing_error = Column(Text)
    
    # Additional Metadata
    extra_metadata = Column(db.JSON, default=dict)
    notes = Column(Text)
    is_evidence = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis_results = relationship('AnalysisResult', backref='video', cascade='all, delete-orphan', lazy='dynamic')
    
    @property
    def duration_formatted(self) -> str:
        """Get formatted duration string."""
        if not self.duration:
            return "Unknown"
        
        hours = int(self.duration // 3600)
        minutes = int((self.duration % 3600) // 60)
        seconds = int(self.duration % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def file_size_formatted(self) -> str:
        """Get formatted file size string."""
        if not self.file_size:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"
    
    @property
    def resolution(self) -> str:
        """Get video resolution string."""
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return "Unknown"
    
    @property
    def has_analysis(self) -> bool:
        """Check if video has any analysis results."""
        return self.analysis_results.count() > 0
    
    def get_analysis_by_type(self, analysis_type: str):
        """Get analysis result by type."""
        return self.analysis_results.filter_by(analysis_type=analysis_type).first()
    
    def to_dict(self, include_analysis: bool = False) -> dict:
        """Convert video to dictionary."""
        result = {
            'id': str(self.id),
            'case_id': str(self.case_id),
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_size_formatted': self.file_size_formatted,
            'storage_url': self.storage_url,
            'duration': self.duration,
            'duration_formatted': self.duration_formatted,
            'width': self.width,
            'height': self.height,
            'resolution': self.resolution,
            'fps': self.fps,
            'format': self.format,
            'codec': self.codec,
            'bitrate': self.bitrate,
            'status': self.status.value if self.status else None,
            'analysis_status': self.analysis_status.value if self.analysis_status else None,
            'upload_progress': self.upload_progress,
            'upload_error': self.upload_error,
            'processing_started_at': self.processing_started_at.isoformat() if self.processing_started_at else None,
            'processing_completed_at': self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            'processing_error': self.processing_error,
            'metadata': self.extra_metadata or {},
            'notes': self.notes,
            'is_evidence': self.is_evidence,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'has_analysis': self.has_analysis
        }
        
        if include_analysis:
            result['analysis_results'] = [
                analysis.to_dict() for analysis in self.analysis_results
            ]
        
        return result
    
    def __repr__(self) -> str:
        return f'<Video {self.filename}>' 