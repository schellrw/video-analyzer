"""
Analysis Routes
API endpoints for video analysis, AI processing, and report generation.
"""

import os
import logging
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from celery.result import AsyncResult
from ..tasks import (
    analyze_local_video_optimized, process_video_analysis_optimized,
    generate_comprehensive_report, generate_local_report,
    analyze_local_video, process_video_analysis  # Legacy tasks
)
from ..extensions import db
from ..models import Video, AnalysisResult
from ..services.redis_service import redis_service

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')


@analysis_bp.route('/test-local-optimized', methods=['POST'])
def test_local_analysis_optimized():
    """
    Test optimized video analysis with a local file (for development/testing).
    No authentication required for testing.
    """
    try:
        data = request.get_json()
        
        if not data or 'video_path' not in data:
            return jsonify({'error': 'video_path is required'}), 400
        
        video_path = data['video_path']
        case_id = data.get('case_id', 'test-case')
        max_frames = data.get('max_frames', 30)
        strategy = data.get('strategy', 'uniform')
        video_id = data.get('video_id')  # Extract video_id for database saving
        
        # Validate strategy
        valid_strategies = ['uniform', 'motion_based', 'keyframe']
        if strategy not in valid_strategies:
            return jsonify({
                'error': f'Invalid strategy. Must be one of: {valid_strategies}'
            }), 400
        
        # Validate max_frames
        if not isinstance(max_frames, int) or max_frames < 1 or max_frames > 100:
            return jsonify({
                'error': 'max_frames must be an integer between 1 and 100'
            }), 400
        
        # Check if file exists
        if not os.path.exists(video_path):
            return jsonify({'error': f'Video file not found: {video_path}'}), 404
        
        # Check if file is a video (basic check)
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
        if not any(video_path.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({'error': 'Invalid video file format'}), 400
        
        logger.info(f"Starting optimized local video analysis for: {video_path}")
        
        # Start async analysis task
        task = analyze_local_video_optimized.delay(
            video_path, case_id, max_frames, strategy, video_id
        )
        
        return jsonify({
            'task_id': task.id,
            'status': 'started',
            'video_path': video_path,
            'max_frames': max_frames,
            'strategy': strategy,
            'message': 'Optimized video analysis started successfully'
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting optimized local video analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/video/<video_id>/optimized', methods=['POST'])
@jwt_required()
def analyze_video_optimized(video_id):
    """
    Start optimized analysis of an uploaded video (production endpoint).
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Get video record and verify access
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # TODO: Add proper authorization check
        
        if video.status == 'processing':
            return jsonify({'error': 'Video is already being processed'}), 400
        
        if video.status == 'completed':
            return jsonify({'error': 'Video has already been analyzed'}), 400
        
        # Get analysis parameters
        max_frames = data.get('max_frames', 30)
        strategy = data.get('strategy', 'uniform')
        
        # Validate parameters
        valid_strategies = ['uniform', 'motion_based', 'keyframe']
        if strategy not in valid_strategies:
            return jsonify({
                'error': f'Invalid strategy. Must be one of: {valid_strategies}'
            }), 400
        
        if not isinstance(max_frames, int) or max_frames < 1 or max_frames > 100:
            return jsonify({
                'error': 'max_frames must be an integer between 1 and 100'
            }), 400
        
        logger.info(f"Starting optimized video analysis for video {video_id}")
        
        # Start async analysis task
        task = process_video_analysis_optimized.delay(
            video_id, None, max_frames, strategy
        )
        
        # Update video with task ID
        video.task_id = task.id
        video.status = 'queued'
        db.session.commit()
        
        return jsonify({
            'task_id': task.id,
            'video_id': video_id,
            'max_frames': max_frames,
            'strategy': strategy,
            'status': 'started',
            'message': 'Optimized video analysis started successfully'
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting optimized video analysis for {video_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/generate-report', methods=['POST'])
@jwt_required()
def generate_analysis_report():
    """
    Generate a comprehensive PDF report from analysis results.
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'analysis_id' not in data:
            return jsonify({'error': 'analysis_id is required'}), 400
        
        analysis_id = data['analysis_id']
        case_info = data.get('case_info', {})
        output_format = data.get('output_format', 'comprehensive')
        
        # Validate output format
        valid_formats = ['comprehensive', 'summary']
        if output_format not in valid_formats:
            return jsonify({
                'error': f'Invalid output_format. Must be one of: {valid_formats}'
            }), 400
        
        # Check if analysis exists
        analysis_record = AnalysisResult.query.get(analysis_id)
        if not analysis_record:
            return jsonify({'error': 'Analysis result not found'}), 404
        
        # TODO: Add proper authorization check
        
        logger.info(f"Starting report generation for analysis {analysis_id}")
        
        # Start async report generation task
        task = generate_comprehensive_report.delay(
            analysis_id, case_info, output_format
        )
        
        return jsonify({
            'task_id': task.id,
            'analysis_id': analysis_id,
            'output_format': output_format,
            'status': 'started',
            'message': 'Report generation started successfully'
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting report generation: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/generate-local-report', methods=['POST'])
def generate_local_analysis_report():
    """
    Generate a report from local analysis results (for testing).
    No authentication required for testing.
    """
    try:
        data = request.get_json()
        
        if not data or 'analysis_results' not in data:
            return jsonify({'error': 'analysis_results is required'}), 400
        
        analysis_results = data['analysis_results']
        case_info = data.get('case_info', {})
        output_format = data.get('output_format', 'comprehensive')
        
        # Validate output format
        valid_formats = ['comprehensive', 'summary']
        if output_format not in valid_formats:
            return jsonify({
                'error': f'Invalid output_format. Must be one of: {valid_formats}'
            }), 400
        
        logger.info("Starting local report generation")
        
        # Start async report generation task
        task = generate_local_report.delay(
            analysis_results, case_info, output_format
        )
        
        return jsonify({
            'task_id': task.id,
            'output_format': output_format,
            'status': 'started',
            'message': 'Local report generation started successfully'
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting local report generation: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/download-report/<task_id>', methods=['GET'])
def download_report(task_id):
    """
    Download a generated report by task ID.
    """
    try:
        task = AsyncResult(task_id)
        
        if task.state != 'SUCCESS':
            return jsonify({
                'error': 'Report is not ready yet or generation failed',
                'task_state': task.state
            }), 400
        
        result = task.result
        report_path = result.get('report_path')
        
        if not report_path or not os.path.exists(report_path):
            return jsonify({'error': 'Report file not found'}), 404
        
        # Send file for download
        return send_file(
            report_path,
            as_attachment=True,
            download_name=os.path.basename(report_path),
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error downloading report for task {task_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/redis-stats', methods=['GET'])
def get_redis_stats():
    """
    Get Redis usage statistics (for monitoring).
    """
    try:
        stats = redis_service.get_usage_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting Redis stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/redis/force-fallback', methods=['POST'])
def force_redis_fallback():
    """
    Force switch to fallback Redis (for testing).
    """
    try:
        success = redis_service.force_fallback()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Switched to fallback Redis',
                'stats': redis_service.get_usage_stats()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Fallback Redis not available'
            }), 400
        
    except Exception as e:
        logger.error(f"Error forcing Redis fallback: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/redis/try-primary', methods=['POST'])
def try_redis_primary():
    """
    Try to switch back to primary Redis.
    """
    try:
        success = redis_service.try_primary()
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'message': 'Switched to primary Redis' if success else 'Primary Redis not available',
            'stats': redis_service.get_usage_stats()
        })
        
    except Exception as e:
        logger.error(f"Error trying primary Redis: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Legacy endpoints (for backward compatibility)
@analysis_bp.route('/test-local', methods=['POST'])
def test_local_analysis():
    """
    Test video analysis with a local file (legacy endpoint).
    """
    try:
        data = request.get_json()
        
        if not data or 'video_path' not in data:
            return jsonify({'error': 'video_path is required'}), 400
        
        video_path = data['video_path']
        case_id = data.get('case_id', 'test-case')
        
        # Check if file exists
        if not os.path.exists(video_path):
            return jsonify({'error': f'Video file not found: {video_path}'}), 404
        
        # Check if file is a video (basic check)
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
        if not any(video_path.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({'error': 'Invalid video file format'}), 400
        
        logger.info(f"Starting legacy local video analysis for: {video_path}")
        
        # Start async analysis task (legacy)
        task = analyze_local_video.delay(video_path, case_id)
        
        return jsonify({
            'task_id': task.id,
            'status': 'started',
            'video_path': video_path,
            'message': 'Video analysis started successfully (legacy)'
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting legacy local video analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    Get the status of an analysis task.
    """
    try:
        task = AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': 'Task is waiting to be processed'
            }
        elif task.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': task.info.get('status', 'Processing...'),
                'progress': task.info
            }
        elif task.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': 'completed',
                'result': task.result
            }
        elif task.state == 'FAILURE':
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': 'failed',
                'error': str(task.info)
            }
        else:
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': 'Unknown state'
            }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/video/<video_id>', methods=['POST'])
@jwt_required()
def analyze_video(video_id):
    """
    Start analysis of an uploaded video (legacy production endpoint).
    """
    try:
        user_id = get_jwt_identity()
        
        # Get video record and verify access
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # TODO: Add proper authorization check
        
        if video.status == 'processing':
            return jsonify({'error': 'Video is already being processed'}), 400
        
        if video.status == 'completed':
            return jsonify({'error': 'Video has already been analyzed'}), 400
        
        logger.info(f"Starting legacy video analysis for video {video_id}")
        
        # Start async analysis task (legacy)
        task = process_video_analysis.delay(video_id)
        
        # Update video with task ID
        video.task_id = task.id
        video.status = 'queued'
        db.session.commit()
        
        return jsonify({
            'task_id': task.id,
            'video_id': video_id,
            'status': 'started',
            'message': 'Video analysis started successfully (legacy)'
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting legacy video analysis for {video_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/video/<video_id>/results', methods=['GET'])
@jwt_required()
def get_analysis_results(video_id):
    """
    Get analysis results for a video.
    """
    try:
        user_id = get_jwt_identity()
        
        # Get video record and verify access
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # TODO: Add proper authorization check
        
        # Get analysis results
        analysis_results = AnalysisResult.query.filter_by(video_id=video_id).all()
        
        if not analysis_results:
            return jsonify({
                'video_id': video_id,
                'status': video.status,
                'message': 'No analysis results found'
            }), 404
        
        # Format results
        results = []
        for result in analysis_results:
            results.append({
                'id': str(result.id),
                'analysis_type': result.analysis_type,
                'confidence': result.confidence,
                'status': result.status,
                'processing_time': result.processing_time,
                'created_at': result.created_at.isoformat() if result.created_at else None,
                'results': result.results
            })
        
        return jsonify({
            'video_id': video_id,
            'video_status': video.status,
            'analysis_results': results
        })
        
    except Exception as e:
        logger.error(f"Error getting analysis results for {video_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/list-local-videos', methods=['GET'])
def list_local_videos():
    """
    List available local video files for testing.
    """
    try:
        # Define test video directories
        test_dirs = [
            'test_videos',
            'uploads',
            os.path.expanduser('~/Videos'),
            '/tmp/test_videos'
        ]
        
        videos = []
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
        
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                for filename in os.listdir(test_dir):
                    if any(filename.lower().endswith(ext) for ext in video_extensions):
                        file_path = os.path.join(test_dir, filename)
                        if os.path.isfile(file_path):
                            file_stats = os.stat(file_path)
                            videos.append({
                                'filename': filename,
                                'path': file_path,
                                'size': file_stats.st_size,
                                'modified': file_stats.st_mtime
                            })
        
        return jsonify({
            'videos': videos,
            'count': len(videos)
        })
        
    except Exception as e:
        logger.error(f"Error listing local videos: {str(e)}")
        return jsonify({'error': str(e)}), 500 