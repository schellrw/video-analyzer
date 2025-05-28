#!/usr/bin/env python3
"""
Simple Celery Setup - No Redis Backend
Just uses Redis as broker, no result backend to avoid all the serialization issues.
"""

import os
import sys
from pathlib import Path
from celery import Celery

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Clear any result backend environment variables that might interfere
if 'CELERY_RESULT_BACKEND' in os.environ:
    del os.environ['CELERY_RESULT_BACKEND']

# Create simple Celery app
app = Celery('video_analyzer')

# Simple configuration - Redis broker only, no result backend
app.conf.update(
    broker_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    result_backend=None,  # No result backend - we'll handle results in our API
    task_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_ignore_result=True,  # No result storage
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    # Explicitly disable result backend
    task_store_eager_result=False,
    result_expires=None,
    # More aggressive disabling
    result_backend_transport_options={},
    result_backend_max_retries=0,
)

# Force disable result backend multiple ways
app.conf.result_backend = None
app.conf['result_backend'] = None

# Set up Flask app context
from app import create_app
flask_app = create_app()

class ContextTask(app.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

app.Task = ContextTask

# Import tasks
from app import tasks

if __name__ == '__main__':
    # Start worker with minimal settings
    app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=1',
        '--pool=solo',  # Windows compatible
    ]) 