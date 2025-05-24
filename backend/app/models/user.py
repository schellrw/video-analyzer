"""
User and Profile Models
Handles user authentication and profile information.
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db


class UserRole(Enum):
    """User role enumeration."""
    ATTORNEY = "attorney"
    INVESTIGATOR = "investigator"
    ADMIN = "admin"


class User(db.Model):
    """
    User model for authentication.
    This extends Supabase auth.users functionality.
    """
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))  # For local dev, Supabase handles this in prod
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to profile
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password: str) -> None:
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check password against hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            'id': str(self.id),
            'email': self.email,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'profile': self.profile.to_dict() if self.profile else None
        }
    
    def __repr__(self) -> str:
        return f'<User {self.email}>'


class Profile(db.Model):
    """
    User profile model with extended information.
    """
    __tablename__ = 'profiles'
    
    id = Column(UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    organization = Column(String(200))
    role = Column(ENUM(UserRole), nullable=False, default=UserRole.ATTORNEY)
    phone = Column(String(20))
    bio = Column(Text)
    avatar_url = Column(String(500))
    preferences = Column(db.JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> dict:
        """Convert profile to dictionary."""
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'organization': self.organization,
            'role': self.role.value if self.role else None,
            'phone': self.phone,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self) -> str:
        return f'<Profile {self.full_name}>' 