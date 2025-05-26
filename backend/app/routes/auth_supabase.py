"""
Supabase Authentication Routes
Handles authentication using Supabase Auth instead of custom user management.
"""

from flask import Blueprint, jsonify, request
from ..extensions import db
from ..models.profile import Profile, UserRole
from ..services.supabase_auth import supabase_auth
from ..utils.auth_decorators import supabase_jwt_required, get_current_user_id

auth_supabase_bp = Blueprint('auth_supabase', __name__)


@auth_supabase_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """
    Verify a Supabase JWT token and return user data with profile.
    This replaces the traditional login endpoint.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        token = data.get('access_token')
        if not token:
            return jsonify({
                'success': False,
                'message': 'Access token required'
            }), 400
        
        # Verify token with Supabase
        user_data = supabase_auth.verify_jwt_token(token)
        if not user_data:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401
        
        user_id = user_data['user_id']
        
        # Get user profile from our database
        profile = Profile.query.filter_by(id=user_id).first()
        
        if not profile:
            return jsonify({
                'success': False,
                'message': 'User profile not found. Please complete registration.'
            }), 404
        
        # Return user data
        response_data = {
            'id': user_id,
            'email': user_data['email'],
            'firstName': profile.first_name,
            'lastName': profile.last_name,
            'organization': profile.organization,
            'role': profile.role.value,
            'profile': profile.to_dict()
        }
        
        return jsonify({
            'success': True,
            'data': {
                'user': response_data,
                'access_token': token  # Return the same token
            },
            'message': 'Token verified successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Token verification failed',
            'error': str(e)
        }), 500


@auth_supabase_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user - just store profile data, let frontend handle Supabase signup.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        organization = data.get('organization')
        role = data.get('role', 'attorney')
        
        # Validate required fields
        if not all([email, password, first_name, last_name]):
            return jsonify({
                'success': False,
                'message': 'Email, password, first name, and last name are required'
            }), 400
        
        # For now, just return success - frontend will handle Supabase signup
        # We'll create the profile after email confirmation via a webhook or separate endpoint
        return jsonify({
            'success': True,
            'data': {
                'email': email,
                'message': 'Please complete registration using Supabase Auth on the frontend'
            },
            'message': 'Registration initiated. Please check your email for confirmation.'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'error': str(e)
        }), 500


@auth_supabase_bp.route('/profile', methods=['POST'])
@supabase_jwt_required
def create_profile():
    """
    Create user profile after Supabase email confirmation.
    Called by frontend after successful Supabase signup.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        user_id = get_current_user_id()
        supabase_user_id = data.get('supabase_user_id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        organization = data.get('organization')
        role = data.get('role', 'attorney')
        
        # Use the user ID from the JWT token
        if supabase_user_id and supabase_user_id != user_id:
            return jsonify({
                'success': False,
                'message': 'User ID mismatch'
            }), 400
        
        # Validate required fields
        if not all([first_name, last_name]):
            return jsonify({
                'success': False,
                'message': 'First name and last name are required'
            }), 400
        
        # Check if profile already exists
        existing_profile = Profile.query.filter_by(id=user_id).first()
        if existing_profile:
            return jsonify({
                'success': True,
                'data': existing_profile.to_dict(),
                'message': 'Profile already exists'
            })
        
        # Create profile in our database
        role_enum = UserRole.ATTORNEY  # default
        if role == 'investigator':
            role_enum = UserRole.INVESTIGATOR
        elif role == 'admin':
            role_enum = UserRole.ADMIN
        
        profile = Profile(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            organization=organization,
            role=role_enum
        )
        
        db.session.add(profile)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': profile.to_dict(),
            'message': 'Profile created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to create profile',
            'error': str(e)
        }), 500


@auth_supabase_bp.route('/profile', methods=['GET'])
@supabase_jwt_required
def get_profile():
    """Get current user's profile."""
    try:
        user_id = get_current_user_id()
        profile = Profile.query.filter_by(id=user_id).first()
        
        if not profile:
            return jsonify({
                'success': False,
                'message': 'Profile not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': profile.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get profile',
            'error': str(e)
        }), 500


@auth_supabase_bp.route('/profile', methods=['PUT'])
@supabase_jwt_required
def update_profile():
    """Update current user's profile."""
    try:
        user_id = get_current_user_id()
        profile = Profile.query.filter_by(id=user_id).first()
        
        if not profile:
            return jsonify({
                'success': False,
                'message': 'Profile not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Update allowed fields
        if 'first_name' in data:
            profile.first_name = data['first_name']
        if 'last_name' in data:
            profile.last_name = data['last_name']
        if 'organization' in data:
            profile.organization = data['organization']
        if 'phone' in data:
            profile.phone = data['phone']
        if 'bio' in data:
            profile.bio = data['bio']
        if 'avatar_url' in data:
            profile.avatar_url = data['avatar_url']
        if 'preferences' in data:
            profile.preferences = data['preferences']
        
        # Handle role update (admin only in production)
        if 'role' in data:
            role_value = data['role']
            if role_value == 'investigator':
                profile.role = UserRole.INVESTIGATOR
            elif role_value == 'admin':
                profile.role = UserRole.ADMIN
            else:
                profile.role = UserRole.ATTORNEY
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': profile.to_dict(),
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update profile',
            'error': str(e)
        }), 500


@auth_supabase_bp.route('/logout', methods=['POST'])
def logout():
    """
    User logout endpoint.
    With Supabase Auth, logout is handled client-side.
    """
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    }) 