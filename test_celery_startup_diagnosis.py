#!/usr/bin/env python3
"""
Diagnostic script to identify why backend server hangs during startup.
Tests Celery initialization and Redis connectivity separately.
"""

import os
import sys
import time
import logging
from urllib.parse import urlparse

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_redis_connection():
    """Test Redis connection independently"""
    logger.info("🔍 DIAGNOSIS: Testing Redis connection independently...")
    
    try:
        import redis
        from backend.app.core.config import settings
        
        redis_url = settings.REDIS_URL
        logger.info(f"📍 Redis URL: {redis_url}")
        
        # Parse URL
        parsed = urlparse(redis_url)
        logger.info(f"📍 Scheme: {parsed.scheme}")
        logger.info(f"📍 Host: {parsed.hostname}")
        logger.info(f"📍 Port: {parsed.port}")
        
        # Test connection with timeout
        logger.info("🔌 Attempting Redis connection with 5s timeout...")
        start_time = time.time()
        
        if parsed.scheme == 'rediss':
            # SSL connection
            r = redis.from_url(
                redis_url,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                ssl_cert_reqs=None,
                ssl_check_hostname=False
            )
        else:
            # Non-SSL connection
            r = redis.from_url(redis_url, socket_timeout=5.0, socket_connect_timeout=5.0)
        
        # Test ping
        result = r.ping()
        elapsed = time.time() - start_time
        
        logger.info(f"✅ Redis connection successful! Ping: {result}, Time: {elapsed:.2f}s")
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Redis connection failed after {elapsed:.2f}s: {e}")
        return False

def test_celery_initialization():
    """Test Celery initialization separately"""
    logger.info("🔍 DIAGNOSIS: Testing Celery initialization...")
    
    try:
        # Set environment to disable Celery
        os.environ['DISABLE_CELERY_ON_STARTUP'] = 'true'
        logger.info("🚫 Disabled Celery for this test")
        
        start_time = time.time()
        from backend.app.core.celery_app import get_celery_app
        
        celery_app = get_celery_app()
        elapsed = time.time() - start_time
        
        logger.info(f"✅ Celery initialization successful (disabled mode): {elapsed:.2f}s")
        logger.info(f"📍 Celery app type: {type(celery_app)}")
        
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Celery initialization failed after {elapsed:.2f}s: {e}")
        return False

def test_celery_with_redis():
    """Test Celery with Redis enabled"""
    logger.info("🔍 DIAGNOSIS: Testing Celery with Redis enabled...")
    
    try:
        # Enable Celery
        os.environ['DISABLE_CELERY_ON_STARTUP'] = 'false'
        logger.info("🚀 Enabled Celery for this test")
        
        start_time = time.time()
        
        # Import fresh (clear any cached modules)
        import importlib
        if 'backend.app.core.celery_app' in sys.modules:
            importlib.reload(sys.modules['backend.app.core.celery_app'])
        
        from backend.app.core.celery_app import get_celery_app
        
        logger.info("📍 Calling get_celery_app()...")
        celery_app = get_celery_app()
        elapsed = time.time() - start_time
        
        logger.info(f"✅ Celery with Redis successful: {elapsed:.2f}s")
        logger.info(f"📍 Celery app type: {type(celery_app)}")
        
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Celery with Redis failed after {elapsed:.2f}s: {e}")
        return False

def test_worker_import():
    """Test importing worker.py (which triggers Celery initialization)"""
    logger.info("🔍 DIAGNOSIS: Testing worker.py import (main culprit)...")
    
    try:
        # Enable Celery
        os.environ['DISABLE_CELERY_ON_STARTUP'] = 'false'
        
        start_time = time.time()
        logger.info("📍 Importing worker.py...")
        
        # This is what happens during FastAPI startup
        from backend.app import worker
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Worker import successful: {elapsed:.2f}s")
        
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Worker import failed after {elapsed:.2f}s: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    logger.info("🚀 CELERY STARTUP DIAGNOSIS")
    logger.info("=" * 50)
    
    results = {}
    
    # Test 1: Redis connection
    results['redis'] = test_redis_connection()
    logger.info("")
    
    # Test 2: Celery disabled
    results['celery_disabled'] = test_celery_initialization()
    logger.info("")
    
    # Test 3: Celery with Redis
    results['celery_enabled'] = test_celery_with_redis()
    logger.info("")
    
    # Test 4: Worker import (the real issue)
    results['worker_import'] = test_worker_import()
    logger.info("")
    
    # Summary
    logger.info("📊 DIAGNOSIS SUMMARY")
    logger.info("=" * 50)
    for test, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{test}: {status}")
    
    # Conclusion
    logger.info("")
    logger.info("🎯 CONCLUSION:")
    if not results['redis']:
        logger.info("❌ Redis connection is the primary issue")
    elif not results['worker_import']:
        logger.info("❌ Worker import (Celery initialization) is blocking startup")
    else:
        logger.info("✅ All tests passed - issue may be elsewhere")

if __name__ == "__main__":
    main()