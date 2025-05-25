"""Authentication Routes"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from datetime import timedelta
from ..extensions import db
from ..models import User, Profile, UserRole

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
            
            # Create user response data
            user_data = {
                'id': str(user.id),
                'email': user.email,
                'firstName': user.profile.first_name if user.profile else '',
                'lastName': user.profile.last_name if user.profile else '',
                'organization': user.profile.organization if user.profile else '',
                'role': user.profile.role.value if user.profile else 'attorney',
                'is_active': user.is_active,
                'is_verified': user.is_verified
            }
            
            return jsonify({
                'success': True,
                'data': {
                    'access_token': access_token,
                    'user': user_data
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
        # Convert role string to enum
        role_enum = UserRole.ATTORNEY  # default
        if role == 'investigator':
            role_enum = UserRole.INVESTIGATOR
        elif role == 'admin':
            role_enum = UserRole.ADMIN
        
        profile = Profile(
            id=user.id,
            first_name=first_name,
            last_name=last_name,
            organization=organization,
            role=role_enum
        )
        
        db.session.add(profile)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24)
        )
        
        # Create user response data manually to avoid relationship issues
        user_data = {
            'id': str(user.id),
            'email': user.email,
            'firstName': profile.first_name,
            'lastName': profile.last_name,
            'organization': profile.organization,
            'role': profile.role.value,
            'is_active': user.is_active,
            'is_verified': user.is_verified
        }
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': access_token,
                'user': user_data
            },
            'message': 'Registration successful'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")  # Debug logging
        import traceback
        traceback.print_exc()  # Print full stack trace
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