"""Videos Routes"""
from flask import Blueprint, jsonify

videos_bp = Blueprint('videos', __name__)

@videos_bp.route('/<video_id>', methods=['GET'])
def get_video(video_id):
    return jsonify({'success': True, 'message': f'Get video {video_id} - to be implemented'})

@videos_bp.route('/<video_id>/analyze', methods=['POST'])
def analyze_video(video_id):
    return jsonify({'success': True, 'message': f'Analyze video {video_id} - to be implemented'}) 