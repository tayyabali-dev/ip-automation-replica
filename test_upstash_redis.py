#!/usr/bin/env python3
"""
Test script to verify Upstash Redis connection with SSL
"""
import os
import sys
import ssl
import redis
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv('backend/.env')

def test_upstash_redis():
    """Test Upstash Redis connection with SSL"""
    
    # Get Redis URL from environment
    redis_url = os.getenv('REDIS_URL')
    
    if not redis_url:
        print("❌ REDIS_URL not found in environment variables")
        return False
    
    print(f"Testing Upstash Redis connection...")
    print(f"Redis URL: {redis_url[:30]}...")
    
    try:
        # Parse URL to determine if SSL is needed
        parsed_url = urlparse(redis_url)
        use_ssl = parsed_url.scheme == 'rediss'
        
        print(f"SSL Mode: {'Enabled' if use_ssl else 'Disabled'}")
        print(f"Host: {parsed_url.hostname}")
        print(f"Port: {parsed_url.port}")
        
        # Create Redis connection with SSL configuration
        if use_ssl:
            print("Configuring SSL connection for Upstash...")
            r = redis.Redis.from_url(
                redis_url,
                ssl_cert_reqs=ssl.CERT_NONE,
                ssl_check_hostname=False,
                ssl_ca_certs=None,
                ssl_certfile=None,
                ssl_keyfile=None,
                socket_timeout=10,
                socket_connect_timeout=10
            )
        else:
            r = redis.Redis.from_url(redis_url)
        
        # Test connection
        print("Testing connection...")
        response = r.ping()
        
        if response:
            print("✅ Upstash Redis connection successful!")
            
            # Test basic operations
            print("Testing basic operations...")
            r.set('test_key', 'test_value', ex=60)  # Expire in 60 seconds
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
        print(f"❌ Upstash Redis connection failed: {e}")
        return False

def test_celery_import():
    """Test importing Celery configuration"""
    print("\nTesting Celery import...")
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.getcwd(), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Import Celery app
        from app.core.celery_app import celery_app
        from app.core.config import settings
        
        print(f"✅ Celery imported successfully")
        print(f"Broker URL: {settings.CELERY_BROKER_URL[:30]}...")
        print(f"Result Backend: {settings.CELERY_RESULT_BACKEND[:30]}...")
        
        # Check SSL configuration
        broker_options = celery_app.conf.get('broker_transport_options', {})
        if broker_options:
            print("✅ SSL broker transport options configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery import failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Upstash Redis & Celery SSL Test")
    print("=" * 50)
    
    # Test Upstash Redis connection
    redis_success = test_upstash_redis()
    
    # Test Celery configuration
    celery_success = test_celery_import()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"• Upstash Redis: {'✅ PASSED' if redis_success else '❌ FAILED'}")
    print(f"• Celery Config: {'✅ PASSED' if celery_success else '❌ FAILED'}")
    
    if redis_success and celery_success:
        print("\n🎉 All tests passed! Redis and Celery are configured correctly.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. This may be causing the startup hang.")
        sys.exit(1)