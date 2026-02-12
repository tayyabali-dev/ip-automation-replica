#!/usr/bin/env python3
"""
Comprehensive test for enhanced multiple applicant detection system.
Tests the improved evidence gathering, parsing, and JSON generation.
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Mock environment variables for testing
os.environ.setdefault("MONGODB_URL", "mongodb://localhost:27017/test_db")
os.environ.setdefault("SECRET_KEY", "test_secret_key")
os.environ.setdefault("GOOGLE_API_KEY", "test_google_api_key")

from app.services.enhanced_extraction_service import EnhancedExtractionService
from app.services.llm import LLMService
from app.models.enhanced_extraction import ExtractionMethod
from unittest.mock import Mock, AsyncMock

class TestEnhancedMultiApplicantExtraction:
    """Test suite for enhanced multiple applicant detection"""
    
    def __init__(self):
        self.mock_llm_service = self._create_mock_llm_service()
        self.extraction_service = EnhancedExtractionService(llm_service=self.mock_llm_service)
    
    def _create_mock_llm_service(self) -> Mock:
        """Create mock LLM service for testing"""
        mock_service = Mock()
        mock_service.upload_file = AsyncMock()
        mock_service._extract_text_locally = AsyncMock()
        mock_service._extract_xfa_data = AsyncMock(return_value=None)
        mock_service.generate_structured_content = AsyncMock()
        return mock_service
    
    async def test_multi_applicant_evidence_gathering(self):
        """Test enhanced evidence gathering for multiple applicants"""
        print("🧪 Testing Enhanced Multi-Applicant Evidence Gathering...")
        
        # Mock document text with multiple applicants
        mock_text = """
        Title of Invention: Advanced AI System for Patent Processing
        
        Applicant Information:
        Applicant 1: TechCorp Industries Inc
        Address: 123 Innovation Drive, Tech City, CA 94105, USA
        Customer Number: 12345
        
        Applicant 2: Global Health Analytics Ltd
        Address: 456 Research Blvd, Innovation Park, CA 94106, USA
        Customer Number: 67890
        
        Inventor Information:
        Inventor 1: John A. Doe
        Address: 789 Inventor St, Residential City, CA 94107, USA
        """
        
        # Mock LLM response with multiple applicants
        mock_evidence_response = {
            "title_evidence": {
                "raw_text": "Advanced AI System for Patent Processing",
                "page": 1,
                "section": "header",
                "confidence": "high"
            },
            "applicants_evidence": [
                {
                    "organization_name": "TechCorp Industries Inc",
                    "address": "123 Innovation Drive, Tech City, CA 94105, USA",
                    "customer_number": "12345",
                    "source": {"page": 1, "section": "applicant_info"},
                    "completeness": "complete",
                    "confidence": "high"
                },
                {
                    "organization_name": "Global Health Analytics Ltd",
                    "address": "456 Research Blvd, Innovation Park, CA 94106, USA", 
                    "customer_number": "67890",
                    "source": {"page": 1, "section": "applicant_info"},
                    "completeness": "complete",
                    "confidence": "high"
                }
            ],
            "inventors_evidence": [
                {
                    "name": "John A. Doe",
                    "address": "789 Inventor St, Residential City, CA 94107, USA",
                    "source": {"page": 1, "section": "inventor_info"},
                    "completeness": "complete",
                    "confidence": "high"
                }
            ]
        }
        
        # Setup mock responses
        self.mock_llm_service._extract_text_locally.return_value = mock_text
        self.mock_llm_service.generate_structured_content.return_value = mock_evidence_response
        
        # Test evidence gathering
        document_evidence = await self.extraction_service._gather_evidence_systematic(
            "test.pdf", None, "patent_application"
        )
        
        # Validate results
        assert document_evidence.title_evidence is not None
        assert document_evidence.title_evidence.raw_text == "Advanced AI System for Patent Processing"
        
        # Check multiple applicants were found
        assert len(document_evidence.applicant_evidence) == 2
        
        # Validate first applicant
        first_applicant = document_evidence.applicant_evidence[0]
        assert first_applicant.organization_name_evidence is not None
        assert first_applicant.organization_name_evidence.raw_text == "TechCorp Industries Inc"
        assert len(first_applicant.address_evidence) > 0
        assert len(first_applicant.contact_evidence) > 0
        
        # Validate second applicant
        second_applicant = document_evidence.applicant_evidence[1]
        assert second_applicant.organization_name_evidence is not None
        assert second_applicant.organization_name_evidence.raw_text == "Global Health Analytics Ltd"
        assert len(second_applicant.address_evidence) > 0
        assert len(second_applicant.contact_evidence) > 0
        
        # Check inventor was found
        assert len(document_evidence.inventor_evidence) == 1
        
        print("✅ Multi-applicant evidence gathering test passed!")
        return True
    
    async def test_secondary_applicant_detection(self):
        """Test detection of applicants in secondary sections"""
        print("🧪 Testing Secondary Applicant Detection...")
        
        # Mock evidence response with applicants in secondary sections
        mock_evidence_response = {
            "applicants_evidence": [
                {
                    "organization_name": "Primary Corp Inc",
                    "address": "123 Main St, City, CA 94105",
                    "completeness": "complete",
                    "confidence": "high"
                }
            ],
            "correspondence_evidence": [
                {
                    "raw_text": "Correspondence Address: Secondary Technologies LLC, 456 Business Ave, Tech City, CA 94106",
                    "page": 1,
                    "section": "correspondence"
                }
            ],
            "header_evidence": [
                {
                    "raw_text": "Third Party Industries Corporation - Patent Application",
                    "page": 1,
                    "section": "header"
                }
            ]
        }
        
        self.mock_llm_service.generate_structured_content.return_value = mock_evidence_response
        
        # Test evidence parsing
        document_evidence = await self.extraction_service._parse_evidence_response(
            mock_evidence_response, ExtractionMethod.TEXT_EXTRACTION
        )
        
        # Should find primary applicant plus secondary applicants
        print(f"Found {len(document_evidence.applicant_evidence)} total applicants")
        
        # Validate we found multiple applicants from different sources
        assert len(document_evidence.applicant_evidence) >= 2
        
        # Check for primary applicant
        primary_found = any(
            app.organization_name_evidence and 
            "Primary Corp Inc" in app.organization_name_evidence.raw_text
            for app in document_evidence.applicant_evidence
        )
        assert primary_found, "Primary applicant not found"
        
        print("✅ Secondary applicant detection test passed!")
        return True
    
    async def test_applicant_deduplication(self):
        """Test applicant deduplication logic"""
        print("🧪 Testing Applicant Deduplication...")
        
        try:
            # Create duplicate applicant candidates
            from app.models.enhanced_extraction import ApplicantEvidence, EvidenceItem, SourceLocation, ConfidenceLevel, DataCompleteness
            
            # First instance of same company
            applicant1 = ApplicantEvidence(
                completeness=DataCompleteness.COMPLETE,
                overall_confidence=ConfidenceLevel.HIGH
            )
            applicant1.organization_name_evidence = EvidenceItem(
                field_name="organization_name",
                raw_text="TechCorp Industries Inc",
                source_location=SourceLocation(
                    page=1, section="applicant_info", raw_text="TechCorp Industries Inc",
                    extraction_method=ExtractionMethod.TEXT_EXTRACTION
                ),
                confidence=ConfidenceLevel.HIGH
            )
            
            # Second instance of same company (slight variation)
            applicant2 = ApplicantEvidence(
                completeness=DataCompleteness.PARTIAL_NAME,
                overall_confidence=ConfidenceLevel.MEDIUM
            )
            applicant2.organization_name_evidence = EvidenceItem(
                field_name="organization_name",
                raw_text="TechCorp Industries Inc.",
                source_location=SourceLocation(
                    page=1, section="header", raw_text="TechCorp Industries Inc.",
                    extraction_method=ExtractionMethod.TEXT_EXTRACTION
                ),
                confidence=ConfidenceLevel.MEDIUM
            )
            
            # Different company
            applicant3 = ApplicantEvidence(
                completeness=DataCompleteness.COMPLETE,
                overall_confidence=ConfidenceLevel.HIGH
            )
            applicant3.organization_name_evidence = EvidenceItem(
                field_name="organization_name",
                raw_text="Global Health Analytics Ltd",
                source_location=SourceLocation(
                    page=1, section="applicant_info", raw_text="Global Health Analytics Ltd",
                    extraction_method=ExtractionMethod.TEXT_EXTRACTION
                ),
                confidence=ConfidenceLevel.HIGH
            )
            
            # Test deduplication
            candidates = [applicant1, applicant2, applicant3]
            deduplicated = self.extraction_service._deduplicate_applicant_candidates(candidates)
            
            # Should have 2 unique applicants (TechCorp and Global Health)
            assert len(deduplicated) == 2, f"Expected 2 unique applicants, got {len(deduplicated)}"
            
            # Check that the higher quality version was kept
            techcorp_applicant = None
            for app in deduplicated:
                if app.organization_name_evidence and "TechCorp" in app.organization_name_evidence.raw_text:
                    techcorp_applicant = app
                    break
            
            assert techcorp_applicant is not None, "TechCorp applicant not found in deduplicated results"
            assert techcorp_applicant.completeness == DataCompleteness.COMPLETE, f"Expected COMPLETE, got {techcorp_applicant.completeness}"
            
            print("✅ Applicant deduplication test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Deduplication test error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_enhanced_json_generation(self):
        """Test enhanced JSON generation with multiple applicants"""
        print("🧪 Testing Enhanced JSON Generation...")
        
        # Create mock document evidence with multiple applicants
        from app.models.enhanced_extraction import DocumentEvidence, ApplicantEvidence, EvidenceItem, SourceLocation, DataCompleteness, ConfidenceLevel
        from datetime import datetime
        
        document_evidence = DocumentEvidence(
            document_pages=1,
            extraction_timestamp=datetime.utcnow()
        )
        
        # Add multiple applicants
        for i, (name, address) in enumerate([
            ("TechCorp Industries Inc", "123 Innovation Drive, Tech City, CA 94105"),
            ("Global Health Analytics Ltd", "456 Research Blvd, Innovation Park, CA 94106")
        ]):
            applicant = ApplicantEvidence(
                completeness=DataCompleteness.COMPLETE,
                overall_confidence=ConfidenceLevel.HIGH
            )
            applicant.organization_name_evidence = EvidenceItem(
                field_name="organization_name",
                raw_text=name,
                source_location=SourceLocation(
                    page=1, section="applicant_info", raw_text=name,
                    extraction_method=ExtractionMethod.TEXT_EXTRACTION
                ),
                confidence=ConfidenceLevel.HIGH
            )
            applicant.address_evidence.append(EvidenceItem(
                field_name="address",
                raw_text=address,
                source_location=SourceLocation(
                    page=1, section="applicant_info", raw_text=address,
                    extraction_method=ExtractionMethod.TEXT_EXTRACTION
                ),
                confidence=ConfidenceLevel.HIGH
            ))
            document_evidence.applicant_evidence.append(applicant)
        
        # Mock JSON response with multiple applicants
        mock_json_response = {
            "title": "Advanced AI System for Patent Processing",
            "applicants": [
                {
                    "applicant_sequence": 1,
                    "organization_name": "TechCorp Industries Inc",
                    "street_address": "123 Innovation Drive",
                    "city": "Tech City",
                    "state": "CA",
                    "postal_code": "94105",
                    "country": "US",
                    "is_assignee": True,
                    "relationship_to_inventors": "separate_entity",
                    "completeness": "complete",
                    "confidence_score": 0.9
                },
                {
                    "applicant_sequence": 2,
                    "organization_name": "Global Health Analytics Ltd",
                    "street_address": "456 Research Blvd",
                    "city": "Innovation Park", 
                    "state": "CA",
                    "postal_code": "94106",
                    "country": "US",
                    "is_assignee": True,
                    "relationship_to_inventors": "separate_entity",
                    "completeness": "complete",
                    "confidence_score": 0.9
                }
            ],
            "inventors": []
        }
        
        self.mock_llm_service.generate_structured_content.return_value = mock_json_response
        
        # Test JSON generation
        extraction_result = await self.extraction_service._generate_json_from_evidence(
            document_evidence
        )
        
        # Validate results
        assert extraction_result.title == "Advanced AI System for Patent Processing"
        assert len(extraction_result.applicants) == 2
        
        # Check first applicant
        first_applicant = extraction_result.applicants[0]
        assert first_applicant.organization_name == "TechCorp Industries Inc"
        assert first_applicant.street_address == "123 Innovation Drive"
        assert first_applicant.city == "Tech City"
        assert first_applicant.state == "CA"
        assert first_applicant.postal_code == "94105"
        
        # Check second applicant
        second_applicant = extraction_result.applicants[1]
        assert second_applicant.organization_name == "Global Health Analytics Ltd"
        assert second_applicant.street_address == "456 Research Blvd"
        assert second_applicant.city == "Innovation Park"
        assert second_applicant.state == "CA"
        assert second_applicant.postal_code == "94106"
        
        print("✅ Enhanced JSON generation test passed!")
        return True
    
    async def test_complete_multi_applicant_workflow(self):
        """Test the complete multi-applicant extraction workflow"""
        print("🧪 Testing Complete Multi-Applicant Workflow...")
        
        # Mock complete workflow with multiple applicants
        mock_text = """
        Advanced AI System for Patent Processing
        
        Applicant 1: TechCorp Industries Inc
        123 Innovation Drive, Tech City, CA 94105
        Customer Number: 12345
        
        Applicant 2: Global Health Analytics Ltd  
        456 Research Blvd, Innovation Park, CA 94106
        Customer Number: 67890
        
        Inventor: John A. Doe
        789 Inventor St, Residential City, CA 94107
        """
        
        # Mock evidence response
        mock_evidence_response = {
            "applicants_evidence": [
                {
                    "organization_name": "TechCorp Industries Inc",
                    "address": "123 Innovation Drive, Tech City, CA 94105",
                    "customer_number": "12345",
                    "completeness": "complete",
                    "confidence": "high"
                },
                {
                    "organization_name": "Global Health Analytics Ltd",
                    "address": "456 Research Blvd, Innovation Park, CA 94106",
                    "customer_number": "67890", 
                    "completeness": "complete",
                    "confidence": "high"
                }
            ],
            "inventors_evidence": [
                {
                    "name": "John A. Doe",
                    "address": "789 Inventor St, Residential City, CA 94107",
                    "completeness": "complete",
                    "confidence": "high"
                }
            ]
        }
        
        # Mock JSON response
        mock_json_response = {
            "title": "Advanced AI System for Patent Processing",
            "applicants": [
                {
                    "organization_name": "TechCorp Industries Inc",
                    "street_address": "123 Innovation Drive",
                    "city": "Tech City",
                    "state": "CA", 
                    "postal_code": "94105",
                    "country": "US",
                    "customer_number": "12345",
                    "is_assignee": True,
                    "relationship_to_inventors": "separate_entity",
                    "completeness": "complete",
                    "confidence_score": 0.9
                },
                {
                    "organization_name": "Global Health Analytics Ltd",
                    "street_address": "456 Research Blvd",
                    "city": "Innovation Park",
                    "state": "CA",
                    "postal_code": "94106", 
                    "country": "US",
                    "customer_number": "67890",
                    "is_assignee": True,
                    "relationship_to_inventors": "separate_entity",
                    "completeness": "complete",
                    "confidence_score": 0.9
                }
            ],
            "inventors": [
                {
                    "given_name": "John",
                    "middle_name": "A",
                    "family_name": "Doe",
                    "street_address": "789 Inventor St",
                    "city": "Residential City",
                    "state": "CA",
                    "postal_code": "94107",
                    "country": "US",
                    "completeness": "complete",
                    "confidence_score": 0.9
                }
            ]
        }
        
        # Setup mocks
        self.mock_llm_service._extract_text_locally.return_value = mock_text
        self.mock_llm_service.generate_structured_content.side_effect = [
            mock_evidence_response, mock_json_response
        ]
        
        # Test complete workflow
        result = await self.extraction_service.extract_with_two_step_process(
            "test.pdf", None, "patent_application"
        )
        
        # Validate complete results
        assert result.title == "Advanced AI System for Patent Processing"
        assert len(result.applicants) == 2
        assert len(result.inventors) == 1
        
        # Validate applicant details
        applicant_names = [app.organization_name for app in result.applicants]
        assert "TechCorp Industries Inc" in applicant_names
        assert "Global Health Analytics Ltd" in applicant_names
        
        # Validate inventor details
        inventor = result.inventors[0]
        assert inventor.given_name == "John"
        assert inventor.middle_name == "A"
        assert inventor.family_name == "Doe"
        
        print("✅ Complete multi-applicant workflow test passed!")
        return True

async def run_all_tests():
    """Run all enhanced multi-applicant extraction tests"""
    print("🚀 Starting Enhanced Multi-Applicant Extraction Tests")
    print("=" * 60)
    
    test_suite = TestEnhancedMultiApplicantExtraction()
    
    tests = [
        ("Multi-Applicant Evidence Gathering", test_suite.test_multi_applicant_evidence_gathering),
        ("Secondary Applicant Detection", test_suite.test_secondary_applicant_detection),
        ("Applicant Deduplication", test_suite.test_applicant_deduplication),
        ("Enhanced JSON Generation", test_suite.test_enhanced_json_generation),
        ("Complete Multi-Applicant Workflow", test_suite.test_complete_multi_applicant_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n📋 Running: {test_name}")
            success = await test_func()
            results.append((test_name, success, None))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False, str(e)))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if error:
            print(f"    Error: {error}")
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All enhanced multi-applicant extraction tests passed!")
        print("The system is ready for improved multiple applicant detection.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the implementation.")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest execution failed: {e}")
        sys.exit(1)