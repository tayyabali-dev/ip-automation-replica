#!/usr/bin/env python3
"""
Test script to validate ADS extraction fixes with diagnostic logging.
This script tests the specific issues reported:
1. Missing Applicant #2 (Global Health Analytics Ltd.)
2. Missing postal codes for inventors
3. Missing entity status
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.enhanced_llm_integration import enhanced_llm_service
from app.core.config import settings

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ads_extraction_debug.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_ads_extraction_with_diagnostics():
    """Test ADS extraction with enhanced diagnostics"""
    
    # Test PDF path - you'll need to provide the actual path to your test PDF
    test_pdf_path = "tests/complex_ads_test.pdf"  # Update this path
    
    if not os.path.exists(test_pdf_path):
        logger.error(f"ERROR: Test PDF not found: {test_pdf_path}")
        logger.info("Please update the test_pdf_path variable with the correct path to your test PDF")
        return
    
    logger.info("STARTING ADS EXTRACTION DEBUG TEST")
    logger.info(f"Test PDF: {test_pdf_path}")
    logger.info(f"Model: {settings.GEMINI_MODEL}")
    
    try:
        # Test enhanced extraction with diagnostics
        logger.info("=" * 60)
        logger.info("TESTING ENHANCED EXTRACTION WITH DIAGNOSTICS")
        logger.info("=" * 60)
        
        async def progress_callback(progress: int, message: str):
            logger.info(f"Progress: {progress}% - {message}")
        
        # Run enhanced extraction
        result = await enhanced_llm_service.analyze_cover_sheet_enhanced(
            file_path=test_pdf_path,
            progress_callback=progress_callback,
            use_validation=True
        )
        
        logger.info("=" * 60)
        logger.info("EXTRACTION RESULTS ANALYSIS")
        logger.info("=" * 60)
        
        # Analyze results for the specific missing data
        logger.info(f"Title: {result.title}")
        logger.info(f"Application Number: {result.application_number}")
        logger.info(f"Entity Status: {result.entity_status}")
        
        # Check inventors and postal codes
        logger.info(f"Inventors Found: {len(result.inventors)}")
        for i, inventor in enumerate(result.inventors):
            logger.info(f"  Inventor {i+1}:")
            logger.info(f"    Name: {inventor.given_name} {inventor.middle_name or ''} {inventor.family_name}")
            logger.info(f"    Address: {inventor.street_address}")
            logger.info(f"    City/State: {inventor.city}, {inventor.state}")
            logger.info(f"    Postal Code: {inventor.postal_code} {'FOUND' if inventor.postal_code else 'MISSING'}")
            logger.info(f"    Country: {inventor.country}")
            logger.info(f"    Citizenship: {inventor.citizenship}")
        
        # Check applicants - THIS IS THE CRITICAL TEST
        logger.info(f"Applicants Found: {len(result.applicants)}")
        expected_applicants = ["MedTech Innovations Corporation", "Global Health Analytics Ltd."]
        
        for i, applicant in enumerate(result.applicants):
            logger.info(f"  Applicant {i+1}:")
            logger.info(f"    Organization: {applicant.organization_name}")
            logger.info(f"    Address: {applicant.street_address}")
            logger.info(f"    City/State: {applicant.city}, {applicant.state}")
            logger.info(f"    Postal Code: {applicant.postal_code}")
            logger.info(f"    Country: {applicant.country}")
        
        # VALIDATION CHECKS
        logger.info("=" * 60)
        logger.info("VALIDATION RESULTS")
        logger.info("=" * 60)
        
        # Check for missing Applicant #2
        applicant_names = [app.organization_name for app in result.applicants if app.organization_name]
        missing_applicants = []
        for expected in expected_applicants:
            if not any(expected.lower() in name.lower() for name in applicant_names):
                missing_applicants.append(expected)
        
        if missing_applicants:
            logger.error(f"MISSING APPLICANTS: {missing_applicants}")
        else:
            logger.info("All expected applicants found")
        
        # Check for missing postal codes
        missing_postal_codes = []
        expected_postal_codes = ["02115", "02138", "94103", "94301"]
        found_postal_codes = [inv.postal_code for inv in result.inventors if inv.postal_code]
        
        for expected_code in expected_postal_codes:
            if expected_code not in found_postal_codes:
                missing_postal_codes.append(expected_code)
        
        if missing_postal_codes:
            logger.error(f"MISSING POSTAL CODES: {missing_postal_codes}")
        else:
            logger.info("All expected postal codes found")
        
        # Check entity status
        if not result.entity_status:
            logger.error("MISSING ENTITY STATUS")
        elif "Large Entity" not in result.entity_status:
            logger.warning(f"UNEXPECTED ENTITY STATUS: {result.entity_status} (expected: Large Entity)")
        else:
            logger.info("Entity status found correctly")
        
        # Quality metrics
        logger.info("=" * 60)
        logger.info("QUALITY METRICS")
        logger.info("=" * 60)
        logger.info(f"Overall Quality Score: {result.quality_metrics.overall_quality_score:.2f}")
        logger.info(f"Completeness Score: {result.quality_metrics.completeness_score:.2f}")
        logger.info(f"Confidence Score: {result.quality_metrics.confidence_score:.2f}")
        logger.info(f"Manual Review Required: {result.manual_review_required}")
        
        if result.extraction_warnings:
            logger.warning("EXTRACTION WARNINGS:")
            for warning in result.extraction_warnings:
                logger.warning(f"  - {warning}")
        
        if result.recommendations:
            logger.info("RECOMMENDATIONS:")
            for rec in result.recommendations:
                logger.info(f"  - {rec}")
        
        return result
        
    except Exception as e:
        logger.error(f"EXTRACTION FAILED: {e}", exc_info=True)
        return None

async def main():
    """Main test function"""
    logger.info("ADS EXTRACTION DEBUG TEST STARTING")
    
    # Test the extraction
    result = await test_ads_extraction_with_diagnostics()
    
    if result:
        logger.info("TEST COMPLETED - Check logs above for detailed analysis")
    else:
        logger.error("TEST FAILED - Check error logs")
    
    logger.info("Full debug log saved to: ads_extraction_debug.log")

if __name__ == "__main__":
    asyncio.run(main())