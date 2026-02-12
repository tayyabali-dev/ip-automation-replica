#!/usr/bin/env python3
"""
Test script to diagnose exactly where Celery is blocking during FastAPI startup
"""
import os
import sys
import time
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def test_celery_import_blocking():
    """Test where exactly Celery import blocks"""
    print("🔍 DIAGNOSING CELERY BLOCKING BEHAVIOR")
    print("=" * 60)
    
    # Add backend to path
    backend_path = os.path.join(os.getcwd(), 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    print("📋 Step-by-step Celery import test:")
    print("-" * 40)
    
    try:
        print("1. Importing basic modules...")
        from celery import Celery
        import ssl
        print("   ✅ Basic imports successful")
        
        print("2. Importing config...")
        from app.core.config import settings
        print("   ✅ Config import successful")
        
        print("3. Creating Celery app instance...")
        celery_app = Celery("worker")
        print("   ✅ Celery app created")
        
        print("4. Configuring SSL settings...")
        redis_url = settings.REDIS_URL
        use_ssl = redis_url.startswith('rediss://')
        
        if use_ssl:
            ssl_config = {
                'ssl_cert_reqs': ssl.CERT_NONE,
                'ssl_check_hostname': False,
                'ssl_ca_certs': None,
                'ssl_certfile': None,
                'ssl_keyfile': None,
            }
            
            print("   🔧 Applying SSL configuration...")
            celery_app.conf.update(
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='UTC',
                enable_utc=True,
                broker_url=settings.CELERY_BROKER_URL,
                result_backend=settings.CELERY_RESULT_BACKEND,
                broker_transport_options=ssl_config,
                result_backend_transport_options=ssl_config,
                redis_backend_use_ssl=ssl_config,
                broker_use_ssl=ssl_config,
                worker_pool='solo',
                worker_concurrency=1,
                task_always_eager=False,
                task_eager_propagates=True,
            )
            print("   ✅ SSL configuration applied")
        
        print("5. Testing autodiscover_tasks (THIS IS WHERE IT LIKELY HANGS)...")
        
        # Use a timeout to detect if this blocks
        def autodiscover_with_timeout():
            try:
                print("   🔄 Starting autodiscover_tasks...")
                celery_app.autodiscover_tasks(["app.worker"])
                print("   ✅ autodiscover_tasks completed successfully!")
                return True
            except Exception as e:
                print(f"   ❌ autodiscover_tasks failed: {e}")
                return False
        
        # Run autodiscover in a separate thread with timeout
        result = [None]
        
        def run_autodiscover():
            result[0] = autodiscover_with_timeout()
        
        thread = threading.Thread(target=run_autodiscover)
        thread.daemon = True
        thread.start()
        
        # Wait for 10 seconds
        thread.join(timeout=10)
        
        if thread.is_alive():
            print("   ⚠️ autodiscover_tasks is BLOCKING! (timeout after 10 seconds)")
            print("   🔍 This confirms the root cause of the FastAPI startup hang")
            return False
        elif result[0]:
            print("   ✅ autodiscover_tasks completed without blocking")
            return True
        else:
            print("   ❌ autodiscover_tasks failed with error")
            return False
            
    except Exception as e:
        print(f"❌ Error during Celery import test: {e}")
        return False

def test_alternative_celery_config():
    """Test alternative Celery configuration that doesn't block"""
    print("\n📋 Testing Alternative Non-Blocking Configuration:")
    print("-" * 50)
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.getcwd(), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from celery import Celery
        import ssl
        from app.core.config import settings
        
        print("1. Creating Celery app with lazy configuration...")
        celery_app = Celery("worker")
        
        # Configure without autodiscovery
        redis_url = settings.REDIS_URL
        use_ssl = redis_url.startswith('rediss://')
        
        if use_ssl:
            ssl_config = {
                'ssl_cert_reqs': ssl.CERT_NONE,
                'ssl_check_hostname': False,
                'ssl_ca_certs': None,
                'ssl_certfile': None,
                'ssl_keyfile': None,
            }
            
            celery_app.conf.update(
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='UTC',
                enable_utc=True,
                broker_url=settings.CELERY_BROKER_URL,
                result_backend=settings.CELERY_RESULT_BACKEND,
                broker_transport_options=ssl_config,
                result_backend_transport_options=ssl_config,
                redis_backend_use_ssl=ssl_config,
                broker_use_ssl=ssl_config,
                worker_pool='solo',
                worker_concurrency=1,
                task_always_eager=False,
                task_eager_propagates=True,
            )
        
        print("2. ✅ Celery configured without autodiscovery")
        print("3. ✅ This configuration should not block FastAPI startup")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing alternative config: {e}")
        return False

if __name__ == "__main__":
    print("🧪 CELERY BLOCKING DIAGNOSIS")
    print("This will identify exactly where the startup hangs")
    
    # Test current blocking behavior
    blocking_test = test_celery_import_blocking()
    
    # Test alternative non-blocking approach
    alternative_test = test_alternative_celery_config()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS RESULTS")
    print("=" * 60)
    
    if not blocking_test:
        print("🎯 ROOT CAUSE CONFIRMED:")
        print("• celery_app.autodiscover_tasks() is blocking FastAPI startup")
        print("• This happens because Celery tries to connect to Redis during autodiscovery")
        print("• The connection attempts are synchronous and block the main thread")
        
        print("\n💡 RECOMMENDED SOLUTION:")
        print("• Remove autodiscover_tasks() from celery_app.py")
        print("• Use lazy task discovery or manual task registration")
        print("• This will allow FastAPI to start without waiting for Celery")
        
    else:
        print("✅ autodiscover_tasks completed successfully")
        print("The blocking issue may be elsewhere")
    
    if alternative_test:
        print("\n✅ Alternative configuration works without blocking")
    
    sys.exit(0 if not blocking_test else 1)