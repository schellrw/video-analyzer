"""
Custom authentication decorators for Supabase JWT tokens.
"""

from functools import wraps
from flask import request, jsonify, g
from ..services.supabase_auth import supabase_auth


def supabase_jwt_required(f):
    """
    Decorator to require valid Supabase JWT token.
    Sets g.current_user_id with the authenticated user's ID.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'success': False,
                'message': 'Authorization header required'
            }), 401
        
        # Extract token from "Bearer <token>" format
        try:
            token_type, token = auth_header.split(' ', 1)
            if token_type.lower() != 'bearer':
                return jsonify({
                    'success': False,
                    'message': 'Invalid authorization header format. Use "Bearer <token>"'
                }), 401
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid authorization header format. Use "Bearer <token>"'
            }), 401
        
        # Verify token with Supabase
        user_data = supabase_auth.verify_jwt_token(token)
        if not user_data:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401
        
        # Set current user ID in Flask's g object
        g.current_user_id = user_data['user_id']
        g.current_user_email = user_data['email']
        g.current_user_data = user_data
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user_id():
    """
    Get the current authenticated user's ID.
    Must be called within a route decorated with @supabase_jwt_required.
    """
    return getattr(g, 'current_user_id', None)


def get_current_user_email():
    """
    Get the current authenticated user's email.
    Must be called within a route decorated with @supabase_jwt_required.
    """
    return getattr(g, 'current_user_email', None)


def get_current_user_data():
    """
    Get the current authenticated user's full data.
    Must be called within a route decorated with @supabase_jwt_required.
    """
    return getattr(g, 'current_user_data', None) 