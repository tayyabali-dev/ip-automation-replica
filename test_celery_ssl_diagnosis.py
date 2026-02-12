#!/usr/bin/env python3
"""
Test script to diagnose Celery SSL warnings with Upstash Redis.
This will help us understand exactly when and why the SSL warnings appear.
"""

import os
import sys
import subprocess
import time
import logging

# Set up logging to capture all output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_celery_ssl_diagnosis():
    """Test Celery SSL configuration and capture warnings."""
    print("🔍 DIAGNOSING CELERY SSL WARNINGS")
    print("=" * 60)
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    # Test 1: Import Celery app directly
    print("\n📋 Test 1: Direct Celery App Import")
    print("-" * 40)
    
    try:
        # Change to backend directory for proper imports
        original_cwd = os.getcwd()
        os.chdir(backend_dir)
        sys.path.insert(0, backend_dir)
        
        # Import the celery app - this should trigger any SSL warnings
        print("Importing Celery app...")
        from app.core.celery_app import celery_app
        print("✅ Celery app imported successfully")
        
        # Check configuration
        print(f"Broker URL: {celery_app.conf.broker_url}")
        print(f"Result Backend: {celery_app.conf.result_backend}")
        print(f"Broker Transport Options: {celery_app.conf.broker_transport_options}")
        
    except Exception as e:
        print(f"❌ Error importing Celery app: {e}")
        return False
    finally:
        os.chdir(original_cwd)
        if backend_dir in sys.path:
            sys.path.remove(backend_dir)
    
    # Test 2: Start Celery worker briefly
    print("\n📋 Test 2: Celery Worker Startup")
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
        
        print("\n📋 Celery Worker Output:")
        print("-" * 30)
        
        # Capture output for 10 seconds
        start_time = time.time()
        ssl_warnings_found = []
        
        while time.time() - start_time < 10:
            try:
                line = process.stdout.readline()
                if line:
                    print(line.rstrip())
                    
                    # Look for SSL warnings
                    if "ssl_cert_reqs=CERT_NONE" in line:
                        ssl_warnings_found.append(line.strip())
                    
                    # Look for successful startup
                    if "ready" in line.lower() or "connected" in line.lower():
                        print("✅ Worker appears to be starting successfully")
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
        
        print("-" * 30)
        
        # Analyze results
        if ssl_warnings_found:
            print(f"\n⚠️ Found {len(ssl_warnings_found)} SSL warnings:")
            for warning in ssl_warnings_found:
                print(f"   • {warning}")
            return ssl_warnings_found
        else:
            print("\n✅ No SSL warnings detected!")
            return []
            
    except Exception as e:
        print(f"❌ Error testing Celery worker: {e}")
        return False

def main():
    """Main diagnosis function."""
    print("🧪 CELERY SSL DIAGNOSIS")
    print("This will help identify the exact source of SSL warnings")
    
    warnings = test_celery_ssl_diagnosis()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS RESULTS")
    print("=" * 60)
    
    if warnings is False:
        print("❌ Diagnosis failed due to errors")
        return False
    elif warnings:
        print("🔍 SSL WARNINGS DETECTED:")
        print("\n📋 Analysis:")
        print("• The warnings appear during Celery worker initialization")
        print("• This suggests the SSL configuration is not being applied early enough")
        print("• The warnings are likely from the redis-py library itself")
        
        print("\n💡 RECOMMENDED FIXES:")
        print("1. Suppress the specific warning using Python warnings module")
        print("2. Update redis-py library to latest version")
        print("3. Use alternative SSL configuration approach")
        
        return True
    else:
        print("✅ NO SSL WARNINGS FOUND!")
        print("The configuration appears to be working correctly.")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)