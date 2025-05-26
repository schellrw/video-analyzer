"""Cases Routes"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from ..models.case import Case, CaseStatus, CasePriority
from ..models.user import User
from ..extensions import db

cases_bp = Blueprint('cases', __name__)

@cases_bp.route('/', methods=['GET'])
@jwt_required()
def get_cases():
    """Get all cases for the current user with pagination and filtering."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status = request.args.get('status')
        priority = request.args.get('priority')
        search = request.args.get('search', '').strip()
        
        # Build query
        query = Case.query.filter_by(user_id=current_user_id)
        
        # Apply filters
        if status:
            try:
                status_enum = CaseStatus(status)
                query = query.filter(Case.status == status_enum)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'Invalid status: {status}'
                }), 400
        
        if priority:
            try:
                priority_enum = CasePriority(priority)
                query = query.filter(Case.priority == priority_enum)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'Invalid priority: {priority}'
                }), 400
        
        if search:
            search_filter = f'%{search}%'
            query = query.filter(
                db.or_(
                    Case.name.ilike(search_filter),
                    Case.description.ilike(search_filter),
                    Case.case_number.ilike(search_filter),
                    Case.incident_location.ilike(search_filter)
                )
            )
        
        # Order by most recent first
        query = query.order_by(Case.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        cases = [case.to_dict() for case in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'cases': cases,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving cases: {str(e)}'
        }), 500

@cases_bp.route('/', methods=['POST'])
@jwt_required()
def create_case():
    """Create a new case."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate enums if provided
        if 'status' in data:
            try:
                CaseStatus(data['status'])
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'Invalid status: {data["status"]}'
                }), 400
        
        if 'priority' in data:
            try:
                CasePriority(data['priority'])
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'Invalid priority: {data["priority"]}'
                }), 400
        
        # Parse incident_date if provided
        incident_date = None
        if data.get('incident_date'):
            try:
                incident_date = datetime.fromisoformat(data['incident_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid incident_date format. Use ISO 8601 format.'
                }), 400
        
        # Create new case
        case = Case(
            user_id=current_user_id,
            name=data['name'],
            description=data.get('description'),
            case_number=data.get('case_number'),  # User-provided case number
            incident_date=incident_date,
            incident_location=data.get('incident_location'),
            incident_description=data.get('incident_description'),
            status=CaseStatus(data.get('status', 'pending')),
            priority=CasePriority(data.get('priority', 'medium')),
            tags=data.get('tags', []),
            court_jurisdiction=data.get('court_jurisdiction'),
            opposing_party=data.get('opposing_party'),
            legal_theory=data.get('legal_theory')
        )
        
        db.session.add(case)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': case.to_dict(),
            'message': 'Case created successfully'
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Database error: {str(e)}'
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating case: {str(e)}'
        }), 500

@cases_bp.route('/<case_id>', methods=['GET'])
@jwt_required()
def get_case(case_id):
    """Get a specific case by ID."""
    try:
        current_user_id = get_jwt_identity()
        
        case = Case.query.filter_by(
            id=case_id,
            user_id=current_user_id
        ).first()
        
        if not case:
            return jsonify({
                'success': False,
                'message': 'Case not found'
            }), 404
        
        # Include videos in the response
        include_videos = request.args.get('include_videos', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'data': case.to_dict(include_videos=include_videos)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving case: {str(e)}'
        }), 500

@cases_bp.route('/<case_id>', methods=['PUT'])
@jwt_required()
def update_case(case_id):
    """Update a specific case."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        case = Case.query.filter_by(
            id=case_id,
            user_id=current_user_id
        ).first()
        
        if not case:
            return jsonify({
                'success': False,
                'message': 'Case not found'
            }), 404
        
        # Validate enums if provided
        if 'status' in data:
            try:
                CaseStatus(data['status'])
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'Invalid status: {data["status"]}'
                }), 400
        
        if 'priority' in data:
            try:
                CasePriority(data['priority'])
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'Invalid priority: {data["priority"]}'
                }), 400
        
        # Parse incident_date if provided
        if 'incident_date' in data and data['incident_date']:
            try:
                data['incident_date'] = datetime.fromisoformat(data['incident_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid incident_date format. Use ISO 8601 format.'
                }), 400
        
        # Update fields
        updatable_fields = [
            'name', 'description', 'case_number', 'incident_date', 'incident_location',
            'incident_description', 'status', 'priority', 'tags',
            'court_jurisdiction', 'opposing_party', 'legal_theory'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field in ['status', 'priority']:
                    setattr(case, field, CaseStatus(data[field]) if field == 'status' else CasePriority(data[field]))
                else:
                    setattr(case, field, data[field])
        
        # Set closed_at if status is closed
        if 'status' in data and data['status'] == 'closed' and not case.closed_at:
            case.closed_at = datetime.utcnow()
        elif 'status' in data and data['status'] != 'closed':
            case.closed_at = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': case.to_dict(),
            'message': 'Case updated successfully'
        })
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Database error: {str(e)}'
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating case: {str(e)}'
        }), 500

@cases_bp.route('/<case_id>', methods=['DELETE'])
@jwt_required()
def delete_case(case_id):
    """Delete a specific case."""
    try:
        current_user_id = get_jwt_identity()
        
        case = Case.query.filter_by(
            id=case_id,
            user_id=current_user_id
        ).first()
        
        if not case:
            return jsonify({
                'success': False,
                'message': 'Case not found'
            }), 404
        
        # Check if case has videos
        if case.video_count > 0:
            return jsonify({
                'success': False,
                'message': 'Cannot delete case with associated videos. Delete videos first.'
            }), 400
        
        db.session.delete(case)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Case deleted successfully'
        })
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Database error: {str(e)}'
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting case: {str(e)}'
        }), 500

@cases_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_case_stats():
    """Get case statistics for the current user."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get basic counts
        total_cases = Case.query.filter_by(user_id=current_user_id).count()
        
        # Get counts by status
        status_counts = {}
        for status in CaseStatus:
            count = Case.query.filter_by(
                user_id=current_user_id,
                status=status
            ).count()
            status_counts[status.value] = count
        
        # Get counts by priority
        priority_counts = {}
        for priority in CasePriority:
            count = Case.query.filter_by(
                user_id=current_user_id,
                priority=priority
            ).count()
            priority_counts[priority.value] = count
        
        # Get recent activity (cases created in last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_cases = Case.query.filter(
            Case.user_id == current_user_id,
            Case.created_at >= thirty_days_ago
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_cases': total_cases,
                'status_counts': status_counts,
                'priority_counts': priority_counts,
                'recent_cases': recent_cases
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving case statistics: {str(e)}'
        }), 500 