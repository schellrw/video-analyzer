"""Admin Routes"""
from flask import Blueprint, jsonify

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify({'success': True, 'message': 'Get users - to be implemented'}) 