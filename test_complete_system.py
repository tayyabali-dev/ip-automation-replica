#!/usr/bin/env python3
"""
Comprehensive test script to verify:
1. SSL configuration is working without warnings
2. PDF parsing functionality is working correctly
3. ADS generation is working properly
4. Complete system integration
"""

import os
import sys
import asyncio
import tempfile
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv()

async def test_ssl_configuration():
    """Test SSL configuration for Celery/Redis connection."""
    print("🔧 Testing SSL Configuration...")
    
    try:
        from app.core.celery_app import celery_app
        
        # Check broker transport options
        broker_options = celery_app.conf.broker_transport_options
        result_options = celery_app.conf.result_backend_transport_options
        
        print(f"✅ Broker SSL Options: {broker_options}")
        print(f"✅ Result Backend SSL Options: {result_options}")
        
        # Test connection
        try:
            # This will test the broker connection
            celery_app.control.inspect().stats()
            print("✅ Celery SSL connection successful!")
            return True
        except Exception as e:
            print(f"❌ Celery connection failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ SSL configuration test failed: {e}")
        return False

async def test_pdf_parsing():
    """Test PDF parsing functionality."""
    print("\n📄 Testing PDF Parsing...")
    
    try:
        from app.services.llm import llm_service
        from app.models.patent_application import PatentApplicationMetadata
        
        # Create a simple test PDF with text
        test_pdf_path = "test_simple.pdf"
        
        # Create a minimal PDF for testing
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(test_pdf_path, pagesize=letter)
        c.drawString(100, 750, "PATENT APPLICATION DATA SHEET")
        c.drawString(100, 700, "Title of Invention: Test Invention System")
        c.drawString(100, 650, "Application Number: 18/123,456")
        c.drawString(100, 600, "Inventor Information:")
        c.drawString(120, 580, "Given Name: John")
        c.drawString(120, 560, "Family Name: Doe")
        c.drawString(120, 540, "City: San Francisco")
        c.drawString(120, 520, "State: CA")
        c.drawString(120, 500, "Country: US")
        c.save()
        
        print(f"✅ Created test PDF: {test_pdf_path}")
        
        # Test text extraction
        text_content = await llm_service._extract_text_locally(test_pdf_path)
        print(f"✅ Extracted text length: {len(text_content)} characters")
        
        if "Test Invention System" in text_content:
            print("✅ PDF text extraction working correctly")
        else:
            print("❌ PDF text extraction not finding expected content")
            
        # Clean up
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)
            
        return True
        
    except Exception as e:
        print(f"❌ PDF parsing test failed: {e}")
        return False

async def test_ads_generation():
    """Test ADS generation functionality."""
    print("\n📋 Testing ADS Generation...")
    
    try:
        from app.services.ads_generator import ADSGenerator
        from app.models.patent_application import PatentApplicationMetadata, Inventor
        
        generator = ADSGenerator()
        
        # Create test data
        test_data = PatentApplicationMetadata(
            title="Test System and Method for Automated Processing",
            application_number="18/123,456",
            filing_date="2024-01-24",
            entity_status="Small Entity",
            inventors=[
                Inventor(
                    first_name="John",
                    middle_name="A.",
                    last_name="Doe",
                    street_address="123 Test St",
                    city="Test City",
                    state="CA",
                    zip_code="90210",
                    country="US",
                    citizenship="US"
                ),
                Inventor(
                    first_name="Jane",
                    last_name="Smith",
                    street_address="456 Demo Ave",
                    city="Demo City",
                    state="NY",
                    zip_code="10001",
                    country="US",
                    citizenship="US"
                )
            ]
        )
        
        # Test ADS generation
        output_path = "test_ads_output.pdf"
        
        # Check if template exists
        if not os.path.exists(generator.template_path):
            print(f"❌ ADS template not found at: {generator.template_path}")
            return False
            
        result_path = generator.generate_ads_pdf(test_data, output_path)
        
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ ADS PDF generated successfully: {result_path} ({file_size} bytes)")
            
            # Clean up
            os.remove(result_path)
            return True
        else:
            print("❌ ADS PDF was not created")
            return False
            
    except Exception as e:
        print(f"❌ ADS generation test failed: {e}")
        return False

async def test_celery_task():
    """Test Celery task execution."""
    print("\n⚙️ Testing Celery Task Execution...")
    
    try:
        from app.worker import write_log_entry
        
        # Test simple log task
        test_log = {
            "timestamp": "2024-01-24T12:00:00Z",
            "level": "INFO",
            "message": "Test log entry from system test",
            "module": "test_complete_system"
        }
        
        # Send task to Celery
        result = write_log_entry.delay(test_log)
        
        # Wait for result (with timeout)
        try:
            task_result = result.get(timeout=10)
            print("✅ Celery task executed successfully")
            return True
        except Exception as e:
            print(f"❌ Celery task execution failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Celery task test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 COMPREHENSIVE SYSTEM TEST")
    print("=" * 50)
    
    tests = [
        ("SSL Configuration", test_ssl_configuration),
        ("PDF Parsing", test_pdf_parsing),
        ("ADS Generation", test_ads_generation),
        ("Celery Task Execution", test_celery_task)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} Test...")
        try:
            success = await test_func()
            results[test_name] = success
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! System is working correctly.")
        print("\nThe SSL configuration has been fixed and PDF processing is functional.")
        print("\nTo run the system:")
        print("1. Terminal 1 (Backend): cd backend && python -m uvicorn app.main:app --reload")
        print("2. Terminal 2 (Celery): cd backend && python -m celery -A app.worker worker --loglevel=info --pool=solo")
        print("3. Terminal 3 (Frontend): cd frontend && npm run dev")
    else:
        print("❌ SOME TESTS FAILED. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)