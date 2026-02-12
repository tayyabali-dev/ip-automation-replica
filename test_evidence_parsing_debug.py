#!/usr/bin/env python3
"""
Targeted diagnostic test to investigate evidence parsing issues
"""

import asyncio
import logging
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.enhanced_extraction_service import EnhancedExtractionService
from app.services.llm import LLMService
from app.models.enhanced_extraction import ExtractionMethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('evidence_parsing_debug.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_evidence_parsing_detailed():
    """Test evidence parsing step by step with detailed logging"""
    
    logger.info("=== EVIDENCE PARSING DEBUG TEST ===")
    
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
        
        # Step 1: Get raw LLM response
        logger.info("=== STEP 1: RAW LLM RESPONSE ===")
        
        # Get evidence prompt
        evidence_prompt = extraction_service.evidence_gathering_prompts.get_evidence_prompt(
            ExtractionMethod.TEXT_EXTRACTION, "patent_application"
        )
        
        # Extract text content
        text_content = await llm_service._extract_text_locally(test_file, None)
        
        # Generate evidence using LLM
        full_prompt = f"{evidence_prompt}\n\n## DOCUMENT TEXT CONTENT:\n{text_content[:50000]}"
        raw_response = await llm_service.generate_structured_content(
            prompt=full_prompt,
            retries=3
        )
        
        logger.info("=== RAW LLM RESPONSE STRUCTURE ===")
        logger.info(f"Response type: {type(raw_response)}")
        
        if isinstance(raw_response, list):
            logger.info(f"List length: {len(raw_response)}")
            if raw_response:
                logger.info(f"First element type: {type(raw_response[0])}")
                if isinstance(raw_response[0], dict):
                    logger.info(f"First element keys: {list(raw_response[0].keys())}")
                    
                    # Check inventor structure
                    if "inventors" in raw_response[0]:
                        inventors = raw_response[0]["inventors"]
                        logger.info(f"Inventors found: {len(inventors)}")
                        for i, inv in enumerate(inventors):
                            logger.info(f"INVENTOR {i+1} STRUCTURE:")
                            logger.info(f"  Type: {type(inv)}")
                            logger.info(f"  Keys: {list(inv.keys()) if isinstance(inv, dict) else 'Not a dict'}")
                            if isinstance(inv, dict):
                                if "given_name" in inv:
                                    logger.info(f"  given_name type: {type(inv['given_name'])}")
                                    logger.info(f"  given_name value: {inv['given_name']}")
                                if "family_name" in inv:
                                    logger.info(f"  family_name type: {type(inv['family_name'])}")
                                    logger.info(f"  family_name value: {inv['family_name']}")
                    
                    # Check applicant structure
                    if "applicants" in raw_response[0]:
                        applicants = raw_response[0]["applicants"]
                        logger.info(f"Applicants found: {len(applicants)}")
                        for i, app in enumerate(applicants):
                            logger.info(f"APPLICANT {i+1} STRUCTURE:")
                            logger.info(f"  Type: {type(app)}")
                            logger.info(f"  Keys: {list(app.keys()) if isinstance(app, dict) else 'Not a dict'}")
                            if isinstance(app, dict) and "organization_name" in app:
                                logger.info(f"  organization_name type: {type(app['organization_name'])}")
                                logger.info(f"  organization_name value: {app['organization_name']}")
        
        elif isinstance(raw_response, dict):
            logger.info(f"Dict keys: {list(raw_response.keys())}")
        
        # Step 2: Test evidence parsing
        logger.info("=== STEP 2: EVIDENCE PARSING TEST ===")
        
        # Parse the response using the extraction service
        document_evidence = await extraction_service._parse_evidence_response(
            raw_response, ExtractionMethod.TEXT_EXTRACTION
        )
        
        # Step 3: Examine parsed evidence structure
        logger.info("=== STEP 3: PARSED EVIDENCE STRUCTURE ===")
        
        logger.info(f"Inventor evidence count: {len(document_evidence.inventor_evidence)}")
        for i, inv_evidence in enumerate(document_evidence.inventor_evidence):
            logger.info(f"INVENTOR {i+1} EVIDENCE:")
            if inv_evidence.given_name_evidence:
                logger.info(f"  given_name_evidence.raw_text type: {type(inv_evidence.given_name_evidence.raw_text)}")
                logger.info(f"  given_name_evidence.raw_text value: {inv_evidence.given_name_evidence.raw_text}")
            if inv_evidence.family_name_evidence:
                logger.info(f"  family_name_evidence.raw_text type: {type(inv_evidence.family_name_evidence.raw_text)}")
                logger.info(f"  family_name_evidence.raw_text value: {inv_evidence.family_name_evidence.raw_text}")
        
        logger.info(f"Applicant evidence count: {len(document_evidence.applicant_evidence)}")
        for i, app_evidence in enumerate(document_evidence.applicant_evidence):
            logger.info(f"APPLICANT {i+1} EVIDENCE:")
            if app_evidence.organization_name_evidence:
                logger.info(f"  organization_name_evidence.raw_text type: {type(app_evidence.organization_name_evidence.raw_text)}")
                logger.info(f"  organization_name_evidence.raw_text value: {app_evidence.organization_name_evidence.raw_text}")
        
        # Step 4: Test evidence summary generation
        logger.info("=== STEP 4: EVIDENCE SUMMARY GENERATION ===")
        evidence_summary = extraction_service.json_generation_prompts._summarize_evidence(document_evidence)
        
        logger.info("=== EVIDENCE SUMMARY RESULT ===")
        logger.info(evidence_summary)
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_evidence_parsing_detailed())