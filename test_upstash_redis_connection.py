#!/usr/bin/env python3
"""
Test script to validate Upstash Redis connection and SSL configuration.
This will help diagnose any connection or SSL issues.
"""

import os
import sys
import ssl
import logging
from urllib.parse import urlparse
import asyncio

# Add backend to path
sys.path.append('backend')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_redis_connection():
    """Test basic Redis connection with SSL"""
    try:
        import redis
        from backend.app.core.config import settings
        
        redis_url = settings.REDIS_URL
        logger.info(f"🔍 Testing Redis connection to: {redis_url}")
        
        # Parse URL to check SSL requirements
        parsed_url = urlparse(redis_url)
        use_ssl = parsed_url.scheme == 'rediss'
        
        logger.info(f"🔍 SSL required: {use_ssl}")
        logger.info(f"🔍 Host: {parsed_url.hostname}")
        logger.info(f"🔍 Port: {parsed_url.port}")
        
        if use_ssl:
            # Configure SSL for Upstash Redis
            ssl_config = {
                'ssl_cert_reqs': ssl.CERT_NONE,
                'ssl_check_hostname': False,
                'ssl_ca_certs': None,
                'socket_timeout': 10.0,
                'socket_connect_timeout': 10.0,
            }
            
            logger.info("🔧 Configuring SSL settings for Upstash Redis")
            
            # Create Redis client with SSL
            client = redis.from_url(
                redis_url,
                **ssl_config,
                decode_responses=True
            )
        else:
            # Create Redis client without SSL
            client = redis.from_url(redis_url, decode_responses=True)
        
        # Test basic operations
        logger.info("🧪 Testing basic Redis operations...")
        
        # Test ping
        result = client.ping()
        logger.info(f"✅ PING successful: {result}")
        
        # Test set/get
        test_key = "test_connection_key"
        test_value = "test_connection_value"
        
        client.set(test_key, test_value, ex=60)  # Expire in 60 seconds
        retrieved_value = client.get(test_key)
        
        if retrieved_value == test_value:
            logger.info(f"✅ SET/GET successful: {test_key} = {retrieved_value}")
        else:
            logger.error(f"❌ SET/GET failed: expected {test_value}, got {retrieved_value}")
            return False
        
        # Clean up test key
        client.delete(test_key)
        logger.info("🧹 Cleaned up test key")
        
        # Test connection info
        info = client.info()
        logger.info(f"📊 Redis server version: {info.get('redis_version', 'unknown')}")
        logger.info(f"📊 Connected clients: {info.get('connected_clients', 'unknown')}")
        
        logger.info("✅ All Redis tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Redis connection test failed: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        return False

def test_celery_redis_config():
    """Test Celery Redis configuration"""
    try:
        from backend.app.core.celery_app import get_celery_app
        from backend.app.core.config import settings
        
        logger.info("🔍 Testing Celery Redis configuration...")
        
        # Temporarily enable Celery for testing
        os.environ['DISABLE_CELERY_ON_STARTUP'] = 'false'
        
        # Get Celery app
        celery_app = get_celery_app()
        
        if hasattr(celery_app, 'conf'):
            logger.info(f"📊 Broker URL: {celery_app.conf.broker_url}")
            logger.info(f"📊 Result backend: {celery_app.conf.result_backend}")
            logger.info(f"📊 Task serializer: {celery_app.conf.task_serializer}")
            
            # Check SSL configuration
            if hasattr(celery_app.conf, 'broker_transport_options'):
                ssl_config = celery_app.conf.broker_transport_options
                logger.info(f"📊 SSL cert reqs: {ssl_config.get('ssl_cert_reqs', 'not set')}")
                logger.info(f"📊 SSL check hostname: {ssl_config.get('ssl_check_hostname', 'not set')}")
            
            logger.info("✅ Celery configuration loaded successfully!")
            return True
        else:
            logger.error("❌ Celery app configuration not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Celery configuration test failed: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        return False

def main():
    """Run all Redis connection tests"""
    logger.info("🚀 Starting Upstash Redis connection tests...")
    
    # Test 1: Basic Redis connection
    redis_success = test_redis_connection()
    
    # Test 2: Celery Redis configuration
    celery_success = test_celery_redis_config()
    
    # Summary
    logger.info("=" * 50)
    logger.info("📋 TEST SUMMARY:")
    logger.info(f"   Redis Connection: {'✅ PASS' if redis_success else '❌ FAIL'}")
    logger.info(f"   Celery Config:    {'✅ PASS' if celery_success else '❌ FAIL'}")
    
    if redis_success and celery_success:
        logger.info("🎉 All tests passed! Upstash Redis is properly configured.")
        return True
    else:
        logger.error("💥 Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)