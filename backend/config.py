"""
Flask Configuration Module
Handles environment-specific configuration for the Video Analyzer backend.
"""

import os
from datetime import timedelta
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings."""
    
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/video_analyzer'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
    SUPABASE_JWT_SECRET = os.environ.get('SUPABASE_JWT_SECRET')
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # Digital Ocean Spaces Configuration
    DO_SPACES_KEY = os.environ.get('DO_SPACES_KEY')
    DO_SPACES_SECRET = os.environ.get('DO_SPACES_SECRET')
    DO_SPACES_ENDPOINT = os.environ.get('DO_SPACES_ENDPOINT', 'https://nyc3.digitaloceanspaces.com')
    DO_SPACES_BUCKET = os.environ.get('DO_SPACES_BUCKET', 'video-analyzer')
    DO_SPACES_REGION = os.environ.get('DO_SPACES_REGION', 'nyc3')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 2GB max file size
    UPLOAD_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    
    # AI Model Configuration
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')  # Optional
    
    # Model Paths and Settings
    WHISPER_MODEL = os.environ.get('WHISPER_MODEL', 'base')
    LLAVA_MODEL = os.environ.get('LLAVA_MODEL', 'llava-hf/llava-1.5-7b-hf')
    NLP_MODEL_PATH = os.environ.get('NLP_MODEL_PATH', 'ai-models/violation_detection/')
    
    # Email Configuration (SendGrid)
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@videoanalyzer.tech')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "1000 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # CORS Configuration
    CORS_ORIGINS = [
        'http://localhost:3000',  # Development frontend
        'http://localhost:5173',  # Vite dev server
        'https://videoanalyzer.tech',  # Production frontend
    ]
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    
    # Monitoring
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        pass


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'
    
    # Disable rate limiting in development
    RATELIMIT_ENABLED = False
    
    # Allow all origins in development
    CORS_ORIGINS = ['*']
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        import logging
        logging.basicConfig(level=logging.DEBUG)


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable JWT expiration for tests
    JWT_ACCESS_TOKEN_EXPIRES = False
    
    # Use fake Redis for tests
    REDIS_URL = 'redis://localhost:6379/1'
    
    # Disable external services in tests
    SENDGRID_API_KEY = 'test-key'
    SENTRY_DSN = None
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Strict CORS in production
    CORS_ORIGINS = [
                    'https://videoanalyzer.tech',
        'https://yourdomain.com',
    ]
    
    # Enhanced security headers
    FORCE_HTTPS = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database connection pooling for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 20,
        'pool_size': 10
    }
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Initialize Sentry for error tracking
        if Config.SENTRY_DSN:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.celery import CeleryIntegration
            
            sentry_sdk.init(
                dsn=Config.SENTRY_DSN,
                integrations=[
                    FlaskIntegration(),
                    CeleryIntegration()
                ],
                traces_sample_rate=0.1,
                environment=Config.FLASK_ENV
            )


class StagingConfig(ProductionConfig):
    """Staging environment configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Less strict rate limiting for staging
    RATELIMIT_DEFAULT = "2000 per hour"
    
    # Allow staging domains
    CORS_ORIGINS = [
                    'https://staging.videoanalyzer.tech',
        'https://staging.yourdomain.com',
    ]


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default']) 