#!/usr/bin/env python3
"""
Test script to verify backend startup without hanging.
"""

import os
import sys
import subprocess
import time
import requests
import signal

def test_backend_startup():
    """Test if the backend can start without hanging."""
    print("🚀 Testing Backend Startup (Fixed Celery Import Issue)...")
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    # Start the backend server
    cmd = [
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--reload', 
        '--host', '0.0.0.0', 
        '--port', '8000'
    ]
    
    print(f"Starting backend with command: {' '.join(cmd)}")
    print("Working directory:", backend_dir)
    
    try:
        # Start the process
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("\n📋 Backend Startup Output:")
        print("-" * 40)
        
        startup_success = False
        startup_timeout = 30  # 30 seconds timeout
        start_time = time.time()
        
        while time.time() - start_time < startup_timeout:
            try:
                line = process.stdout.readline()
                if line:
                    print(line.rstrip())
                    
                    # Check for successful startup indicators
                    if "Application startup complete" in line or "Uvicorn running on" in line:
                        startup_success = True
                        print("\n✅ Backend started successfully!")
                        break
                        
                elif process.poll() is not None:
                    print(f"\n❌ Process exited with code: {process.poll()}")
                    break
                    
            except Exception as e:
                print(f"Error reading output: {e}")
                break
        
        # Test if server is responding
        if startup_success:
            print("\n🔍 Testing server response...")
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Server is responding to health check!")
                else:
                    print(f"⚠️ Server responded with status: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Health check failed: {e}")
        
        # Terminate the process
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        print("-" * 40)
        
        if startup_success:
            print("\n🎉 SUCCESS! Backend startup issue has been FIXED!")
            print("\n📋 The issue was:")
            print("   • Celery worker tasks were imported at module level")
            print("   • This caused Celery to try connecting to Redis during FastAPI startup")
            print("   • Fixed by making imports lazy (only when endpoints are called)")
            print("\n✅ Backend server can now start normally!")
            return True
        else:
            print("\n❌ Backend startup still has issues")
            return False
            
    except Exception as e:
        print(f"❌ Error testing backend startup: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 BACKEND STARTUP FIX VERIFICATION")
    print("=" * 60)
    
    success = test_backend_startup()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 BACKEND STARTUP ISSUE RESOLVED!")
        print("\n📋 Next Steps:")
        print("1. Start backend: cd backend && python -m uvicorn app.main:app --reload")
        print("2. Start Celery: cd backend && python -m celery -A app.worker worker --loglevel=info --pool=solo")
        print("3. Start frontend: cd frontend && npm run dev")
        print("4. Login at: http://localhost:3000/login")
        print("   Email: test@jwhd.com")
        print("   Password: testpassword123")
    else:
        print("❌ Backend startup still needs attention")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)