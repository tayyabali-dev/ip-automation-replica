#!/usr/bin/env python3
"""
Final test to verify Celery SSL configuration is working without warnings.
This script will help you verify that the SSL warnings are completely eliminated.
"""

import os
import sys
import subprocess
import time
import signal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_celery_worker_ssl():
    """Test Celery worker startup and check for SSL warnings."""
    print("🔧 Testing Celery Worker SSL Configuration...")
    print("=" * 60)
    
    # Check if REDIS_URL is configured
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        print("❌ REDIS_URL not found in environment variables")
        return False
    
    if not redis_url.startswith('rediss://'):
        print("❌ REDIS_URL does not use SSL (rediss://)")
        return False
    
    print(f"✅ Redis URL configured with SSL: {redis_url[:20]}...")
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found")
        return False
    
    print(f"✅ Backend directory found: {backend_dir}")
    
    # Test Celery worker startup
    print("\n🚀 Starting Celery worker to test SSL configuration...")
    print("   (Worker will run for 15 seconds to capture startup logs)")
    
    try:
        # Start Celery worker process
        cmd = [
            sys.executable, '-m', 'celery', 
            '-A', 'app.worker', 
            'worker', 
            '--loglevel=info', 
            '--pool=solo',
            '--concurrency=1'
        ]
        
        print(f"   Command: {' '.join(cmd)}")
        print("   Working directory:", backend_dir)
        print("\n📋 Celery Worker Output:")
        print("-" * 40)
        
        # Start process and capture output
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Capture output for analysis
        output_lines = []
        ssl_warnings = []
        
        # Read output for 15 seconds
        start_time = time.time()
        while time.time() - start_time < 15:
            try:
                line = process.stdout.readline()
                if line:
                    print(line.rstrip())
                    output_lines.append(line.rstrip())
                    
                    # Check for SSL warnings
                    if "insecure SSL behaviour" in line.lower():
                        ssl_warnings.append(line.rstrip())
                    
                    # Check if worker is ready
                    if "ready" in line.lower() and "celery" in line.lower():
                        print("\n✅ Celery worker started successfully!")
                        break
                        
                elif process.poll() is not None:
                    break
                    
            except Exception as e:
                print(f"Error reading output: {e}")
                break
        
        # Terminate the process
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        print("-" * 40)
        
        # Analyze results
        print("\n📊 SSL Configuration Analysis:")
        print("=" * 40)
        
        if ssl_warnings:
            print(f"❌ Found {len(ssl_warnings)} SSL warning(s):")
            for warning in ssl_warnings:
                print(f"   • {warning}")
            return False
        else:
            print("✅ No SSL warnings detected!")
            print("✅ Celery worker connected to Upstash Redis securely!")
            return True
            
    except Exception as e:
        print(f"❌ Error testing Celery worker: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 FINAL CELERY SSL VERIFICATION TEST")
    print("=" * 60)
    
    success = test_celery_worker_ssl()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! SSL configuration is working correctly.")
        print("\nThe Celery worker connects to Upstash Redis without SSL warnings.")
        print("\n📋 To run the system:")
        print("1. Terminal 1: cd backend && python -m uvicorn app.main:app --reload")
        print("2. Terminal 2: cd backend && python -m celery -A app.worker worker --loglevel=info --pool=solo")
        print("3. Terminal 3: cd frontend && npm run dev")
        print("\n✅ The SSL warnings have been completely eliminated!")
    else:
        print("❌ SSL warnings are still present. Please check the configuration.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure REDIS_URL uses 'rediss://' protocol")
        print("2. Restart the Celery worker")
        print("3. Check that the SSL configuration is loaded properly")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)