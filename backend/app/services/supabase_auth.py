"""
Supabase Authentication Service
Handles integration with Supabase Auth for user management.
"""

import os
import jwt
import requests
from typing import Optional, Dict, Any
from flask import current_app


class SupabaseAuthService:
    """Service for Supabase Authentication operations."""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.jwt_secret = os.getenv('SUPABASE_JWT_SECRET')
        
        if not all([self.supabase_url, self.supabase_anon_key, self.jwt_secret]):
            raise ValueError("Missing required Supabase environment variables")
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a Supabase JWT token and return user data.
        
        Args:
            token: JWT token from Supabase Auth
            
        Returns:
            User data if token is valid, None otherwise
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=['HS256'],
                audience='authenticated'
            )
            
            return {
                'user_id': payload.get('sub'),
                'email': payload.get('email'),
                'role': payload.get('role'),
                'aud': payload.get('aud'),
                'exp': payload.get('exp')
            }
            
        except jwt.ExpiredSignatureError:
            current_app.logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f"Invalid JWT token: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data from Supabase Auth by user ID.
        Requires service role key.
        
        Args:
            user_id: Supabase auth user ID
            
        Returns:
            User data if found, None otherwise
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.supabase_service_key}',
                'apikey': self.supabase_service_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{self.supabase_url}/auth/v1/admin/users/{user_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                current_app.logger.warning(f"Failed to get user {user_id}: {response.status_code}")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error getting user {user_id}: {str(e)}")
            return None
    
    def create_user(self, email: str, password: str, user_metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new user in Supabase Auth.
        Requires service role key.
        
        Args:
            email: User email
            password: User password
            user_metadata: Additional user metadata
            
        Returns:
            Created user data if successful, None otherwise
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.supabase_service_key}',
                'apikey': self.supabase_service_key,
                'Content-Type': 'application/json'
            }
            
            data = {
                'email': email,
                'password': password,
                'email_confirm': True  # Auto-confirm for now
            }
            
            if user_metadata:
                data['user_metadata'] = user_metadata
            
            response = requests.post(
                f'{self.supabase_url}/auth/v1/admin/users',
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                current_app.logger.warning(f"Failed to create user: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error creating user: {str(e)}")
            return None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user in Supabase Auth.
        Requires service role key.
        
        Args:
            user_id: Supabase auth user ID
            updates: Fields to update
            
        Returns:
            Updated user data if successful, None otherwise
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.supabase_service_key}',
                'apikey': self.supabase_service_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.put(
                f'{self.supabase_url}/auth/v1/admin/users/{user_id}',
                headers=headers,
                json=updates
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                current_app.logger.warning(f"Failed to update user {user_id}: {response.status_code}")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error updating user {user_id}: {str(e)}")
            return None
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user from Supabase Auth.
        Requires service role key.
        
        Args:
            user_id: Supabase auth user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.supabase_service_key}',
                'apikey': self.supabase_service_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.delete(
                f'{self.supabase_url}/auth/v1/admin/users/{user_id}',
                headers=headers
            )
            
            return response.status_code == 200
            
        except Exception as e:
            current_app.logger.error(f"Error deleting user {user_id}: {str(e)}")
            return False


# Global instance
supabase_auth = SupabaseAuthService() 