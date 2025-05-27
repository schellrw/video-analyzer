"""
Celery Application Entry Point
Dedicated entry point for Celery workers.
"""

import os
from app import create_app, create_celery

# Create Flask app and Celery instance
flask_app = create_app(os.getenv('FLASK_ENV', 'development'))
celery = create_celery(flask_app)

if __name__ == '__main__':
    celery.start() 