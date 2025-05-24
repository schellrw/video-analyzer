"""Error Handlers"""
from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'The request could not be understood by the server.'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication is required.'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'The requested resource was not found.'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An internal server error occurred.'
        }), 500 