"""
Flask Application Entry Point
Main entry point for the Video Analyzer backend API.
"""

import os
from app import create_app, create_celery

# Create Flask application
app = create_app(os.getenv('FLASK_ENV', 'development'))

# Create Celery instance
celery = create_celery(app)

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    ) 