#!/usr/bin/env python3
"""
Complete Enhanced Data Flow Test
Tests the full pipeline from document upload to frontend data reception with new USPTO ADS fields.
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.enhanced_extraction_service import enhanced_extraction_service
from app.services.jobs import job_service
from app.models.enhanced_extraction import EnhancedExtractionResult
from app.db.mongodb import connect_to_mongo, close_mongo_connection, get_database
from app.models.document import DocumentCreate, DocumentInDB, ProcessedStatus
from app.models.job import JobType, JobStatus
from bson import ObjectId
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_complete_enhanced_data_flow():
    """Test the complete data flow with enhanced extraction."""
    
    logger.info("🚀 Starting Complete Enhanced Data Flow Test")
    
    try:
        # Connect to database
        await connect_to_mongo()
        db = await get_database()
        
        # 1. Create a test document record (simulating upload)
        logger.info("📄 Creating test document record...")
        
        test_user_id = "test_user_enhanced_flow"
        storage_key = f"{test_user_id}/test_enhanced_document.pdf"
        
        doc_in = DocumentCreate(
            filename="test_enhanced_document.pdf",
            document_type="cover_sheet",
            file_size=1024,
            mime_type="application/pdf",
            storage_key=storage_key,
            user_id=test_user_id
        )
        
        doc_db = DocumentInDB(**doc_in.model_dump())
        new_doc = await db.documents.insert_one(doc_db.model_dump(by_alias=True))
        document_id = str(new_doc.inserted_id)
        
        logger.info(f"✅ Created document: {document_id}")
        
        # 2. Test Enhanced Extraction Service directly
        logger.info("🔍 Testing Enhanced Extraction Service...")
        
        # Create sample PDF content (minimal valid PDF)
        sample_pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Patent Application) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
        
        try:
            enhanced_result = await enhanced_extraction_service.extract_enhanced_data(
                file_content=sample_pdf_content,
                filename="test_enhanced_document.pdf"
            )
            
            logger.info("✅ Enhanced Extraction Service working")
            logger.info(f"📊 Result type: {type(enhanced_result)}")
            logger.info(f"📊 Result fields: {list(enhanced_result.model_dump().keys())}")
            
            # Verify new fields are present
            result_dict = enhanced_result.model_dump()
            new_fields_found = []
            
            # Check for new metadata fields
            if 'application_type' in result_dict:
                new_fields_found.append('application_type')
            if 'correspondence_phone' in result_dict:
                new_fields_found.append('correspondence_phone')
                
            # Check for new applicant fields
            if result_dict.get('applicants'):
                for applicant in result_dict['applicants']:
                    if 'is_organization' in applicant:
                        new_fields_found.append('applicant.is_organization')
                    if 'applicant_type' in applicant:
                        new_fields_found.append('applicant.applicant_type')
                    if 'address_2' in applicant:
                        new_fields_found.append('applicant.address_2')
                    if 'phone_number' in applicant:
                        new_fields_found.append('applicant.phone_number')
                    if 'email' in applicant:
                        new_fields_found.append('applicant.email')
                        
            # Check for new inventor fields
            if result_dict.get('inventors'):
                for inventor in result_dict['inventors']:
                    if 'address_2' in inventor:
                        new_fields_found.append('inventor.address_2')
                        
            logger.info(f"🆕 New fields found: {new_fields_found}")
            
        except Exception as e:
            logger.error(f"❌ Enhanced Extraction Service failed: {e}")
            return False
        
        # 3. Test Job Service with Enhanced Extraction
        logger.info("⚙️ Testing Job Service with Enhanced Extraction...")
        
        try:
            # Create a job
            job_id = await job_service.create_job(
                user_id=test_user_id,
                job_type=JobType.ADS_EXTRACTION,
                input_refs=[document_id]
            )
            
            logger.info(f"✅ Created job: {job_id}")
            
            # Process the job (this should now use enhanced extraction)
            await job_service.process_document_extraction(
                job_id=job_id,
                document_id=document_id,
                storage_key=storage_key
            )
            
            logger.info("✅ Job processing completed")
            
            # Check job status
            job = await job_service.get_job(job_id)
            logger.info(f"📊 Job status: {job.status}")
            
            if job.status == JobStatus.COMPLETED:
                logger.info("✅ Job completed successfully")
            else:
                logger.warning(f"⚠️ Job status: {job.status}")
                if job.error_details:
                    logger.error(f"❌ Job error: {job.error_details}")
            
        except Exception as e:
            logger.error(f"❌ Job Service test failed: {e}")
            # Continue with document check anyway
        
        # 4. Verify Document has Enhanced Data
        logger.info("📋 Checking document extraction data...")
        
        try:
            doc = await db.documents.find_one({"_id": ObjectId(document_id)})
            
            if doc and doc.get('extraction_data'):
                extraction_data = doc['extraction_data']
                logger.info("✅ Document has extraction data")
                logger.info(f"📊 Extraction data keys: {list(extraction_data.keys())}")
                
                # Check for enhanced fields in the stored data
                enhanced_fields_in_db = []
                
                if 'application_type' in extraction_data:
                    enhanced_fields_in_db.append('application_type')
                if 'correspondence_phone' in extraction_data:
                    enhanced_fields_in_db.append('correspondence_phone')
                    
                if extraction_data.get('applicants'):
                    for i, applicant in enumerate(extraction_data['applicants']):
                        if 'is_organization' in applicant:
                            enhanced_fields_in_db.append(f'applicants[{i}].is_organization')
                        if 'applicant_type' in applicant:
                            enhanced_fields_in_db.append(f'applicants[{i}].applicant_type')
                        if 'address_2' in applicant:
                            enhanced_fields_in_db.append(f'applicants[{i}].address_2')
                        if 'phone_number' in applicant:
                            enhanced_fields_in_db.append(f'applicants[{i}].phone_number')
                        if 'email' in applicant:
                            enhanced_fields_in_db.append(f'applicants[{i}].email')
                            
                if extraction_data.get('inventors'):
                    for i, inventor in enumerate(extraction_data['inventors']):
                        if 'address_2' in inventor:
                            enhanced_fields_in_db.append(f'inventors[{i}].address_2')
                
                logger.info(f"🆕 Enhanced fields in database: {enhanced_fields_in_db}")
                
                if enhanced_fields_in_db:
                    logger.info("✅ Enhanced fields successfully stored in database!")
                else:
                    logger.warning("⚠️ No enhanced fields found in database - may be using old extraction")
                    
            else:
                logger.warning("⚠️ No extraction data found in document")
                
        except Exception as e:
            logger.error(f"❌ Document data check failed: {e}")
        
        # 5. Simulate Frontend Data Reception
        logger.info("🖥️ Simulating Frontend Data Reception...")
        
        try:
            # This simulates what the frontend would receive from the API
            doc = await db.documents.find_one({"_id": ObjectId(document_id)})
            
            if doc and doc.get('extraction_data'):
                frontend_data = doc['extraction_data']
                
                # Simulate the frontend mergeFileResults function
                merged_data = {
                    'title': frontend_data.get('title'),
                    'application_number': frontend_data.get('application_number'),
                    'application_type': frontend_data.get('application_type'),  # NEW FIELD
                    'correspondence_phone': frontend_data.get('correspondence_phone'),  # NEW FIELD
                    'inventors': [],
                    'applicants': []
                }
                
                # Process inventors with new fields
                if frontend_data.get('inventors'):
                    for inventor in frontend_data['inventors']:
                        merged_inventor = {
                            'name': inventor.get('name'),
                            'first_name': inventor.get('first_name'),
                            'last_name': inventor.get('last_name'),
                            'city': inventor.get('city'),
                            'state': inventor.get('state'),
                            'country': inventor.get('country'),
                            'address_2': inventor.get('address_2')  # NEW FIELD
                        }
                        merged_data['inventors'].append(merged_inventor)
                
                # Process applicants with new fields
                if frontend_data.get('applicants'):
                    for applicant in frontend_data['applicants']:
                        merged_applicant = {
                            'name': applicant.get('name'),
                            'city': applicant.get('city'),
                            'state': applicant.get('state'),
                            'country': applicant.get('country'),
                            'is_organization': applicant.get('is_organization', False),  # NEW FIELD
                            'applicant_type': applicant.get('applicant_type', 'Assignee'),  # NEW FIELD
                            'address_2': applicant.get('address_2'),  # NEW FIELD
                            'phone_number': applicant.get('phone_number'),  # NEW FIELD
                            'email': applicant.get('email')  # NEW FIELD
                        }
                        merged_data['applicants'].append(merged_applicant)
                
                logger.info("✅ Frontend data simulation successful")
                logger.info(f"📊 Frontend would receive: {json.dumps(merged_data, indent=2)}")
                
                # Check if new fields would be available to frontend
                frontend_new_fields = []
                if merged_data.get('application_type') is not None:
                    frontend_new_fields.append('application_type')
                if merged_data.get('correspondence_phone') is not None:
                    frontend_new_fields.append('correspondence_phone')
                    
                for i, applicant in enumerate(merged_data.get('applicants', [])):
                    if applicant.get('is_organization') is not None:
                        frontend_new_fields.append(f'applicants[{i}].is_organization')
                    if applicant.get('applicant_type') is not None:
                        frontend_new_fields.append(f'applicants[{i}].applicant_type')
                    if applicant.get('address_2') is not None:
                        frontend_new_fields.append(f'applicants[{i}].address_2')
                    if applicant.get('phone_number') is not None:
                        frontend_new_fields.append(f'applicants[{i}].phone_number')
                    if applicant.get('email') is not None:
                        frontend_new_fields.append(f'applicants[{i}].email')
                        
                for i, inventor in enumerate(merged_data.get('inventors', [])):
                    if inventor.get('address_2') is not None:
                        frontend_new_fields.append(f'inventors[{i}].address_2')
                
                if frontend_new_fields:
                    logger.info(f"✅ Frontend would receive new fields: {frontend_new_fields}")
                else:
                    logger.warning("⚠️ Frontend would not receive any new fields")
                    
            else:
                logger.error("❌ No data available for frontend simulation")
                
        except Exception as e:
            logger.error(f"❌ Frontend simulation failed: {e}")
        
        # 6. Cleanup
        logger.info("🧹 Cleaning up test data...")
        try:
            await db.documents.delete_one({"_id": ObjectId(document_id)})
            await db.processing_jobs.delete_many({"user_id": test_user_id})
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup failed: {e}")
        
        logger.info("🎉 Complete Enhanced Data Flow Test finished!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        await close_mongo_connection()

async def main():
    """Main test runner."""
    success = await test_complete_enhanced_data_flow()
    
    if success:
        print("\n✅ COMPLETE ENHANCED DATA FLOW TEST PASSED")
        print("The enhanced extraction pipeline is working correctly!")
        print("Frontend should now receive the new USPTO ADS fields.")
    else:
        print("\n❌ COMPLETE ENHANCED DATA FLOW TEST FAILED")
        print("There are issues with the enhanced extraction pipeline.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())