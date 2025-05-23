# app.py - Main Flask application
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from datetime import datetime, timedelta
import uuid
from werkzeug.utils import secure_filename
import json

# Import our custom modules
from video_processor import VideoProcessor
from ai_analyzer import AIAnalyzer
from violation_detector import ViolationDetector
from supabase_client import SupabaseClient
from report_generator import ReportGenerator

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024  # 16GB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
CORS(app)
jwt = JWTManager(app)

# Initialize our services
video_processor = VideoProcessor()
ai_analyzer = AIAnalyzer()
violation_detector = ViolationDetector()
supabase_client = SupabaseClient()
report_generator = ReportGenerator()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user with Supabase"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Authenticate with Supabase
        user = supabase_client.authenticate(email, password)
        if user:
            access_token = create_access_token(
                identity=user['id'],
                expires_delta=timedelta(hours=24)
            )
            return jsonify({
                'access_token': access_token,
                'user': user
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cases', methods=['GET', 'POST'])
@jwt_required()
def handle_cases():
    """Get all cases or create a new case"""
    user_id = get_jwt_identity()
    
    if request.method == 'GET':
        try:
            cases = supabase_client.get_user_cases(user_id)
            return jsonify(cases)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            case_data = {
                'name': data.get('name'),
                'description': data.get('description', ''),
                'user_id': user_id,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'created'
            }
            
            case = supabase_client.create_case(case_data)
            return jsonify(case), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/cases/<case_id>/upload', methods=['POST'])
@jwt_required()
def upload_video(case_id):
    """Upload video file to a specific case"""
    user_id = get_jwt_identity()
    
    # Verify case ownership
    if not supabase_client.verify_case_access(case_id, user_id):
        return jsonify({'error': 'Access denied'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        stored_filename = f"{file_id}.{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_filename)
        
        # Save file
        file.save(file_path)
        
        # Get file metadata
        file_info = video_processor.get_video_info(file_path)
        
        # Store file record in database
        file_record = {
            'id': file_id,
            'case_id': case_id,
            'original_filename': filename,
            'stored_filename': stored_filename,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'duration': file_info.get('duration', 0),
            'fps': file_info.get('fps', 0),
            'resolution': file_info.get('resolution', ''),
            'uploaded_at': datetime.utcnow().isoformat(),
            'status': 'uploaded'
        }
        
        supabase_client.create_file_record(file_record)
        
        return jsonify({
            'file_id': file_id,
            'message': 'File uploaded successfully',
            'file_info': file_info
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<file_id>/analyze', methods=['POST'])
@jwt_required()
def analyze_video(file_id):
    """Start analysis of uploaded video"""
    user_id = get_jwt_identity()
    
    try:
        # Get file record and verify access
        file_record = supabase_client.get_file_record(file_id)
        if not file_record or not supabase_client.verify_case_access(file_record['case_id'], user_id):
            return jsonify({'error': 'File not found or access denied'}), 404
        
        # Update status to processing
        supabase_client.update_file_status(file_id, 'processing')
        
        # Start async analysis process
        analysis_id = str(uuid.uuid4())
        
        # This would typically be sent to a job queue (Celery/Redis)
        # For now, we'll process synchronously for simplicity
        analysis_result = perform_video_analysis(file_record, analysis_id)
        
        return jsonify({
            'analysis_id': analysis_id,
            'status': 'started',
            'message': 'Analysis started successfully'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def perform_video_analysis(file_record, analysis_id):
    """Perform the actual video analysis"""
    try:
        file_path = file_record['file_path']
        
        # Step 1: Process video (chunking, frame extraction)
        chunks = video_processor.chunk_video(file_path)
        
        # Step 2: Extract audio and transcribe
        audio_path = video_processor.extract_audio(file_path)
        transcript = ai_analyzer.transcribe_audio(audio_path)
        
        # Step 3: Analyze video frames
        visual_analysis = []
        for chunk in chunks:
            frames = video_processor.extract_frames(chunk)
            chunk_analysis = ai_analyzer.analyze_frames(frames)
            visual_analysis.extend(chunk_analysis)
        
        # Step 4: Detect violations
        violations = violation_detector.detect_violations(visual_analysis, transcript)
        
        # Step 5: Generate structured report
        report = report_generator.generate_report({
            'file_id': file_record['id'],
            'visual_analysis': visual_analysis,
            'transcript': transcript,
            'violations': violations,
            'analysis_id': analysis_id
        })
        
        # Step 6: Store results
        analysis_record = {
            'id': analysis_id,
            'file_id': file_record['id'],
            'transcript': transcript,
            'visual_analysis': visual_analysis,
            'violations': violations,
            'report': report,
            'completed_at': datetime.utcnow().isoformat(),
            'status': 'completed'
        }
        
        supabase_client.store_analysis_results(analysis_record)
        supabase_client.update_file_status(file_record['id'], 'analyzed')
        
        return report
        
    except Exception as e:
        # Update status to failed
        supabase_client.update_file_status(file_record['id'], 'failed')
        raise e

@app.route('/api/analysis/<analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis_results(analysis_id):
    """Get analysis results"""
    user_id = get_jwt_identity()
    
    try:
        analysis = supabase_client.get_analysis_results(analysis_id)
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Verify user has access to this analysis
        file_record = supabase_client.get_file_record(analysis['file_id'])
        if not supabase_client.verify_case_access(file_record['case_id'], user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/<analysis_id>/report', methods=['GET'])
@jwt_required()
def download_report(analysis_id):
    """Download generated report"""
    user_id = get_jwt_identity()
    
    try:
        analysis = supabase_client.get_analysis_results(analysis_id)
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Verify access
        file_record = supabase_client.get_file_record(analysis['file_id'])
        if not supabase_client.verify_case_access(file_record['case_id'], user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        # Generate PDF report
        pdf_path = report_generator.generate_pdf_report(analysis['report'])
        
        return send_file(pdf_path, as_attachment=True, download_name=f'analysis_report_{analysis_id}.pdf')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)