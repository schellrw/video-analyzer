"""Health Check Routes"""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'message': 'Video Analyzer API is running',
        'status': 'healthy'
    }) 