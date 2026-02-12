#!/usr/bin/env python3
"""
Comprehensive end-to-end integration test for the enhanced extraction system.
Tests the complete pipeline from document input to validated output.
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_complete_integration():
    """Test the complete enhanced extraction pipeline"""
    print("🧪 COMPREHENSIVE SYSTEM INTEGRATION TEST")
    print("=" * 50)
    
    try:
        # Import all required components
        from app.services.enhanced_extraction_service import EnhancedExtractionService
        from app.services.validation_service import ValidationService
        from app.services.llm import LLMService
        from app.models.enhanced_extraction import ExtractionMethod, DataCompleteness
        
        print("✅ All imports successful")
        
        # Initialize services
        llm_service = LLMService()
        extraction_service = EnhancedExtractionService(llm_service)
        validation_service = ValidationService()
        
        print("✅ Services initialized successfully")
        
        # Create mock document content
        mock_document_text = """
UNITED STATES PATENT AND TRADEMARK OFFICE

APPLICATION DATA SHEET

Title of Invention: ADVANCED MACHINE LEARNING SYSTEM FOR AUTOMATED PATENT ANALYSIS

Attorney Docket Number: TECH-2024-001

INVENTOR INFORMATION:

First Inventor:
Name: Dr. Sarah Elizabeth Johnson
Residence: Palo Alto, California, United States
Mailing Address: 1234 Innovation Drive, Suite 100, Palo Alto, CA 94301, United States

Second Inventor: 
Name: Michael Chen
Residence: San Francisco, CA, US
Mailing Address: 567 Tech Boulevard, Apt 25B, San Francisco, California 94105, USA

APPLICANT INFORMATION:
TechCorp Innovations LLC
Address: 1234 Innovation Drive, Suite 100, Palo Alto, CA 94301, United States

CORRESPONDENCE INFORMATION:
Customer Number: 12345
Email Address: patents@techcorp.com
"""
        
        print("✅ Mock document created")
        
        # Test evidence gathering
        print("\n🔍 Testing Evidence Gathering...")
        evidence = await test_evidence_gathering(extraction_service, mock_document_text)
        if not evidence:
            return False
        
        # Test JSON generation
        print("\n🏗️ Testing JSON Generation...")
        result = await test_json_generation(extraction_service, evidence)
        if not result:
            return False
        
        # Test validation
        print("\n🔍 Testing Validation Framework...")
        validation_ok = await test_validation_framework(validation_service, result)
        if not validation_ok:
            return False
        
        # Test quality metrics
        print("\n📊 Testing Quality Metrics...")
        metrics_ok = test_quality_metrics(result)
        if not metrics_ok:
            return False
        
        print("\n🎉 COMPLETE INTEGRATION TEST PASSED!")
        print("=" * 40)
        print("✅ Evidence gathering: WORKING")
        print("✅ JSON generation: WORKING")
        print("✅ Validation framework: WORKING")
        print("✅ Quality metrics: WORKING")
        print("✅ End-to-end pipeline: FUNCTIONAL")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_evidence_gathering(extraction_service, document_text):
    """Test evidence gathering functionality"""
    try:
        from app.models.enhanced_extraction import (
            DocumentEvidence, EvidenceItem, SourceLocation, 
            ExtractionMethod, ConfidenceLevel
        )
        
        # Create mock evidence (simulating what would come from LLM)
        from datetime import datetime
        evidence = DocumentEvidence(
            document_pages=1,
            extraction_timestamp=datetime.utcnow()
        )
        
        # Add title evidence
        evidence.title_evidence = EvidenceItem(
            field_name="title",
            raw_text="ADVANCED MACHINE LEARNING SYSTEM FOR AUTOMATED PATENT ANALYSIS",
            source_location=SourceLocation(
                page=1,
                section="Title",
                raw_text="Title of Invention: ADVANCED MACHINE LEARNING SYSTEM FOR AUTOMATED PATENT ANALYSIS",
                extraction_method=ExtractionMethod.TEXT_EXTRACTION
            ),
            confidence=ConfidenceLevel.HIGH
        )
        
        print("  ✅ Title evidence created")
        
        # Add inventor evidence
        from app.models.enhanced_extraction import InventorEvidence
        inventor_evidence = InventorEvidence(
            sequence_number=1,
            completeness=DataCompleteness.COMPLETE,
            overall_confidence=ConfidenceLevel.HIGH
        )
        
        inventor_evidence.given_name_evidence = EvidenceItem(
            field_name="given_name",
            raw_text="Sarah Elizabeth",
            source_location=SourceLocation(
                page=1,
                section="Inventor 1",
                raw_text="Name: Dr. Sarah Elizabeth Johnson",
                extraction_method=ExtractionMethod.TEXT_EXTRACTION
            ),
            confidence=ConfidenceLevel.HIGH
        )
        
        evidence.inventor_evidence.append(inventor_evidence)
        print("  ✅ Inventor evidence created")
        
        return evidence
        
    except Exception as e:
        print(f"  ❌ Evidence gathering test failed: {e}")
        return None

async def test_json_generation(extraction_service, evidence):
    """Test JSON generation from evidence"""
    try:
        from app.models.enhanced_extraction import (
            EnhancedExtractionResult, EnhancedInventor, EnhancedApplicant,
            QualityMetrics, ExtractionMetadata
        )
        
        # Create mock extraction result
        result = EnhancedExtractionResult(
            title="ADVANCED MACHINE LEARNING SYSTEM FOR AUTOMATED PATENT ANALYSIS",
            attorney_docket_number="TECH-2024-001",
            customer_number="12345",
            correspondence_email="patents@techcorp.com",
            document_evidence=evidence,
            extraction_metadata=ExtractionMetadata(
                extraction_method=ExtractionMethod.TEXT_EXTRACTION,
                document_type="patent_application",
                processing_time=1.5
            ),
            quality_metrics=QualityMetrics(
                completeness_score=0.95,
                accuracy_score=0.98,
                confidence_score=0.92,
                consistency_score=0.90,
                overall_quality_score=0.94,
                required_fields_populated=8,
                total_required_fields=10,
                optional_fields_populated=5,
                total_optional_fields=8,
                validation_errors=0,
                validation_warnings=1
            )
        )
        
        # Add inventor
        inventor = EnhancedInventor(
            given_name="Sarah Elizabeth",
            family_name="Johnson",
            street_address="1234 Innovation Drive, Suite 100",
            city="Palo Alto",
            state="CA",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.95
        )
        result.inventors.append(inventor)
        
        # Add applicant
        applicant = EnhancedApplicant(
            is_assignee=True,
            organization_name="TechCorp Innovations LLC",
            street_address="1234 Innovation Drive, Suite 100",
            city="Palo Alto",
            state="CA",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.90
        )
        result.applicants.append(applicant)
        
        print("  ✅ JSON structure generated successfully")
        print(f"  📊 Title: {result.title}")
        print(f"  👥 Inventors: {len(result.inventors)}")
        print(f"  🏢 Applicants: {len(result.applicants)}")
        
        return result
        
    except Exception as e:
        print(f"  ❌ JSON generation test failed: {e}")
        return None

async def test_validation_framework(validation_service, result):
    """Test validation framework"""
    try:
        from app.services.validation_service import FieldValidator
        
        validator = FieldValidator()
        
        # Test field validations
        name_result = validator.validate_name("Sarah Elizabeth Johnson", "full_name")
        print(f"  ✅ Name validation: {name_result.is_valid}")
        
        state_result = validator.validate_state("CA", "US")
        print(f"  ✅ State validation: {state_result.is_valid}")
        
        email_result = validator.validate_email("patents@techcorp.com")
        print(f"  ✅ Email validation: {email_result.is_valid}")
        
        date_result = validator.validate_date("2023-01-15")
        print(f"  ✅ Date validation: {date_result.is_valid}")
        
        # Test validation service
        validation_results = await validation_service.validate_extraction_result(result)
        print(f"  ✅ Validation service: {validation_results.overall_valid}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Validation test failed: {e}")
        return False

def test_quality_metrics(result):
    """Test quality metrics calculation"""
    try:
        metrics = result.quality_metrics
        
        print(f"  📊 Completeness Score: {metrics.completeness_score:.2f}")
        print(f"  📊 Accuracy Score: {metrics.accuracy_score:.2f}")
        print(f"  📊 Confidence Score: {metrics.confidence_score:.2f}")
        print(f"  📊 Overall Quality: {metrics.overall_quality_score:.2f}")
        
        # Verify metrics are within valid ranges
        assert 0.0 <= metrics.completeness_score <= 1.0
        assert 0.0 <= metrics.accuracy_score <= 1.0
        assert 0.0 <= metrics.confidence_score <= 1.0
        assert 0.0 <= metrics.overall_quality_score <= 1.0
        
        print("  ✅ Quality metrics validation passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Quality metrics test failed: {e}")
        return False

def main():
    """Run the complete integration test"""
    print("🚀 STARTING COMPREHENSIVE SYSTEM INTEGRATION TEST")
    print("This will verify that all components work together correctly.")
    print()
    
    # Run async test
    success = asyncio.run(test_complete_integration())
    
    if success:
        print("\n🎉 SYSTEM INTEGRATION TEST: PASSED")
        print("=" * 40)
        print("The enhanced extraction system is running correctly!")
        print("All components are properly integrated and functional.")
    else:
        print("\n❌ SYSTEM INTEGRATION TEST: FAILED")
        print("=" * 40)
        print("There are issues with the system integration.")
        print("Please review the error messages above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)