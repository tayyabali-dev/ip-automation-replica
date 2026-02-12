#!/usr/bin/env python3
"""
Critical diagnostic test to investigate evidence summary generation
and identify why JSON generation returns empty results.
"""

import asyncio
import logging
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.enhanced_extraction_service import EnhancedExtractionService
from app.services.llm import LLMService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('evidence_summary_debug.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_evidence_summary_generation():
    """Test evidence summary generation step by step"""
    
    logger.info("=== EVIDENCE SUMMARY DEBUG TEST ===")
    
    try:
        # Initialize services
        llm_service = LLMService()
        extraction_service = EnhancedExtractionService(llm_service)
        
        # Test file path
        test_file = "tests/complex_ads_test.pdf"
        
        if not os.path.exists(test_file):
            logger.error(f"Test file not found: {test_file}")
            return
        
        logger.info(f"Testing with file: {test_file}")
        
        # Step 1: Evidence Gathering
        logger.info("=== STEP 1: EVIDENCE GATHERING ===")
        document_evidence = await extraction_service._gather_evidence_systematic(
            test_file, None, "patent_application", None
        )
        
        logger.info("Evidence gathering completed")
        logger.info(f"Title evidence: {'FOUND' if document_evidence.title_evidence else 'MISSING'}")
        logger.info(f"App number evidence: {'FOUND' if document_evidence.application_number_evidence else 'MISSING'}")
        logger.info(f"Entity status evidence: {'FOUND' if document_evidence.entity_status_evidence else 'MISSING'}")
        logger.info(f"Inventor evidence count: {len(document_evidence.inventor_evidence)}")
        logger.info(f"Applicant evidence count: {len(document_evidence.applicant_evidence)}")
        
        # Step 2: Evidence Summary Generation
        logger.info("=== STEP 2: EVIDENCE SUMMARY GENERATION ===")
        evidence_summary = extraction_service.json_generation_prompts._summarize_evidence(document_evidence)
        
        logger.info("=== EVIDENCE SUMMARY RESULT ===")
        logger.info(f"Summary length: {len(evidence_summary)} characters")
        logger.info("Summary content:")
        logger.info(evidence_summary)
        logger.info("=== END SUMMARY ===")
        
        # Step 3: Check if summary is empty
        if not evidence_summary.strip():
            logger.error("CRITICAL: Evidence summary is EMPTY!")
            logger.error("This explains why JSON generation returns empty results!")
        else:
            logger.info("Evidence summary contains data - investigating JSON generation...")
            
            # Step 4: Test JSON Generation
            logger.info("=== STEP 3: JSON GENERATION TEST ===")
            json_prompt = extraction_service.json_generation_prompts.create_json_generation_prompt(document_evidence)
            
            logger.info(f"JSON prompt length: {len(json_prompt)} characters")
            logger.info("First 1000 chars of JSON prompt:")
            logger.info(json_prompt[:1000])
            
            # Generate JSON response
            json_response = await llm_service.generate_structured_content(
                prompt=json_prompt,
                retries=3
            )
            
            logger.info("=== JSON RESPONSE ===")
            logger.info(f"Response type: {type(json_response)}")
            logger.info(f"Response: {json_response}")
            
            # Check specific fields
            if isinstance(json_response, dict):
                logger.info(f"Title: {json_response.get('title')}")
                logger.info(f"Inventors count: {len(json_response.get('inventors', []))}")
                logger.info(f"Applicants count: {len(json_response.get('applicants', []))}")
                logger.info(f"Entity status: {json_response.get('entity_status')}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_evidence_summary_generation())