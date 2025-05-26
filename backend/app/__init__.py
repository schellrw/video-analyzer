"""
Flask Application Factory
Creates and configures the Flask application with all extensions and blueprints.
"""

import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery

from config import config
from .extensions import db, jwt, limiter, ma
from .utils.error_handlers import register_error_handlers
from .utils.logging_config import setup_logging


def create_app(config_name: str = 'development') -> Flask:
    """
    Application factory pattern for creating Flask app.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config_class = config[config_name]
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # Disable automatic trailing slash redirects that cause CORS issues
    app.url_map.strict_slashes = False
    
    # Initialize extensions
    init_extensions(app)
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup CORS with more permissive settings for development
    CORS(app, 
         origins=app.config.get('CORS_ORIGINS', ['*']),
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=True)
    
    return app


def init_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    ma.init_app(app)


def register_blueprints(app: Flask) -> None:
    """Register application blueprints."""
    from .routes.auth_supabase import auth_supabase_bp
    from .routes.cases import cases_bp
    from .routes.videos import videos_bp
    from .routes.analysis import analysis_bp
    from .routes.reports import reports_bp
    from .routes.admin import admin_bp
    from .routes.health import health_bp
    
    # API version prefix
    api_prefix = '/api'
    
    app.register_blueprint(health_bp, url_prefix=api_prefix)
    app.register_blueprint(auth_supabase_bp, url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(cases_bp, url_prefix=f'{api_prefix}/cases')
    app.register_blueprint(videos_bp, url_prefix=f'{api_prefix}/videos')
    app.register_blueprint(analysis_bp, url_prefix=f'{api_prefix}/analysis')
    app.register_blueprint(reports_bp, url_prefix=f'{api_prefix}/reports')
    app.register_blueprint(admin_bp, url_prefix=f'{api_prefix}/admin')


def create_celery(app: Flask = None) -> Celery:
    """
    Create Celery instance with Flask app context.
    
    Args:
        app: Flask application instance
        
    Returns:
        Configured Celery instance
    """
    app = app or create_app()
    
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    
    celery.conf.update(
        task_serializer=app.config['CELERY_TASK_SERIALIZER'],
        result_serializer=app.config['CELERY_RESULT_SERIALIZER'],
        accept_content=app.config['CELERY_ACCEPT_CONTENT'],
        timezone=app.config['CELERY_TIMEZONE'],
        enable_utc=app.config['CELERY_ENABLE_UTC'],
    )
    
    # Update task base classes for Flask app context
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    # Import tasks to register them
    from . import tasks  # noqa
    
    return celery 