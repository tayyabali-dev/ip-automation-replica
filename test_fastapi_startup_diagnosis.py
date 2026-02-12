#!/usr/bin/env python3
"""
Diagnostic script to identify what's blocking FastAPI startup.
Tests each import and startup step individually.
"""

import os
import sys
import time
import logging

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_import_step(module_name, description):
    """Test importing a specific module with timing"""
    logger.info(f"🔍 Testing import: {description}")
    start_time = time.time()
    
    try:
        if module_name == "app.main":
            # Special case for main module
            from app import main
            result = main
        elif module_name == "app.api.api":
            from app.api import api
            result = api
        elif module_name == "app.worker":
            from app import worker
            result = worker
        elif module_name == "app.services.storage":
            from app.services import storage
            result = storage
        elif module_name == "app.services.llm":
            from app.services import llm
            result = llm
        elif module_name == "app.services.jobs":
            from app.services import jobs
            result = jobs
        elif module_name == "app.db.mongodb":
            from app.db import mongodb
            result = mongodb
        else:
            result = __import__(module_name)
        
        elapsed = time.time() - start_time
        logger.info(f"✅ {description}: {elapsed:.3f}s")
        return True, elapsed
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ {description} failed after {elapsed:.3f}s: {e}")
        return False, elapsed

def test_fastapi_creation():
    """Test FastAPI app creation"""
    logger.info("🔍 Testing FastAPI app creation...")
    start_time = time.time()
    
    try:
        from fastapi import FastAPI
        from app.core.config import settings
        
        app = FastAPI(
            title=settings.PROJECT_NAME,
            openapi_url=f"{settings.API_V1_STR}/openapi.json"
        )
        
        elapsed = time.time() - start_time
        logger.info(f"✅ FastAPI app creation: {elapsed:.3f}s")
        return True, elapsed
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ FastAPI app creation failed after {elapsed:.3f}s: {e}")
        return False, elapsed

def test_middleware_setup():
    """Test middleware setup"""
    logger.info("🔍 Testing middleware setup...")
    start_time = time.time()
    
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from app.core.config import settings
        
        app = FastAPI(title="Test")
        
        if settings.BACKEND_CORS_ORIGINS:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Middleware setup: {elapsed:.3f}s")
        return True, elapsed
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Middleware setup failed after {elapsed:.3f}s: {e}")
        return False, elapsed

def test_router_inclusion():
    """Test API router inclusion"""
    logger.info("🔍 Testing API router inclusion...")
    start_time = time.time()
    
    try:
        from fastapi import FastAPI
        from app.core.config import settings
        from app.api.api import api_router
        
        app = FastAPI(title="Test")
        app.include_router(api_router, prefix=settings.API_V1_STR)
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Router inclusion: {elapsed:.3f}s")
        return True, elapsed
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Router inclusion failed after {elapsed:.3f}s: {e}")
        return False, elapsed

def test_startup_events():
    """Test startup events"""
    logger.info("🔍 Testing startup events...")
    start_time = time.time()
    
    try:
        import asyncio
        from app.db.mongodb import connect_to_mongo
        from app.services.jobs import job_service
        
        async def test_startup():
            await connect_to_mongo()
            # Don't actually start cleanup task, just test the import
            
        asyncio.run(test_startup())
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Startup events: {elapsed:.3f}s")
        return True, elapsed
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Startup events failed after {elapsed:.3f}s: {e}")
        return False, elapsed

def main():
    """Run comprehensive FastAPI startup diagnosis"""
    logger.info("🚀 FASTAPI STARTUP DIAGNOSIS")
    logger.info("=" * 50)
    
    # Change to backend directory
    os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
    
    results = {}
    total_time = 0
    
    # Test individual imports in order
    import_tests = [
        ("app.core.config", "Core configuration"),
        ("app.core.logging", "Logging setup"),
        ("app.core.errors", "Error handlers"),
        ("app.db.mongodb", "MongoDB connection"),
        ("app.services.storage", "Storage service"),
        ("app.services.llm", "LLM service"),
        ("app.services.jobs", "Job service"),
        ("app.worker", "Worker module (Celery)"),
        ("app.api.api", "API router"),
        ("app.main", "Main FastAPI module"),
    ]
    
    for module, description in import_tests:
        success, elapsed = test_import_step(module, description)
        results[description] = success
        total_time += elapsed
        logger.info("")
    
    # Test FastAPI components
    component_tests = [
        ("fastapi_creation", test_fastapi_creation),
        ("middleware_setup", test_middleware_setup),
        ("router_inclusion", test_router_inclusion),
        ("startup_events", test_startup_events),
    ]
    
    for test_name, test_func in component_tests:
        success, elapsed = test_func()
        results[test_name] = success
        total_time += elapsed
        logger.info("")
    
    # Summary
    logger.info("📊 DIAGNOSIS SUMMARY")
    logger.info("=" * 50)
    for test, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{test}: {status}")
    
    logger.info(f"\n⏱️  Total time: {total_time:.3f}s")
    
    # Find the slowest component
    if total_time > 5.0:
        logger.info("⚠️  Startup is slow - check individual component times above")
    
    # Check for blocking issues
    failed_tests = [test for test, success in results.items() if not success]
    if failed_tests:
        logger.info(f"❌ Failed tests: {', '.join(failed_tests)}")
    else:
        logger.info("✅ All components loaded successfully")
        logger.info("🤔 Issue might be in uvicorn startup or event loop blocking")

if __name__ == "__main__":
    main()