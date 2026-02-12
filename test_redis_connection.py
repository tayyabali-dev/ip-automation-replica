#!/usr/bin/env python3
"""
Test script to verify Redis connection with SSL support for Upstash
"""
import os
import sys
import ssl
import redis
from urllib.parse import urlparse

def test_redis_connection():
    """Test Redis connection with SSL support"""
    
    # Get Redis URL from environment or use default
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    print(f"Testing Redis connection to: {redis_url}")
    
    try:
        # Parse URL to determine if SSL is needed
        parsed_url = urlparse(redis_url)
        use_ssl = parsed_url.scheme == 'rediss'
        
        print(f"SSL Mode: {'Enabled' if use_ssl else 'Disabled'}")
        
        # Create Redis connection
        if use_ssl:
            # SSL configuration for Upstash
            r = redis.Redis.from_url(
                redis_url,
                ssl_cert_reqs=ssl.CERT_NONE,
                ssl_ca_certs=None,
                ssl_certfile=None,
                ssl_keyfile=None,
            )
        else:
            # Standard Redis connection
            r = redis.Redis.from_url(redis_url)
        
        # Test connection
        print("Testing connection...")
        response = r.ping()
        
        if response:
            print("✅ Redis connection successful!")
            
            # Test basic operations
            print("Testing basic operations...")
            r.set('test_key', 'test_value')
            value = r.get('test_key')
            
            if value and value.decode() == 'test_value':
                print("✅ Redis read/write operations successful!")
                r.delete('test_key')  # Clean up
                return True
            else:
                print("❌ Redis read/write operations failed!")
                return False
        else:
            print("❌ Redis ping failed!")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_celery_config():
    """Test Celery configuration"""
    print("\nTesting Celery configuration...")
    
    try:
        # Import the celery app
        sys.path.append('backend')
        from app.core.celery_app import celery_app
        from app.core.config import settings
        
        print(f"Celery broker URL: {settings.CELERY_BROKER_URL}")
        print(f"Celery result backend: {settings.CELERY_RESULT_BACKEND}")
        
        # Check SSL configuration
        broker_options = celery_app.conf.get('broker_transport_options', {})
        redis_ssl = celery_app.conf.get('redis_backend_use_ssl', {})
        
        if broker_options:
            print("✅ SSL broker transport options configured")
        if redis_ssl:
            print("✅ SSL result backend options configured")
            
        print("✅ Celery configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Celery configuration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Redis & Celery Configuration Test")
    print("=" * 50)
    
    # Test Redis connection
    redis_success = test_redis_connection()
    
    # Test Celery configuration
    celery_success = test_celery_config()
    
    print("\n" + "=" * 50)
    if redis_success and celery_success:
        print("🎉 All tests passed! Configuration is ready for cloud deployment.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
        sys.exit(1)