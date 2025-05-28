"""
Redis Service - Simplified for Upstash
Provides Redis functionality with optional local fallback (only if available).
"""

import os
import logging
import json
import time
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Try to import redis, but don't fail if not available
try:
    import redis
    from redis.exceptions import ConnectionError, TimeoutError, ResponseError
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis not available - caching will be disabled")
    REDIS_AVAILABLE = False


class RedisService:
    """Redis service with optional local fallback."""
    
    def __init__(self):
        """Initialize Redis service."""
        self.primary_redis = None
        self.fallback_redis = None
        self.using_fallback = False
        self.command_count = 0
        # Upstash free tier: 10,000 commands/day (not 500k!)
        self.daily_limit = int(os.getenv('REDIS_DAILY_LIMIT', '10000'))
        self.last_reset = datetime.now().date()
        self.redis_available = REDIS_AVAILABLE
        
        if not self.redis_available:
            logger.warning("Redis library not installed - all caching operations will be no-ops")
            return
        
        # Initialize connections
        self._setup_connections()
        
        logger.info(f"RedisService initialized. Redis available: {self.redis_available}, Using fallback: {self.using_fallback}")
    
    def _setup_connections(self):
        """Setup Redis connections."""
        if not self.redis_available:
            return
            
        # Primary Redis (your existing Upstash setup)
        redis_url = os.getenv('REDIS_URL')  # Your existing variable
        
        if redis_url:
            try:
                self.primary_redis = redis.Redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                
                # Test connection
                self.primary_redis.ping()
                logger.info("Connected to Upstash Redis")
                self.using_fallback = False
                
            except Exception as e:
                logger.warning(f"Failed to connect to Upstash Redis: {str(e)}")
                self.primary_redis = None
        
        # Optional fallback Redis (only if user has local Redis running)
        local_redis_url = os.getenv('LOCAL_REDIS_URL', 'redis://localhost:6379/0')
        
        try:
            self.fallback_redis = redis.Redis.from_url(
                local_redis_url,
                decode_responses=True,
                socket_timeout=2,  # Shorter timeout for local
                socket_connect_timeout=2
            )
            
            # Test connection
            self.fallback_redis.ping()
            logger.info("Local Redis available as fallback")
            
        except Exception as e:
            logger.debug(f"Local Redis not available (this is fine): {str(e)}")
            self.fallback_redis = None
        
        # Determine which connection to use
        if self.primary_redis and not self._is_over_limit():
            self.using_fallback = False
        elif self.fallback_redis:
            self.using_fallback = True
            logger.info("Using fallback Redis (local)")
        else:
            logger.warning("No Redis connection available - caching disabled")
    
    def _is_over_limit(self) -> bool:
        """Check if we're over the daily command limit."""
        if not self.redis_available:
            return False
            
        # Reset counter if it's a new day
        if datetime.now().date() > self.last_reset:
            self.command_count = 0
            self.last_reset = datetime.now().date()
        
        return self.command_count >= self.daily_limit
    
    def _get_redis_client(self) -> Optional:
        """Get the appropriate Redis client."""
        if not self.redis_available:
            return None
            
        # Check if we need to switch to fallback due to limits
        if not self.using_fallback and self._is_over_limit():
            logger.warning("Switching to fallback Redis due to command limit")
            self.using_fallback = True
        
        if self.using_fallback:
            return self.fallback_redis
        else:
            return self.primary_redis
    
    def _execute_command(self, func, *args, **kwargs) -> Any:
        """Execute a Redis command with error handling and fallback."""
        if not self.redis_available:
            return None
            
        client = self._get_redis_client()
        
        if not client:
            logger.debug("No Redis client available")
            return None
        
        try:
            result = func(*args, **kwargs)
            
            # Increment command count only for primary Redis
            if not self.using_fallback:
                self.command_count += 1
            
            return result
            
        except Exception as e:
            logger.debug(f"Redis command failed: {str(e)}")
            
            # Try fallback if primary failed
            if not self.using_fallback and self.fallback_redis:
                logger.info("Switching to fallback Redis due to error")
                self.using_fallback = True
                
                try:
                    return func(*args, **kwargs)
                except Exception as fallback_error:
                    logger.debug(f"Fallback Redis also failed: {str(fallback_error)}")
                    return None
            
            return None
    
    # Simplified Redis methods that gracefully handle missing Redis
    def get(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        if not self.redis_available:
            return None
        client = self._get_redis_client()
        if not client:
            return None
        return self._execute_command(client.get, key)
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set a value in Redis with optional expiration."""
        if not self.redis_available:
            return False
        client = self._get_redis_client()
        if not client:
            return False
        result = self._execute_command(client.set, key, value, ex=ex)
        return result is not None
    
    def delete(self, *keys: str) -> int:
        """Delete one or more keys from Redis."""
        if not self.redis_available:
            return 0
        client = self._get_redis_client()
        if not client:
            return 0
        result = self._execute_command(client.delete, *keys)
        return result or 0
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        if not self.redis_available:
            return False
        client = self._get_redis_client()
        if not client:
            return False
        result = self._execute_command(client.exists, key)
        return bool(result)
    
    def ping(self) -> bool:
        """Ping Redis to check connection."""
        if not self.redis_available:
            return False
        client = self._get_redis_client()
        if not client:
            return False
        try:
            result = self._execute_command(client.ping)
            return result is True
        except:
            return False
    
    # Cache-specific methods with graceful fallback
    def cache_set(self, key: str, data: Any, ttl: int = 3600) -> bool:
        """Set cached data with JSON serialization."""
        if not self.redis_available:
            logger.debug(f"Redis not available - skipping cache set for {key}")
            return False
        try:
            serialized_data = json.dumps(data)
            return self.set(key, serialized_data, ex=ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize data for cache: {str(e)}")
            return False
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get cached data with JSON deserialization."""
        if not self.redis_available:
            return None
        try:
            data = self.get(key)
            if data:
                return json.loads(data)
            return None
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to deserialize cached data: {str(e)}")
            return None
    
    def cache_analysis_result(self, video_path: str, frame_hash: str, 
                            analysis_result: Dict[str, Any], ttl: int = 86400) -> bool:
        """Cache video analysis result."""
        cache_key = f"analysis:{video_path}:{frame_hash}"
        return self.cache_set(cache_key, analysis_result, ttl)
    
    def get_cached_analysis_result(self, video_path: str, 
                                 frame_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached video analysis result."""
        cache_key = f"analysis:{video_path}:{frame_hash}"
        return self.cache_get(cache_key)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get Redis usage statistics."""
        return {
            'redis_available': self.redis_available,
            'using_fallback': self.using_fallback,
            'command_count': self.command_count,
            'daily_limit': self.daily_limit,
            'commands_remaining': max(0, self.daily_limit - self.command_count),
            'last_reset': self.last_reset.isoformat(),
            'primary_available': self.primary_redis is not None,
            'fallback_available': self.fallback_redis is not None
        }
    
    def force_fallback(self) -> bool:
        """Force switch to fallback Redis."""
        if not self.redis_available:
            return False
        if self.fallback_redis:
            self.using_fallback = True
            logger.info("Forced switch to fallback Redis")
            return True
        return False
    
    def try_primary(self) -> bool:
        """Try to switch back to primary Redis."""
        if not self.redis_available:
            return False
        if self.primary_redis and not self._is_over_limit():
            try:
                self.primary_redis.ping()
                self.using_fallback = False
                logger.info("Switched back to primary Redis")
                return True
            except Exception as e:
                logger.warning(f"Primary Redis still unavailable: {str(e)}")
        return False


# Global Redis service instance
redis_service = RedisService() 