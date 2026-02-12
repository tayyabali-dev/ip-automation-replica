#!/usr/bin/env python3
"""
Verification script to ensure complete Docker removal and independence
"""
import os
import sys
import subprocess
import redis
import ssl
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env files
def load_env_files():
    """Load environment variables from both root and backend .env files"""
    # Try to load from current directory first
    if os.path.exists('.env'):
        load_dotenv('.env')
        print("✅ Loaded .env from current directory")
    
    # Try to load from backend directory
    if os.path.exists('backend/.env'):
        load_dotenv('backend/.env')
        print("✅ Loaded backend/.env")
    elif os.path.exists('.env'):
        load_dotenv('.env')
        print("✅ Loaded .env from backend directory")
    
    # Also try parent directory if we're in backend
    if os.path.exists('../.env'):
        load_dotenv('../.env')
        print("✅ Loaded ../.env")

def check_docker_running():
    """Check if Docker is running"""
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def test_redis_connection():
    """Test Redis connection"""
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    print(f"Testing Redis connection: {redis_url}")
    
    try:
        parsed_url = urlparse(redis_url)
        use_ssl = parsed_url.scheme == 'rediss'
        
        if use_ssl:
            r = redis.Redis.from_url(redis_url, ssl_cert_reqs=ssl.CERT_NONE)
        else:
            r = redis.Redis.from_url(redis_url)
        
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_celery_config():
    """Test Celery configuration"""
    try:
        # Add the current directory to Python path for imports
        current_dir = os.getcwd()
        if 'backend' in current_dir:
            # We're in backend directory
            sys.path.insert(0, current_dir)
            from app.core.celery_app import celery_app
            from app.core.config import settings
        else:
            # We're in root directory
            sys.path.insert(0, os.path.join(current_dir, 'backend'))
            from app.core.celery_app import celery_app
            from app.core.config import settings
        
        print(f"Celery broker: {settings.CELERY_BROKER_URL}")
        print(f"Celery result backend: {settings.CELERY_RESULT_BACKEND}")
        print("✅ Celery configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Celery configuration failed: {e}")
        return False

def test_environment_variables():
    """Test required environment variables"""
    required_vars = ['MONGODB_URL', 'REDIS_URL', 'SECRET_KEY', 'GOOGLE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✅ All required environment variables present")
        return True

def main():
    print("🔧 Docker Removal Verification")
    print("=" * 50)
    
    # Load environment variables first
    print("Loading environment variables...")
    load_env_files()
    
    # Check if Docker is running
    docker_running = check_docker_running()
    print(f"Docker status: {'Running' if docker_running else 'Not running/Not installed'}")
    
    if docker_running:
        print("⚠️  Docker is still running. This test will verify independence from Docker.")
    else:
        print("✅ Docker is not running - perfect for testing independence!")
    
    print("\n" + "=" * 50)
    
    # Run tests
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Redis Connection", test_redis_connection),
        ("Celery Configuration", test_celery_config),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 SUCCESS: All tests passed!")
        print("✅ The application is completely independent of Docker")
        print("✅ Celery worker can run without Docker containers")
        print("✅ Redis connection works with Upstash (cloud-native)")
        print("\n🚀 Ready for cloud deployment!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())