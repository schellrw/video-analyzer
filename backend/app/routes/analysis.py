"""Analysis Routes"""
from flask import Blueprint, jsonify

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/<analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    return jsonify({'success': True, 'message': f'Get analysis {analysis_id} - to be implemented'}) 