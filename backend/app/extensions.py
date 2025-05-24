"""
Flask Extensions
Centralized initialization of Flask extensions.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_marshmallow import Marshmallow
import redis

# Database ORM
db = SQLAlchemy()

# JWT Authentication
jwt = JWTManager()

# Rate Limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

# Serialization/Deserialization
ma = Marshmallow()

# Redis client (initialized in app factory)
redis_client = None


def init_redis(app):
    """Initialize Redis client with app configuration."""
    global redis_client
    redis_client = redis.from_url(app.config['REDIS_URL']) 