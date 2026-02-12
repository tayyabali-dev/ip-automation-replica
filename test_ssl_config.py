#!/usr/bin/env python3
"""
Test script to verify SSL configuration for Upstash Redis connection.
This script tests the Celery SSL configuration without warnings.
"""

import os
import sys
import ssl
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv()

def test_ssl_config():
    """Test the SSL configuration for Redis connection."""
    print("🔧 Testing SSL Configuration for Upstash Redis...")
    
    # Import after path setup
    from app.core.celery_app import celery_app
    
    # Check if Redis URL is configured
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        print("❌ REDIS_URL not found in environment variables")
        return False
    
    print(f"✅ Redis URL configured: {redis_url[:20]}...")
    
    # Check SSL configuration
    broker_transport_options = celery_app.conf.broker_transport_options
    result_backend_transport_options = celery_app.conf.redis_backend_use_ssl
    
    print("\n📋 Broker Transport Options:")
    for key, value in broker_transport_options.items():
        print(f"  {key}: {value}")
    
    print("\n📋 Result Backend SSL Options:")
    for key, value in result_backend_transport_options.items():
        print(f"  {key}: {value}")
    
    # Verify SSL settings are correct
    expected_ssl_settings = {
        'ssl_cert_reqs': ssl.CERT_NONE,
        'ssl_check_hostname': False,
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    }
    
    print("\n🔍 Verifying SSL Configuration...")
    for key, expected_value in expected_ssl_settings.items():
        broker_value = broker_transport_options.get(key)
        backend_value = result_backend_transport_options.get(key)
        
        if broker_value == expected_value and backend_value == expected_value:
            print(f"  ✅ {key}: {expected_value}")
        else:
            print(f"  ❌ {key}: Expected {expected_value}, got broker={broker_value}, backend={backend_value}")
            return False
    
    print("\n🎉 SSL configuration is correct!")
    print("The Celery worker should now connect to Upstash Redis without SSL warnings.")
    return True

if __name__ == "__main__":
    success = test_ssl_config()
    if success:
        print("\n✅ SSL configuration test completed successfully!")
        print("\nTo test the Celery worker:")
        print("1. cd backend")
        print("2. celery -A app.worker worker --loglevel=info")
        print("\nYou should no longer see 'insecure SSL behaviour' warnings.")
    else:
        print("\n❌ SSL configuration test failed.")
        print("Please check your REDIS_URL and environment configuration.")
    
    sys.exit(0 if success else 1)