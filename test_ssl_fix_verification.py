#!/usr/bin/env python3
"""
Test script to verify that the SSL warnings have been fixed.
"""

import os
import sys
import subprocess
import time

def test_ssl_fix():
    """Test that SSL warnings are no longer appearing."""
    print("🧪 TESTING SSL WARNING FIX")
    print("=" * 60)
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    # Test 1: Import Celery app (should be clean now)
    print("\n📋 Test 1: Clean Celery App Import")
    print("-" * 40)
    
    try:
        original_cwd = os.getcwd()
        os.chdir(backend_dir)
        sys.path.insert(0, backend_dir)
        
        print("Importing Celery app with SSL warning suppression...")
        from app.core.celery_app import celery_app
        print("✅ Celery app imported successfully")
        
    except Exception as e:
        print(f"❌ Error importing Celery app: {e}")
        return False
    finally:
        os.chdir(original_cwd)
        if backend_dir in sys.path:
            sys.path.remove(backend_dir)
    
    # Test 2: Start Celery worker and check for warnings
    print("\n📋 Test 2: Celery Worker Startup (SSL Warning Check)")
    print("-" * 40)
    
    cmd = [
        sys.executable, '-m', 'celery', 
        '-A', 'app.worker', 
        'worker', 
        '--loglevel=info',
        '--pool=solo',
        '--concurrency=1'
    ]
    
    print(f"Starting Celery worker: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        print("\n📋 Celery Worker Output (Monitoring for SSL warnings):")
        print("-" * 50)
        
        ssl_warnings_found = []
        worker_started = False
        start_time = time.time()
        
        while time.time() - start_time < 15:  # Monitor for 15 seconds
            try:
                line = process.stdout.readline()
                if line:
                    print(line.rstrip())
                    
                    # Check for SSL warnings
                    if "ssl_cert_reqs=CERT_NONE" in line:
                        ssl_warnings_found.append(line.strip())
                    
                    # Check for successful startup
                    if "Connected to rediss://" in line:
                        worker_started = True
                        print("✅ Worker connected to Redis successfully!")
                        break
                        
                elif process.poll() is not None:
                    print(f"Process exited with code: {process.poll()}")
                    break
                    
            except Exception as e:
                print(f"Error reading output: {e}")
                break
        
        # Terminate worker
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        print("-" * 50)
        
        # Analyze results
        if ssl_warnings_found:
            print(f"\n❌ STILL FOUND {len(ssl_warnings_found)} SSL WARNINGS:")
            for warning in ssl_warnings_found:
                print(f"   • {warning}")
            return False
        elif worker_started:
            print("\n🎉 SUCCESS! No SSL warnings detected and worker started successfully!")
            return True
        else:
            print("\n⚠️ Worker didn't start properly, but no SSL warnings detected")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Celery worker: {e}")
        return False

def test_backend_startup():
    """Test that the backend starts without SSL warnings."""
    print("\n📋 Test 3: Backend Server Startup")
    print("-" * 40)
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    cmd = [
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--host', '0.0.0.0', 
        '--port', '8000'
    ]
    
    print(f"Starting backend server: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        ssl_warnings_found = []
        server_started = False
        start_time = time.time()
        
        while time.time() - start_time < 20:  # Monitor for 20 seconds
            try:
                line = process.stdout.readline()
                if line:
                    print(line.rstrip())
                    
                    # Check for SSL warnings
                    if "ssl_cert_reqs=CERT_NONE" in line:
                        ssl_warnings_found.append(line.strip())
                    
                    # Check for successful startup
                    if "Application startup complete" in line or "Uvicorn running on" in line:
                        server_started = True
                        print("✅ Backend server started successfully!")
                        break
                        
                elif process.poll() is not None:
                    print(f"Process exited with code: {process.poll()}")
                    break
                    
            except Exception as e:
                print(f"Error reading output: {e}")
                break
        
        # Terminate server
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        if ssl_warnings_found:
            print(f"\n❌ Found SSL warnings in backend startup:")
            for warning in ssl_warnings_found:
                print(f"   • {warning}")
            return False
        elif server_started:
            print("\n✅ Backend started successfully without SSL warnings!")
            return True
        else:
            print("\n⚠️ Backend startup issue (not SSL related)")
            return False
            
    except Exception as e:
        print(f"❌ Error testing backend startup: {e}")
        return False

def main():
    """Main verification function."""
    print("🔧 SSL WARNING FIX VERIFICATION")
    print("Testing that SSL warnings have been suppressed")
    
    # Test Celery worker
    celery_success = test_ssl_fix()
    
    # Test backend server
    backend_success = test_backend_startup()
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION RESULTS")
    print("=" * 60)
    
    if celery_success and backend_success:
        print("🎉 SUCCESS! SSL warnings have been FIXED!")
        print("\n✅ Results:")
        print("• Celery worker starts without SSL warnings")
        print("• Backend server starts without SSL warnings")
        print("• System is ready for normal operation")
        
        print("\n📋 Next Steps:")
        print("1. Start backend: cd backend && python -m uvicorn app.main:app --reload")
        print("2. Start Celery: cd backend && python -m celery -A app.worker worker --loglevel=info --pool=solo")
        print("3. Start frontend: cd frontend && npm run dev")
        
        return True
    else:
        print("❌ SSL warnings still present or other startup issues detected")
        print(f"• Celery test: {'✅ PASSED' if celery_success else '❌ FAILED'}")
        print(f"• Backend test: {'✅ PASSED' if backend_success else '❌ FAILED'}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)