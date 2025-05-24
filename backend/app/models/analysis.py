"""Analysis Results Model"""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM
from ..extensions import db

class AnalysisType(Enum):
    TRANSCRIPTION = "transcription"
    VIOLATION_DETECTION = "violation_detection"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    OBJECT_DETECTION = "object_detection"

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey('videos.id'), nullable=False)
    analysis_type = Column(ENUM(AnalysisType), nullable=False)
    results = Column(db.JSON, nullable=False)
    confidence = Column(Float)
    status = Column(String(50), default='completed')
    processing_time = Column(Float)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'video_id': str(self.video_id),
            'analysis_type': self.analysis_type.value,
            'results': self.results,
            'confidence': self.confidence,
            'status': self.status,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat()
        } 