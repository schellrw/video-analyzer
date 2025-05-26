"""
Profile Model for Supabase Auth Integration
This model extends Supabase auth.users with additional user information.
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM

from ..extensions import db


class UserRole(Enum):
    """User role enumeration."""
    ATTORNEY = "attorney"
    INVESTIGATOR = "investigator"
    ADMIN = "admin"


class Profile(db.Model):
    """
    User profile model that extends Supabase auth.users.
    References auth.users.id as the primary key.
    """
    __tablename__ = 'profiles'
    
    # Primary key that references auth.users.id
    id = Column(UUID(as_uuid=True), primary_key=True)
    
    # Profile information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    organization = Column(String(200))
    role = Column(ENUM(UserRole), nullable=False, default=UserRole.ATTORNEY)
    phone = Column(String(20))
    bio = Column(Text)
    avatar_url = Column(String(500))
    preferences = Column(db.JSON, default=dict)
    
    # Timestamps
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