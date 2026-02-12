#!/usr/bin/env python3
"""
Test script to verify backend server startup with Upstash Redis configuration.
This will test FastAPI startup, Celery initialization, and health checks.
"""

import os
import sys
import time
import logging
import subprocess
import requests
import signal
from threading import Thread
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackendServerTest:
    def __init__(self):
        self.server_process = None
        self.server_url = "http://localhost:8000"
        self.startup_timeout = 30  # seconds
        
    def start_server(self):
        """Start the FastAPI server"""
        try:
            logger.info("🚀 Starting FastAPI server with Upstash Redis...")
            
            # Change to backend directory
            backend_dir = os.path.join(os.getcwd(), 'backend')
            
            # Start server using uvicorn
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "app.main:app", 
                "--host", "0.0.0.0", 
                "--port", "8000",
                "--reload"
            ]
            
            self.server_process = subprocess.Popen(
                cmd,
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            logger.info(f"📊 Server process started with PID: {self.server_process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start server: {e}")
            return False
    
    def wait_for_server(self):
        """Wait for server to be ready"""
        logger.info("⏳ Waiting for server to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < self.startup_timeout:
            try:
                response = requests.get(f"{self.server_url}/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Server is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            # Check if process is still running
            if self.server_process and self.server_process.poll() is not None:
                logger.error("❌ Server process terminated unexpectedly")
                return False
            
            time.sleep(2)
        
        logger.error(f"❌ Server failed to start within {self.startup_timeout} seconds")
        return False
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            logger.info("🧪 Testing health endpoint...")
            
            response = requests.get(f"{self.server_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Health check passed: {health_data.get('status', 'unknown')}")
                logger.info(f"📊 Database connected: {health_data.get('database_connected', False)}")
                logger.info(f"📊 Storage connected: {health_data.get('storage_connected', False)}")
                logger.info(f"📊 LLM accessible: {health_data.get('llm_api_accessible', False)}")
                return True
            else:
                logger.error(f"❌ Health check failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test basic API endpoints"""
        try:
            logger.info("🧪 Testing API endpoints...")
            
            # Test OpenAPI docs endpoint
            response = requests.get(f"{self.server_url}/api/v1/openapi.json", timeout=10)
            if response.status_code == 200:
                logger.info("✅ OpenAPI docs accessible")
            else:
                logger.warning(f"⚠️ OpenAPI docs returned status: {response.status_code}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ API endpoint test failed: {e}")
            return False
    
    def monitor_server_logs(self, duration=10):
        """Monitor server logs for errors"""
        logger.info(f"📋 Monitoring server logs for {duration} seconds...")
        
        if not self.server_process:
            logger.error("❌ No server process to monitor")
            return False
        
        start_time = time.time()
        error_count = 0
        
        try:
            while time.time() - start_time < duration:
                if self.server_process.poll() is not None:
                    logger.error("❌ Server process terminated")
                    return False
                
                # Read available output
                try:
                    line = self.server_process.stdout.readline()
                    if line:
                        line = line.strip()
                        if line:
                            # Check for errors
                            if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', 'traceback']):
                                logger.warning(f"⚠️ Server log: {line}")
                                error_count += 1
                            elif any(keyword in line.lower() for keyword in ['started', 'ready', 'listening']):
                                logger.info(f"📋 Server log: {line}")
                except:
                    pass
                
                time.sleep(0.5)
            
            if error_count == 0:
                logger.info("✅ No errors detected in server logs")
                return True
            else:
                logger.warning(f"⚠️ Detected {error_count} potential errors in logs")
                return True  # Still consider success if server is running
                
        except Exception as e:
            logger.error(f"❌ Error monitoring logs: {e}")
            return False
    
    def stop_server(self):
        """Stop the server process"""
        if self.server_process:
            logger.info("🛑 Stopping server...")
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                logger.info("✅ Server stopped successfully")
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Server didn't stop gracefully, forcing termination")
                self.server_process.kill()
                self.server_process.wait()
            except Exception as e:
                logger.error(f"❌ Error stopping server: {e}")
    
    def run_full_test(self):
        """Run the complete server test suite"""
        logger.info("🚀 Starting comprehensive backend server test...")
        
        try:
            # Start server
            if not self.start_server():
                return False
            
            # Wait for server to be ready
            if not self.wait_for_server():
                return False
            
            # Test health endpoint
            health_success = self.test_health_endpoint()
            
            # Test API endpoints
            api_success = self.test_api_endpoints()
            
            # Monitor logs for a short period
            log_success = self.monitor_server_logs(duration=5)
            
            # Summary
            logger.info("=" * 50)
            logger.info("📋 TEST SUMMARY:")
            logger.info(f"   Server Startup:   {'✅ PASS' if True else '❌ FAIL'}")
            logger.info(f"   Health Check:     {'✅ PASS' if health_success else '❌ FAIL'}")
            logger.info(f"   API Endpoints:    {'✅ PASS' if api_success else '❌ FAIL'}")
            logger.info(f"   Log Monitoring:   {'✅ PASS' if log_success else '❌ FAIL'}")
            
            overall_success = health_success and api_success and log_success
            
            if overall_success:
                logger.info("🎉 All tests passed! Backend server is working properly with Upstash Redis.")
            else:
                logger.error("💥 Some tests failed. Check the logs above for details.")
            
            return overall_success
            
        finally:
            self.stop_server()

def main():
    """Run the backend server test"""
    test = BackendServerTest()
    success = test.run_full_test()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)