"""
Celery Tasks
Asynchronous tasks for video processing, AI analysis, and report generation.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Import Celery app
try:
    from simple_celery import app as celery_app
except ImportError:
    # Fallback for when running from app context
    from celery import current_app as celery_app

from .extensions import db
from .models import Video, AnalysisResult, VideoStatus, AnalysisStatus, AnalysisType
from .services.video_analysis import VideoAnalysisService
from .services.report_generation import ReportGenerationService
from .services.redis_service import redis_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_video_analysis_optimized(self, video_id: str, video_path: str = None,
                                   max_frames: int = 30, strategy: str = 'uniform'):
    """
    Process video analysis using optimized AI models with cost optimization.
    
    Args:
        video_id: ID of the video record in database
        video_path: Optional path to video file (for local testing)
        max_frames: Maximum number of frames to analyze
        strategy: Frame extraction strategy ('uniform', 'motion_based', 'keyframe')
    """
    try:
        # Log progress instead of updating state
        logger.info(f"Starting optimized analysis for video {video_id}")
        
        # Get video record from database
        video = Video.query.get(video_id)
        if not video:
            raise ValueError(f"Video with ID {video_id} not found")
        
        # Determine video file path
        if video_path:
            file_path = video_path
        else:
            file_path = video.file_path
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found: {file_path}")
        
        logger.info(f"Starting optimized analysis for video {video_id}: {file_path}")
        
        # Update video status
        video.status = 'processing'
        db.session.commit()
        
        # Check for cached results
        logger.info("Checking cache...")
        
        # Initialize video analysis service with caching enabled
        analysis_service = VideoAnalysisService(use_cache=True)
        
        # Log progress
        logger.info(f"Extracting frames using {strategy} strategy...")
        
        # Perform optimized analysis
        logger.info("Analyzing frames with AI...")
        analysis_results = analysis_service.analyze_video_optimized(
            video_path=file_path,
            case_id=str(video.case_id) if video.case_id else None,
            max_frames=max_frames,
            strategy=strategy
        )
        
        # Log progress
        logger.info("Saving results...")
        
        # Save analysis results to database
        analysis_record = AnalysisResult(
            video_id=video_id,
            analysis_type=AnalysisType.VIOLATION_DETECTION,
            results=analysis_results,
            confidence=analysis_results.get('overall_confidence', 0.0),
            status='completed',
            processing_time=analysis_results.get('processing_time', 0.0),
            created_at=datetime.utcnow()
        )
        
        db.session.add(analysis_record)
        
        # Update video status
        video.status = VideoStatus.READY
        video.analysis_status = AnalysisStatus.COMPLETED
        video.processing_completed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Cache the results for future use
        redis_service.cache_analysis_result(
            video_path=file_path,
            frame_hash=f"full_analysis_{strategy}_{max_frames}",
            analysis_result=analysis_results,
            ttl=86400  # 24 hours
        )
        
        logger.info(f"Optimized analysis completed for video {video_id}")
        
        # Return enhanced summary for task result
        return {
            'status': 'completed',
            'video_id': video_id,
            'analysis_id': str(analysis_record.id),
            'frames_analyzed': analysis_results.get('total_frames_analyzed', 0),
            'processing_time': analysis_results.get('processing_time', 0.0),
            'extraction_strategy': strategy,
            'overall_confidence': analysis_results.get('overall_confidence', 0.0),
            'violations_detected': analysis_results.get('violations_detected', []),
            'concerns_found': analysis_results.get('concerns_found', False),
            'severity_assessment': analysis_results.get('severity_assessment', 'low'),
            'total_api_cost': analysis_results.get('total_api_cost_estimate', 0.0),
            'violation_timeline_count': len(analysis_results.get('violation_timeline', [])),
            'recommendations_count': len(analysis_results.get('recommendations', [])),
            'message': 'Optimized video analysis completed successfully'
        }
        
    except Exception as e:
        logger.error(f"Error processing optimized video analysis for {video_id}: {str(e)}")
        
        # Update video status to failed
        try:
            video = Video.query.get(video_id)
            if video:
                video.status = 'failed'
                db.session.commit()
        except Exception as db_error:
            logger.error(f"Failed to update video status: {str(db_error)}")
        
        # Re-raise the exception
        raise


@celery_app.task(bind=True)
def analyze_local_video_optimized(self, video_path: str, case_id: str = None,
                                max_frames: int = 30, strategy: str = 'uniform', video_id: str = None):
    """
    Analyze a local video file with optimization (for testing).
    
    Args:
        video_path: Path to the local video file
        case_id: Optional case ID for context
        max_frames: Maximum number of frames to analyze
        strategy: Frame extraction strategy
        video_id: Optional video ID to save results to database
    """
    try:
        # Log progress instead of updating state
        logger.info(f"Starting local optimized analysis for: {video_path}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        logger.info(f"Starting local optimized analysis for: {video_path}")
        
        # Check cache first
        cached_result = redis_service.get_cached_analysis_result(
            video_path=video_path,
            frame_hash=f"full_analysis_{strategy}_{max_frames}"
        )
        
        if cached_result:
            logger.info("Using cached analysis results")
            
            # If video_id provided, save cached results to database
            if video_id:
                logger.info(f"Saving cached results to database for video {video_id}")
                
                # Import Flask app for context
                from . import create_app
                app = create_app()
                
                with app.app_context():
                    video = Video.query.get(video_id)
                    if video:
                        # Create analysis record
                        analysis_record = AnalysisResult(
                            video_id=video_id,
                            analysis_type=AnalysisType.VIOLATION_DETECTION,
                            results=cached_result,
                            confidence=cached_result.get('overall_confidence', 0.0),
                            status='completed',
                            processing_time=cached_result.get('processing_time', 0.0),
                            created_at=datetime.utcnow()
                        )
                        
                        db.session.add(analysis_record)
                        
                        # Update video status
                        video.status = VideoStatus.READY
                        video.analysis_status = AnalysisStatus.COMPLETED
                        video.processing_completed_at = datetime.utcnow()
                        
                        db.session.commit()
                        logger.info(f"Cached results saved to database for video {video_id}")
                    else:
                        logger.error(f"Video not found in database: {video_id}")
            
            return {
                'status': 'completed',
                'video_path': video_path,
                'case_id': case_id,
                'video_id': video_id,
                'analysis_results': cached_result,
                'cached': True,
                'message': 'Local video analysis completed using cached results'
            }
        
        # Log progress
        logger.info(f"Extracting frames using {strategy} strategy...")
        
        # Initialize video analysis service with caching
        analysis_service = VideoAnalysisService(use_cache=True)
        
        # Perform analysis
        logger.info("Analyzing frames with AI...")
        analysis_results = analysis_service.analyze_video_optimized(
            video_path=video_path,
            case_id=case_id,
            max_frames=max_frames,
            strategy=strategy
        )
        
        # Cache the results
        redis_service.cache_analysis_result(
            video_path=video_path,
            frame_hash=f"full_analysis_{strategy}_{max_frames}",
            analysis_result=analysis_results,
            ttl=86400
        )
        
        # If video_id provided, save results to database
        if video_id:
            logger.info(f"Saving results to database for video {video_id}")
            
            # Import Flask app for context
            from . import create_app
            app = create_app()
            
            with app.app_context():
                video = Video.query.get(video_id)
                if video:
                    # Create analysis record
                    analysis_record = AnalysisResult(
                        video_id=video_id,
                        analysis_type=AnalysisType.VIOLATION_DETECTION,
                        results=analysis_results,
                        confidence=analysis_results.get('overall_confidence', 0.0),
                        status='completed',
                        processing_time=analysis_results.get('processing_time', 0.0),
                        created_at=datetime.utcnow()
                    )
                    
                    db.session.add(analysis_record)
                    
                    # Update video status
                    video.status = VideoStatus.READY
                    video.analysis_status = AnalysisStatus.COMPLETED
                    video.processing_completed_at = datetime.utcnow()
                    
                    db.session.commit()
                    logger.info(f"Results saved to database for video {video_id}")
                else:
                    logger.error(f"Video not found in database: {video_id}")
        
        logger.info(f"Local optimized analysis completed for: {video_path}")
        
        # Return full results for local testing
        return {
            'status': 'completed',
            'video_path': video_path,
            'case_id': case_id,
            'video_id': video_id,
            'analysis_results': analysis_results,
            'cached': False,
            'message': 'Local video analysis completed successfully'
        }
        
    except Exception as e:
        logger.error(f"Error in local optimized video analysis for {video_path}: {str(e)}")
        
        # Re-raise the exception
        raise


@celery_app.task(bind=True)
def generate_comprehensive_report(self, analysis_id: str, case_info: dict = None,
                                output_format: str = 'comprehensive'):
    """
    Generate a comprehensive PDF report from analysis results.
    
    Args:
        analysis_id: ID of the analysis result record
        case_info: Optional case information
        output_format: 'comprehensive' or 'summary'
    """
    try:
        logger.info(f"Starting report generation for analysis {analysis_id}")
        
        # Get analysis results from database
        analysis_record = AnalysisResult.query.get(analysis_id)
        if not analysis_record:
            raise ValueError(f"Analysis result with ID {analysis_id} not found")
        
        analysis_results = analysis_record.results
        
        logger.info(f"Generating {output_format} report for analysis {analysis_id}")
        
        # Initialize report generation service
        report_service = ReportGenerationService()
        
        logger.info("Building report content...")
        
        # Generate report based on format
        if output_format == 'comprehensive':
            report_path = report_service.generate_comprehensive_report(
                analysis_results=analysis_results,
                case_info=case_info
            )
        else:  # summary
            report_path = report_service.generate_summary_report(
                analysis_results=analysis_results
            )
        
        logger.info("Finalizing report...")
        
        # Update analysis record with report path
        analysis_record.report_path = report_path
        db.session.commit()
        
        logger.info(f"Report generated successfully: {report_path}")
        
        return {
            'status': 'completed',
            'analysis_id': analysis_id,
            'report_path': report_path,
            'report_format': output_format,
            'file_size': os.path.getsize(report_path) if os.path.exists(report_path) else 0,
            'message': f'{output_format.title()} report generated successfully'
        }
        
    except Exception as e:
        logger.error(f"Error generating report for analysis {analysis_id}: {str(e)}")
        
        # Re-raise the exception
        raise


@celery_app.task(bind=True)
def generate_local_report(self, analysis_results: dict, case_info: dict = None,
                        output_format: str = 'comprehensive'):
    """
    Generate a report from local analysis results (for testing).
    
    Args:
        analysis_results: Analysis results dictionary
        case_info: Optional case information
        output_format: 'comprehensive' or 'summary'
    """
    try:
        logger.info(f"Starting local report generation with {output_format} format")
        
        logger.info(f"Generating {output_format} report from local analysis results")
        
        # Initialize report generation service
        report_service = ReportGenerationService()
        
        logger.info("Building report content...")
        
        # Generate report based on format
        if output_format == 'comprehensive':
            report_path = report_service.generate_comprehensive_report(
                analysis_results=analysis_results,
                case_info=case_info
            )
        else:  # summary
            report_path = report_service.generate_summary_report(
                analysis_results=analysis_results
            )
        
        logger.info(f"Local report generated successfully: {report_path}")
        
        return {
            'status': 'completed',
            'report_path': report_path,
            'report_format': output_format,
            'file_size': os.path.getsize(report_path) if os.path.exists(report_path) else 0,
            'message': f'{output_format.title()} report generated successfully'
        }
        
    except Exception as e:
        logger.error(f"Error generating local report: {str(e)}")
        
        # Re-raise the exception
        raise


@celery_app.task
def cleanup_old_files():
    """Clean up old temporary files and analysis results."""
    try:
        logger.info("Starting cleanup task")
        
        # Clean up old cache entries (simplified)
        cache_cleaned = 0  # Simplified for now since cleanup method was removed
        
        # Clean up old report files (older than 7 days)
        reports_dir = "reports"
        if os.path.exists(reports_dir):
            import time
            current_time = time.time()
            max_age = 7 * 24 * 3600  # 7 days in seconds
            
            files_cleaned = 0
            for filename in os.listdir(reports_dir):
                file_path = os.path.join(reports_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age:
                        try:
                            os.remove(file_path)
                            files_cleaned += 1
                        except Exception as e:
                            logger.warning(f"Failed to delete {file_path}: {str(e)}")
            
            logger.info(f"Cleaned up {files_cleaned} old report files")
        
        # Get Redis usage stats
        redis_stats = redis_service.get_usage_stats()
        
        return {
            'status': 'completed',
            'cache_entries_cleaned': cache_cleaned,
            'report_files_cleaned': files_cleaned if 'files_cleaned' in locals() else 0,
            'redis_stats': redis_stats,
            'message': 'Cleanup completed successfully'
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e),
            'message': 'Cleanup task failed'
        }


@celery_app.task
def optimize_redis_usage():
    """Optimize Redis usage by switching between primary and fallback."""
    try:
        logger.info("Running Redis optimization task")
        
        # Get current usage stats
        stats_before = redis_service.get_usage_stats()
        
        # Try to switch back to primary if using fallback
        if stats_before['using_fallback'] and stats_before['primary_available']:
            if redis_service.try_primary():
                logger.info("Successfully switched back to primary Redis")
        
        # Get updated stats
        stats_after = redis_service.get_usage_stats()
        
        return {
            'status': 'completed',
            'stats_before': stats_before,
            'stats_after': stats_after,
            'switched_to_primary': not stats_after['using_fallback'] and stats_before['using_fallback'],
            'message': 'Redis optimization completed'
        }
        
    except Exception as e:
        logger.error(f"Error in Redis optimization task: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e),
            'message': 'Redis optimization failed'
        }


# Legacy compatibility tasks
@celery_app.task(bind=True)
def process_video_analysis(self, video_id: str, video_path: str = None):
    """Legacy task - redirects to optimized version."""
    return process_video_analysis_optimized.apply_async(
        args=[video_id, video_path],
        kwargs={'max_frames': 30, 'strategy': 'uniform'}
    )


@celery_app.task(bind=True)
def analyze_local_video(self, video_path: str, case_id: str = None):
    """Legacy task - redirects to optimized version."""
    return analyze_local_video_optimized.apply_async(
        args=[video_path, case_id],
        kwargs={'max_frames': 30, 'strategy': 'uniform'}
    )


@celery_app.task
def generate_report(case_id: str, report_id: str):
    """Legacy task for report generation."""
    logger.info(f"Legacy report generation for case {case_id}, report {report_id}")
    # This could be implemented to work with the new system
    return {
        'status': 'completed',
        'message': 'Legacy report generation - use generate_comprehensive_report instead'
    } 