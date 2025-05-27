"""
Celery Tasks
Asynchronous tasks for video processing and AI analysis.
"""

import os
import logging
from datetime import datetime
from celery import current_app as celery_app
from .extensions import db
from .models import Video, AnalysisResult
from .services.video_analysis import VideoAnalysisService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_video_analysis(self, video_id: str, video_path: str = None):
    """
    Process video analysis using AI models.
    
    Args:
        video_id: ID of the video record in database
        video_path: Optional path to video file (for local testing)
    """
    try:
        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Starting analysis...'})
        
        # Get video record from database
        video = Video.query.get(video_id)
        if not video:
            raise ValueError(f"Video with ID {video_id} not found")
        
        # Determine video file path
        if video_path:
            # Use provided path (for local testing)
            file_path = video_path
        else:
            # Use path from video record (for production)
            file_path = video.file_path
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found: {file_path}")
        
        logger.info(f"Starting analysis for video {video_id}: {file_path}")
        
        # Update video status
        video.status = 'processing'
        db.session.commit()
        
        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Extracting frames...'})
        
        # Initialize video analysis service
        analysis_service = VideoAnalysisService()
        
        # Perform analysis
        self.update_state(state='PROGRESS', meta={'status': 'Analyzing frames with AI...'})
        analysis_results = analysis_service.analyze_video(
            video_path=file_path,
            case_id=str(video.case_id) if video.case_id else None
        )
        
        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Saving results...'})
        
        # Save analysis results to database
        analysis_record = AnalysisResult(
            video_id=video_id,
            analysis_type='visual_analysis',
            results=analysis_results,
            confidence=analysis_results.get('overall_confidence', 0.0),
            status='completed',
            processing_time=None,  # Could calculate this
            created_at=datetime.utcnow()
        )
        
        db.session.add(analysis_record)
        
        # Update video status
        video.status = 'completed'
        video.analysis_completed_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Analysis completed for video {video_id}")
        
        # Return summary for task result
        return {
            'status': 'completed',
            'video_id': video_id,
            'analysis_id': str(analysis_record.id),
            'frames_analyzed': analysis_results.get('total_frames_analyzed', 0),
            'overall_confidence': analysis_results.get('overall_confidence', 0.0),
            'violations_detected': analysis_results.get('violations_detected', []),
            'concerns_found': analysis_results.get('concerns_found', False),
            'message': 'Video analysis completed successfully'
        }
        
    except Exception as e:
        logger.error(f"Error processing video analysis for {video_id}: {str(e)}")
        
        # Update video status to failed
        try:
            video = Video.query.get(video_id)
            if video:
                video.status = 'failed'
                db.session.commit()
        except Exception as db_error:
            logger.error(f"Failed to update video status: {str(db_error)}")
        
        # Update task state
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'failed',
                'error': str(e),
                'video_id': video_id
            }
        )
        
        raise


@celery_app.task(bind=True)
def analyze_local_video(self, video_path: str, case_id: str = None):
    """
    Analyze a local video file without database integration (for testing).
    
    Args:
        video_path: Path to the local video file
        case_id: Optional case ID for context
    """
    try:
        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Starting local video analysis...'})
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        logger.info(f"Starting local analysis for: {video_path}")
        
        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Extracting frames...'})
        
        # Initialize video analysis service
        analysis_service = VideoAnalysisService()
        
        # Perform analysis
        self.update_state(state='PROGRESS', meta={'status': 'Analyzing frames with AI...'})
        analysis_results = analysis_service.analyze_video(
            video_path=video_path,
            case_id=case_id
        )
        
        logger.info(f"Local analysis completed for: {video_path}")
        
        # Return full results for local testing
        return {
            'status': 'completed',
            'video_path': video_path,
            'case_id': case_id,
            'analysis_results': analysis_results,
            'message': 'Local video analysis completed successfully'
        }
        
    except Exception as e:
        logger.error(f"Error in local video analysis for {video_path}: {str(e)}")
        
        # Update task state
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'failed',
                'error': str(e),
                'video_path': video_path
            }
        )
        
        raise


@celery_app.task
def generate_report(case_id: str, report_id: str):
    """Generate legal report for a case."""
    # This will be implemented with report generation logic
    logger.info(f"Generating report for case {case_id}, report {report_id}")
    # TODO: Implement report generation
    pass


@celery_app.task
def cleanup_old_files():
    """Clean up old temporary files and analysis results."""
    # This will be implemented for maintenance
    logger.info("Running cleanup task")
    # TODO: Implement cleanup logic
    pass 