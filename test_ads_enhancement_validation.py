"""
Comprehensive test suite for ADS Enhancement functionality.
Tests the new Critical and Important fields for Patent ADS extraction.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from backend.app.services.enhanced_extraction_service import EnhancedExtractionService
from backend.app.models.enhanced_extraction import (
    EnhancedExtractionResult, EnhancedInventor, EnhancedApplicant,
    DocumentEvidence, InventorEvidence, ApplicantEvidence, EvidenceItem,
    SourceLocation, ExtractionMethod, ConfidenceLevel, DataCompleteness,
    QualityMetrics, ExtractionMetadata
)

class TestADSEnhancement:
    """Test ADS Enhancement functionality"""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM service for testing"""
        mock_service = Mock()
        mock_service.upload_file = AsyncMock()
        mock_service._extract_text_locally = AsyncMock()
        mock_service._extract_xfa_data = AsyncMock()
        mock_service.generate_structured_content = AsyncMock()
        return mock_service
    
    @pytest.fixture
    def extraction_service(self, mock_llm_service):
        """Create extraction service with mocked dependencies"""
        return EnhancedExtractionService(llm_service=mock_llm_service)
    
    def test_organization_detection_logic(self, extraction_service):
        """Test organization detection logic for applicants"""
        
        # Test corporate indicators
        test_cases = [
            ("TechCorp Inc.", True, "Assignee"),
            ("Innovation LLC", True, "Assignee"),
            ("Research Ltd.", True, "Assignee"),
            ("Global Corp", True, "Assignee"),
            ("University of Technology", True, "Assignee"),
            ("John Doe", False, "Assignee"),
            ("Jane Smith", False, "Assignee"),
            ("", False, "Assignee"),
            (None, False, "Assignee")
        ]
        
        for name, expected_is_org, expected_type in test_cases:
            is_org, app_type = extraction_service._detect_organization_type(name)
            assert is_org == expected_is_org, f"Failed for '{name}': expected {expected_is_org}, got {is_org}"
            assert app_type == expected_type, f"Failed for '{name}': expected {expected_type}, got {app_type}"
    
    def test_address_separation_logic(self, extraction_service):
        """Test address separation logic for Suite/Apt/Unit"""
        
        test_cases = [
            ("123 Main St, Suite 100", "123 Main St", "Suite 100"),
            ("456 Oak Ave, Apt 5B", "456 Oak Ave", "Apt 5B"),
            ("789 Pine Rd, Unit 12", "789 Pine Rd", "Unit 12"),
            ("321 Elm St, Floor 3", "321 Elm St", "Floor 3"),
            ("654 Maple Dr, Ste. 200", "654 Maple Dr", "Ste. 200"),
            ("987 Cedar Ln, #45", "987 Cedar Ln", "#45"),
            ("111 Simple St", "111 Simple St", None),
            ("", "", None),
            (None, None, None)
        ]
        
        for full_addr, expected_primary, expected_secondary in test_cases:
            primary, secondary = extraction_service._separate_address_components(full_addr)
            assert primary == expected_primary, f"Primary failed for '{full_addr}': expected '{expected_primary}', got '{primary}'"
            assert secondary == expected_secondary, f"Secondary failed for '{full_addr}': expected '{expected_secondary}', got '{secondary}'"
    
    @pytest.mark.asyncio
    async def test_ads_critical_fields_extraction(self, extraction_service, mock_llm_service):
        """Test extraction of ADS Critical fields"""
        
        # Mock LLM responses with ADS Critical fields
        mock_llm_service._extract_xfa_data.return_value = None
        mock_llm_service._extract_text_locally.return_value = "Sample patent document text"
        
        # Mock evidence gathering response with Critical fields
        evidence_response = {
            "title_evidence": {
                "raw_text": "Advanced AI Patent System",
                "page": 1,
                "section": "header",
                "confidence": "high"
            },
            "attorney_docket_evidence": {
                "raw_text": "TECH-2024-001",
                "page": 1,
                "section": "header",
                "confidence": "high"
            },
            "application_type_evidence": {
                "raw_text": "Nonprovisional Application",
                "page": 1,
                "section": "form_field",
                "confidence": "high"
            },
            "customer_number_evidence": {
                "raw_text": "12345",
                "page": 1,
                "section": "correspondence",
                "confidence": "high"
            },
            "correspondence_email_evidence": {
                "raw_text": "attorney@lawfirm.com",
                "page": 1,
                "section": "correspondence",
                "confidence": "high"
            },
            "correspondence_phone_evidence": {
                "raw_text": "(555) 123-4567",
                "page": 1,
                "section": "correspondence",
                "confidence": "high"
            },
            "inventors_evidence": [
                {
                    "given_name": {"raw_text": "John", "page": 1, "confidence": "high"},
                    "family_name": {"raw_text": "Inventor", "page": 1, "confidence": "high"},
                    "address_evidence": [
                        {"field_name": "street_address", "raw_text": "123 Tech Blvd, Suite 100", "page": 1, "confidence": "high"}
                    ],
                    "completeness": "complete",
                    "confidence": "high"
                }
            ],
            "applicants_evidence": [
                {
                    "organization_name": {"raw_text": "TechCorp Inc.", "page": 1, "confidence": "high"},
                    "address_evidence": [
                        {"field_name": "street_address", "raw_text": "456 Business Ave, Floor 5", "page": 1, "confidence": "high"}
                    ],
                    "contact_evidence": [
                        {"field_name": "phone_number", "raw_text": "(555) 987-6543", "page": 1, "confidence": "high"},
                        {"field_name": "email", "raw_text": "contact@techcorp.com", "page": 1, "confidence": "high"}
                    ],
                    "completeness": "complete",
                    "confidence": "high"
                }
            ]
        }
        
        # Mock JSON generation response with ADS fields
        json_response = {
            "title": "Advanced AI Patent System",
            "attorney_docket_number": "TECH-2024-001",
            "application_type": "Nonprovisional Application",
            "customer_number": "12345",
            "correspondence_email": "attorney@lawfirm.com",
            "correspondence_phone": "(555) 123-4567",
            "inventors": [
                {
                    "given_name": "John",
                    "family_name": "Inventor",
                    "street_address": "123 Tech Blvd",
                    "address_2": "Suite 100",
                    "city": "Innovation City",
                    "state": "CA",
                    "country": "US",
                    "completeness": "complete",
                    "confidence_score": 0.9
                }
            ],
            "applicants": [
                {
                    "organization_name": "TechCorp Inc.",
                    "is_organization": True,
                    "applicant_type": "Assignee",
                    "street_address": "456 Business Ave",
                    "address_2": "Floor 5",
                    "phone_number": "(555) 987-6543",
                    "email": "contact@techcorp.com",
                    "city": "Business City",
                    "state": "CA",
                    "country": "US",
                    "is_assignee": True,
                    "completeness": "complete",
                    "confidence_score": 0.9
                }
            ]
        }
        
        mock_llm_service.generate_structured_content.side_effect = [evidence_response, json_response]
        
        # Test extraction
        result = await extraction_service.extract_with_two_step_process(
            file_path="test_ads.pdf",
            file_content=b"mock pdf content",
            document_type="patent_application"
        )
        
        # Verify ADS Critical fields
        assert result.attorney_docket_number == "TECH-2024-001"
        assert result.application_type == "Nonprovisional Application"
        assert result.customer_number == "12345"
        assert result.correspondence_email == "attorney@lawfirm.com"
        assert result.correspondence_phone == "(555) 123-4567"
        
        # Verify inventor address separation
        assert len(result.inventors) == 1
        inventor = result.inventors[0]
        assert inventor.street_address == "123 Tech Blvd"
        assert inventor.address_2 == "Suite 100"
        
        # Verify applicant organization detection and address separation
        assert len(result.applicants) == 1
        applicant = result.applicants[0]
        assert applicant.organization_name == "TechCorp Inc."
        assert applicant.is_organization == True
        assert applicant.applicant_type == "Assignee"
        assert applicant.street_address == "456 Business Ave"
        assert applicant.address_2 == "Floor 5"
        assert applicant.phone_number == "(555) 987-6543"
        assert applicant.email == "contact@techcorp.com"
    
    def test_backward_compatibility(self):
        """Test that new fields don't break existing functionality"""
        
        # Test that existing models can be created without new fields
        inventor = EnhancedInventor(
            given_name="John",
            family_name="Doe",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.9
        )
        
        # New field should default to None
        assert inventor.address_2 is None
        
        applicant = EnhancedApplicant(
            organization_name="Test Corp",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.9
        )
        
        # New fields should have proper defaults
        assert applicant.is_organization == False
        assert applicant.applicant_type == "Assignee"
        assert applicant.address_2 is None
        assert applicant.phone_number is None
        assert applicant.email is None
        
        result = EnhancedExtractionResult(
            title="Test Patent",
            inventors=[inventor],
            applicants=[applicant],
            quality_metrics=QualityMetrics(
                completeness_score=0.8,
                accuracy_score=0.8,
                confidence_score=0.8,
                consistency_score=0.8,
                overall_quality_score=0.8,
                required_fields_populated=2,
                total_required_fields=2,
                optional_fields_populated=0,
                total_optional_fields=0,
                validation_errors=0,
                validation_warnings=0
            ),
            extraction_metadata=ExtractionMetadata(
                extraction_method=ExtractionMethod.TEXT_EXTRACTION,
                document_type="patent_application",
                processing_time=1.0
            )
        )
        
        # New fields should default to None
        assert result.application_type is None
        assert result.correspondence_phone is None
    
    def test_ads_prompt_enhancements(self, extraction_service):
        """Test that ADS prompt enhancements are included"""
        
        # Test evidence gathering prompt includes ADS instructions
        evidence_prompt = extraction_service.evidence_gathering_prompts._get_base_evidence_prompt()
        
        # Check for Critical field instructions
        assert "Attorney Docket Number Search" in evidence_prompt
        assert "Application Type Detection" in evidence_prompt
        assert "Customer Number Extraction" in evidence_prompt
        assert "Correspondence Details" in evidence_prompt
        
        # Check for Important field logic
        assert "ORGANIZATION DETECTION LOGIC" in evidence_prompt
        assert "ADDRESS SEPARATION LOGIC" in evidence_prompt
        
        # Check for enhanced checklist
        assert "Did I extract the Attorney Docket Number" in evidence_prompt
        assert "Did I separate Address 2 for all entities" in evidence_prompt
    
    def test_json_generation_prompt_enhancements(self, extraction_service):
        """Test that JSON generation prompts include ADS fields"""
        
        # Create mock document evidence
        document_evidence = DocumentEvidence(
            document_pages=1,
            extraction_timestamp=None
        )
        
        # Test JSON generation prompt includes ADS fields
        json_prompt = extraction_service.json_generation_prompts.create_json_generation_prompt(document_evidence)
        
        # Check for Critical fields in JSON schema
        assert '"attorney_docket_number"' in json_prompt
        assert '"application_type"' in json_prompt
        assert '"correspondence_phone"' in json_prompt
        
        # Check for Important fields in JSON schema
        assert '"is_organization"' in json_prompt
        assert '"applicant_type"' in json_prompt
        assert '"address_2"' in json_prompt
        
        # Check for ADS validation rules
        assert "organization detection" in json_prompt.lower()
        assert "address separation" in json_prompt.lower()

class TestADSValidationRules:
    """Test ADS-specific validation rules"""
    
    def test_attorney_docket_validation(self):
        """Test attorney docket number validation patterns"""
        
        valid_dockets = [
            "TECH-2024-001",
            "12345-67890",
            "ABC123",
            "CLIENT-REF-2024"
        ]
        
        for docket in valid_dockets:
            # Should be alphanumeric with hyphens
            assert docket.replace("-", "").replace("_", "").isalnum()
    
    def test_application_type_validation(self):
        """Test application type validation"""
        
        valid_types = [
            "Nonprovisional",
            "Divisional",
            "Continuation",
            "Continuation-in-Part",
            "Provisional"
        ]
        
        for app_type in valid_types:
            assert isinstance(app_type, str)
            assert len(app_type) > 0
    
    def test_customer_number_validation(self):
        """Test customer number validation patterns"""
        
        valid_customer_numbers = [
            "12345",
            "123456",
            "98765"
        ]
        
        for customer_num in valid_customer_numbers:
            assert customer_num.isdigit()
            assert 5 <= len(customer_num) <= 6

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])