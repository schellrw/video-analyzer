"""Reports Routes"""
from flask import Blueprint, jsonify

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/<report_id>', methods=['GET'])
def get_report(report_id):
    return jsonify({'success': True, 'message': f'Get report {report_id} - to be implemented'}) 