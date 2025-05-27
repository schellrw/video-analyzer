"""
Analysis Routes
API endpoints for video analysis and AI processing.
"""

import os
import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from celery.result import AsyncResult
from ..tasks import analyze_local_video, process_video_analysis
from ..extensions import db
from ..models import Video, AnalysisResult

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')


@analysis_bp.route('/test-local', methods=['POST'])
def test_local_analysis():
    """
    Test video analysis with a local file (for development/testing).
    No authentication required for testing.
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
        
        logger.info(f"Starting local video analysis for: {video_path}")
        
        # Start async analysis task
        task = analyze_local_video.delay(video_path, case_id)
        
        return jsonify({
            'task_id': task.id,
            'status': 'started',
            'video_path': video_path,
            'message': 'Video analysis started successfully'
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting local video analysis: {str(e)}")
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
    Start analysis of an uploaded video (production endpoint).
    """
    try:
        user_id = get_jwt_identity()
        
        # Get video record and verify access
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # TODO: Add proper authorization check
        # For now, just check if video exists
        
        if video.status == 'processing':
            return jsonify({'error': 'Video is already being processed'}), 400
        
        if video.status == 'completed':
            return jsonify({'error': 'Video has already been analyzed'}), 400
        
        logger.info(f"Starting video analysis for video {video_id}")
        
        # Start async analysis task
        task = process_video_analysis.delay(video_id)
        
        # Update video with task ID
        video.task_id = task.id
        video.status = 'queued'
        db.session.commit()
        
        return jsonify({
            'task_id': task.id,
            'video_id': video_id,
            'status': 'started',
            'message': 'Video analysis started successfully'
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting video analysis for {video_id}: {str(e)}")
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
    List available video files in the uploads directory (for testing).
    """
    try:
        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        
        if not os.path.exists(uploads_dir):
            return jsonify({
                'uploads_dir': uploads_dir,
                'videos': [],
                'message': 'Uploads directory does not exist'
            })
        
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
        videos = []
        
        for filename in os.listdir(uploads_dir):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                file_path = os.path.join(uploads_dir, filename)
                file_size = os.path.getsize(file_path)
                videos.append({
                    'filename': filename,
                    'path': file_path,
                    'size_mb': round(file_size / (1024 * 1024), 2)
                })
        
        return jsonify({
            'uploads_dir': uploads_dir,
            'videos': videos,
            'count': len(videos)
        })
        
    except Exception as e:
        logger.error(f"Error listing local videos: {str(e)}")
        return jsonify({'error': str(e)}), 500 