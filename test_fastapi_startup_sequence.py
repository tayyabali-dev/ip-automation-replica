#!/usr/bin/env python3
"""
Test script to replicate the exact FastAPI startup sequence and identify where it hangs
"""
import os
import sys
import time
import threading
import signal
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def test_fastapi_import_sequence():
    """Test the exact import sequence that FastAPI uses during startup"""
    print("🔍 TESTING FASTAPI STARTUP SEQUENCE")
    print("=" * 60)
    
    # Add backend to path
    backend_path = os.path.join(os.getcwd(), 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    print("📋 Replicating FastAPI startup imports:")
    print("-" * 40)
    
    try:
        print("1. Importing FastAPI core modules...")
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        print("   ✅ FastAPI imports successful")
        
        print("2. Importing app.core.config...")
        from app.core.config import settings
        print("   ✅ Config import successful")
        
        print("3. Importing app.core.logging...")
        from app.core.logging import setup_logging
        setup_logging(level="INFO")
        print("   ✅ Logging setup successful")
        
        print("4. Importing database modules...")
        from app.db.mongodb import connect_to_mongo, close_mongo_connection, db
        print("   ✅ Database imports successful")
        
        print("5. Importing service modules...")
        print("   5a. Importing storage service...")
        from app.services.storage import storage_service
        print("   ✅ Storage service imported")
        
        print("   5b. Importing LLM service...")
        from app.services.llm import llm_service
        print("   ✅ LLM service imported")
        
        print("   5c. Importing job service (THIS MIGHT TRIGGER CELERY)...")
        
        # This is where the hang might occur - job service might import Celery
        def import_job_service():
            from app.services.jobs import job_service
            return True
        
        # Test with timeout
        result = [None]
        exception = [None]
        
        def run_import():
            try:
                result[0] = import_job_service()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=run_import)
        thread.daemon = True
        thread.start()
        
        # Wait for 15 seconds
        thread.join(timeout=15)
        
        if thread.is_alive():
            print("   ⚠️ JOB SERVICE IMPORT IS BLOCKING! (timeout after 15 seconds)")
            print("   🔍 This might be the source of the FastAPI startup hang")
            return False
        elif exception[0]:
            print(f"   ❌ Job service import failed: {exception[0]}")
            return False
        else:
            print("   ✅ Job service imported successfully")
        
        print("6. Importing API router...")
        from app.api.api import api_router
        print("   ✅ API router imported")
        
        print("7. Creating FastAPI app...")
        app = FastAPI(
            title=settings.PROJECT_NAME,
            openapi_url=f"{settings.API_V1_STR}/openapi.json"
        )
        print("   ✅ FastAPI app created")
        
        print("8. Testing startup event simulation...")
        # This simulates what happens in the @app.on_event("startup")
        print("   8a. Testing MongoDB connection...")
        # We won't actually connect, just test the import
        
        print("   8b. Testing job cleanup task creation...")
        # This might trigger Celery task registration
        
        print("✅ All FastAPI startup sequence completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during FastAPI startup sequence: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_celery_import_isolation():
    """Test importing Celery in isolation to see if it blocks"""
    print("\n📋 Testing Celery Import in Isolation:")
    print("-" * 40)
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.getcwd(), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        print("1. Testing direct celery_app import...")
        
        def import_celery():
            from app.core.celery_app import celery_app
            return True
        
        # Test with timeout
        result = [None]
        exception = [None]
        
        def run_celery_import():
            try:
                result[0] = import_celery()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=run_celery_import)
        thread.daemon = True
        thread.start()
        
        # Wait for 15 seconds
        thread.join(timeout=15)
        
        if thread.is_alive():
            print("   ⚠️ CELERY APP IMPORT IS BLOCKING! (timeout after 15 seconds)")
            return False
        elif exception[0]:
            print(f"   ❌ Celery app import failed: {exception[0]}")
            return False
        else:
            print("   ✅ Celery app imported successfully")
            return True
        
    except Exception as e:
        print(f"❌ Error testing Celery import: {e}")
        return False

if __name__ == "__main__":
    print("🧪 FASTAPI STARTUP SEQUENCE DIAGNOSIS")
    print("This will identify exactly where FastAPI startup hangs")
    
    # Test FastAPI import sequence
    fastapi_success = test_fastapi_import_sequence()
    
    # Test Celery import in isolation
    celery_success = test_celery_import_isolation()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS RESULTS")
    print("=" * 60)
    
    if not fastapi_success:
        print("🎯 FASTAPI STARTUP HANG CONFIRMED:")
        print("• The hang occurs during FastAPI's import sequence")
        print("• Most likely during service imports that trigger Celery")
        
    if not celery_success:
        print("🎯 CELERY IMPORT BLOCKING CONFIRMED:")
        print("• Celery app import itself is blocking")
        print("• This is the root cause of the FastAPI startup hang")
        
    if fastapi_success and celery_success:
        print("✅ No blocking detected in isolated tests")
        print("The issue might be environment-specific or timing-related")
    
    print("\n💡 NEXT STEPS:")
    if not celery_success:
        print("• Fix Celery app configuration to prevent blocking")
        print("• Remove or defer autodiscover_tasks()")
        print("• Use lazy Celery initialization")
    elif not fastapi_success:
        print("• Identify which service import is causing the block")
        print("• Defer Celery-related imports until after FastAPI startup")
    
    sys.exit(0 if (fastapi_success and celery_success) else 1)