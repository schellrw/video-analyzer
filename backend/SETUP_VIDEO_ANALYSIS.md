# Video Analysis Setup Guide

This guide will help you set up and test the video analysis functionality locally.

## Prerequisites

1. **Python 3.11+** installed
2. **Redis server** running locally
3. **HuggingFace Pro account** with API token
4. **Video files** for testing

## Setup Steps

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `backend/.env` file with:

```bash
# Required for video analysis
HUGGINGFACE_API_KEY=hf_your_read_token_here

# Upstash Redis configuration (recommended)
REDIS_URL=rediss://default:your_password@your_host:6379/1
CELERY_BROKER_URL=rediss://default:your_password@your_host:6379/1
CELERY_RESULT_BACKEND=rediss://default:your_password@your_host:6379/1

# OR Local Redis (if you prefer local development)
# REDIS_URL=redis://localhost:6379/0
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Flask configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-secret-key

# Database (optional for local testing)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/video_analyzer
```

### 3. Add Test Videos

Create the uploads directory and add some video files:

```bash
mkdir -p backend/uploads
# Copy your test video files to backend/uploads/
```

Supported formats: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.flv`

### 4. Start the Services

**Terminal 1 - Flask API:**
```bash
cd backend
python run.py
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
celery -A celery_app.celery worker --loglevel=info --pool=solo
```

**Terminal 3 - Celery Flower (optional monitoring):**
```bash
cd backend
celery -A celery_app.celery flower
```

## Testing the Analysis

### Option 1: Use the Test Script

```bash
cd backend
python test_video_analysis.py
```

This script will:
1. Check your environment setup
2. List available videos in the uploads folder
3. Start analysis on the first video found
4. Monitor progress and display results

### Option 2: Manual API Testing

**1. List available videos:**
```bash
curl http://localhost:5000/api/analysis/list-local-videos
```

**2. Start analysis:**
```bash
curl -X POST http://localhost:5000/api/analysis/test-local \
  -H "Content-Type: application/json" \
  -d '{"video_path": "/path/to/your/video.mp4", "case_id": "test-001"}'
```

**3. Check task status:**
```bash
curl http://localhost:5000/api/analysis/task/YOUR_TASK_ID
```

## Expected Results

The analysis will:

1. **Extract frames** at 1 FPS (1 frame per second)
2. **Analyze each frame** using LLaVA model for:
   - Civil rights violations
   - Police misconduct
   - Excessive force
   - Constitutional violations
3. **Generate summary** with:
   - Overall confidence score
   - Detected violations
   - Key concerning frames
   - Detailed descriptions

## Sample Output

```json
{
  "status": "completed",
  "analysis_results": {
    "total_frames_analyzed": 30,
    "overall_confidence": 0.75,
    "concerns_found": true,
    "violations_detected": ["excessive force", "misconduct"],
    "summary": {
      "average_confidence": 0.75,
      "key_findings": [
        {
          "frame": 15,
          "timestamp": 15,
          "confidence": 0.85,
          "description": "The image shows what appears to be..."
        }
      ]
    }
  }
}
```

## Troubleshooting

### Common Issues

**1. "HUGGINGFACE_API_KEY environment variable is required"**
- Make sure your `.env` file exists and contains your HF token
- Verify the token is valid and has Pro subscription benefits

**2. "Cannot connect to Flask server"**
- Ensure Flask is running on localhost:5000
- Check for port conflicts

**3. "Redis connection failed"**
- If using Upstash: Check your Redis URL and credentials in `.env`
- If using local Redis: Start Redis server with `redis-server`
- Test connection: `redis-cli ping` (should return "PONG")

**4. "No videos found in uploads directory"**
- Add video files to `backend/uploads/`
- Ensure files have supported extensions

**5. "Analysis failed" or timeout****
- Check Celery worker logs for detailed errors
- Verify HuggingFace API is accessible
- Try with a smaller/shorter video file

### Monitoring Tools

**Celery Flower Dashboard:**
- URL: http://localhost:5555
- Monitor task progress and worker status

**Redis CLI:**
```bash
redis-cli monitor  # Watch Redis commands in real-time
```

**Flask Logs:**
- Check terminal output for detailed error messages

## Performance Notes

- **Frame extraction**: ~1 frame per second (reduces processing time by 97%)
- **Analysis time**: ~2-3 minutes for a 30-second video
- **Memory usage**: ~2-4GB RAM during processing
- **API costs**: ~$0.10-0.50 per video (depending on length)

## Next Steps

Once local testing works:

1. **Deploy to production** with Digital Ocean Spaces
2. **Implement file uploads** with presigned URLs
3. **Add authentication** for production endpoints
4. **Scale Celery workers** for concurrent processing
5. **Add result caching** to avoid reprocessing

## Support

If you encounter issues:

1. Check the logs in all terminals
2. Verify your HuggingFace token has Pro benefits
3. Test with a simple, short video file first
4. Ensure all dependencies are installed correctly 