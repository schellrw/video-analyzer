"""Authentication Routes"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from datetime import timedelta
from ..extensions import db
from ..models import User, Profile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password required'
            }), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_active:
            # Create access token
            access_token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(hours=24)
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'access_token': access_token,
                    'user': user.to_dict()
                },
                'message': 'Login successful'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Login failed',
            'error': str(e)
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
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
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'message': 'User with this email already exists'
            }), 409
        
        # Create new user
        user = User(email=email)
        user.set_password(password)
        user.is_verified = True  # Auto-verify for now, implement email verification later
        
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create profile
        profile = Profile(
            id=user.id,
            first_name=first_name,
            last_name=last_name,
            organization=organization,
            role=role
        )
        
        db.session.add(profile)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': access_token,
                'user': user.to_dict()
            },
            'message': 'Registration successful'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'error': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint."""
    # With JWT, logout is typically handled client-side by removing the token
    # For enhanced security, you could implement a token blacklist
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    }) 