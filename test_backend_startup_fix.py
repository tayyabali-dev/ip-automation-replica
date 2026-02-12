#!/usr/bin/env python3
"""
Test script to verify the backend startup fix works
"""
import subprocess
import time
import sys
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def test_backend_startup():
    """Test that the backend starts successfully without hanging"""
    print("🧪 TESTING BACKEND STARTUP FIX")
    print("=" * 60)
    
    backend_dir = os.path.join(os.getcwd(), 'backend')
    
    cmd = [
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--host', '0.0.0.0', 
        '--port', '8001'  # Use different port to avoid conflicts
    ]
    
    print(f"Starting backend server: {' '.join(cmd)}")
    print("Monitoring for successful startup...")
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        startup_success = False
        startup_logs = []
        start_time = time.time()
        
        # Monitor for 30 seconds
        while time.time() - start_time < 30:
            try:
                line = process.stdout.readline()
                if line:
                    print(line.rstrip())
                    startup_logs.append(line.strip())
                    
                    # Check for successful startup indicators
                    if "Application startup complete" in line or "Uvicorn running on" in line:
                        startup_success = True
                        print("✅ Backend startup completed successfully!")
                        break
                        
                elif process.poll() is not None:
                    print(f"Process exited with code: {process.poll()}")
                    break
                    
            except Exception as e:
                print(f"Error reading output: {e}")
                break
        
        # Test health endpoint if startup succeeded
        if startup_success:
            print("\n📋 Testing health endpoint...")
            try:
                time.sleep(2)  # Give server a moment to be ready
                response = requests.get("http://localhost:8001/health", timeout=10)
                if response.status_code == 200:
                    print("✅ Health endpoint responding correctly!")
                    health_data = response.json()
                    print(f"Health status: {health_data.get('status', 'unknown')}")
                else:
                    print(f"⚠️ Health endpoint returned status: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Could not test health endpoint: {e}")
        
        # Terminate server
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        return startup_success, startup_logs
        
    except Exception as e:
        print(f"❌ Error testing backend startup: {e}")
        return False, []

def analyze_startup_logs(logs):
    """Analyze startup logs for issues"""
    print("\n📊 STARTUP LOG ANALYSIS:")
    print("-" * 40)
    
    ssl_warnings = [log for log in logs if "ssl_cert_reqs=CERT_NONE" in log]
    celery_logs = [log for log in logs if "CELERY" in log]
    error_logs = [log for log in logs if "ERROR" in log or "Failed" in log]
    
    print(f"• SSL warnings found: {len(ssl_warnings)}")
    print(f"• Celery logs found: {len(celery_logs)}")
    print(f"• Error logs found: {len(error_logs)}")
    
    if ssl_warnings:
        print("\n⚠️ SSL warnings still present:")
        for warning in ssl_warnings[:3]:  # Show first 3
            print(f"   {warning}")
    
    if celery_logs:
        print("\n📋 Celery configuration logs:")
        for log in celery_logs[:5]:  # Show first 5
            print(f"   {log}")
    
    if error_logs:
        print("\n❌ Error logs found:")
        for error in error_logs:
            print(f"   {error}")

if __name__ == "__main__":
    print("🔧 BACKEND STARTUP FIX VERIFICATION")
    print("Testing that the backend starts without hanging")
    
    success, logs = test_backend_startup()
    
    if logs:
        analyze_startup_logs(logs)
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    if success:
        print("🎉 SUCCESS! Backend startup fix is working!")
        print("✅ The backend starts without hanging")
        print("✅ FastAPI application startup completes")
        print("✅ Server is ready to accept requests")
        
        print("\n📋 Next Steps:")
        print("1. Start backend: cd backend && python -m uvicorn app.main:app --reload")
        print("2. Start Celery worker: cd backend && python -m celery -A app.worker worker --loglevel=info --pool=solo")
        print("3. Start frontend: cd frontend && npm run dev")
        
    else:
        print("❌ Backend startup is still having issues")
        print("The fix may need additional adjustments")
    
    sys.exit(0 if success else 1)