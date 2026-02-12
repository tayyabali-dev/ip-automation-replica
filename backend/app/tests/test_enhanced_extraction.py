"""
Comprehensive test suite for the enhanced extraction system.
Tests the two-step extraction process, validation, and quality metrics.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from app.services.enhanced_extraction_service import EnhancedExtractionService
from app.services.validation_service import ValidationService, FieldValidator, CrossFieldValidator
from app.models.enhanced_extraction import (
    EnhancedExtractionResult, EnhancedInventor, EnhancedApplicant,
    DocumentEvidence, InventorEvidence, ApplicantEvidence, EvidenceItem,
    SourceLocation, ExtractionMethod, ConfidenceLevel, DataCompleteness,
    QualityMetrics, ExtractionMetadata, ValidationResult
)

class TestEnhancedExtractionService:
    """Test the enhanced extraction service"""
    
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
    
    @pytest.mark.asyncio
    async def test_two_step_extraction_process(self, extraction_service, mock_llm_service):
        """Test the complete two-step extraction process"""
        
        # Mock LLM responses
        mock_llm_service._extract_xfa_data.return_value = None
        mock_llm_service._extract_text_locally.return_value = "Sample patent document text"
        
        # Mock evidence gathering response
        evidence_response = {
            "title_evidence": {
                "raw_text": "Advanced AI System for Patent Processing",
                "page": 1,
                "section": "header",
                "confidence": "high"
            },
            "inventors_evidence": [
                {
                    "sequence_number": 1,
                    "given_name": {"raw_text": "John", "page": 1, "confidence": "high"},
                    "family_name": {"raw_text": "Doe", "page": 1, "confidence": "high"},
                    "address_evidence": [
                        {"field_name": "street_address", "raw_text": "123 Main St", "page": 1, "confidence": "high"},
                        {"field_name": "city", "raw_text": "Springfield", "page": 1, "confidence": "high"}
                    ],
                    "completeness": "complete",
                    "confidence": "high"
                }
            ],
            "applicants_evidence": [
                {
                    "organization_name": {"raw_text": "TechCorp Inc", "page": 1, "confidence": "high"},
                    "address_evidence": [
                        {"field_name": "street_address", "raw_text": "456 Business Ave", "page": 1, "confidence": "high"}
                    ],
                    "completeness": "complete",
                    "confidence": "high"
                }
            ]
        }
        
        # Mock JSON generation response
        json_response = {
            "title": "Advanced AI System for Patent Processing",
            "inventors": [
                {
                    "given_name": "John",
                    "family_name": "Doe",
                    "street_address": "123 Main St",
                    "city": "Springfield",
                    "state": "IL",
                    "country": "US",
                    "completeness": "complete",
                    "confidence_score": 0.9
                }
            ],
            "applicants": [
                {
                    "organization_name": "TechCorp Inc",
                    "street_address": "456 Business Ave",
                    "city": "Springfield",
                    "state": "IL",
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
            file_path="test.pdf",
            file_content=b"mock pdf content",
            document_type="patent_application"
        )
        
        # Verify results
        assert isinstance(result, EnhancedExtractionResult)
        assert result.title == "Advanced AI System for Patent Processing"
        assert len(result.inventors) == 1
        assert result.inventors[0].given_name == "John"
        assert result.inventors[0].family_name == "Doe"
        assert len(result.applicants) == 1
        assert result.applicants[0].organization_name == "TechCorp Inc"
        
        # Verify LLM service was called correctly
        assert mock_llm_service.generate_structured_content.call_count == 2
    
    @pytest.mark.asyncio
    async def test_extraction_method_determination(self, extraction_service, mock_llm_service):
        """Test extraction method determination logic"""
        
        # Test XFA detection
        mock_llm_service._extract_xfa_data.return_value = "<xml>XFA data</xml>"
        method = await extraction_service._determine_extraction_method("test.pdf", None)
        assert method == ExtractionMethod.XFA_FORM
        
        # Test form fields detection
        mock_llm_service._extract_xfa_data.return_value = None
        mock_llm_service._extract_text_locally.return_value = "--- FORM FIELD DATA ---\nField1: Value1"
        method = await extraction_service._determine_extraction_method("test.pdf", None)
        assert method == ExtractionMethod.FORM_FIELDS
        
        # Test text extraction
        mock_llm_service._extract_text_locally.return_value = "Regular text content with sufficient length"
        method = await extraction_service._determine_extraction_method("test.pdf", None)
        assert method == ExtractionMethod.TEXT_EXTRACTION
        
        # Test vision analysis fallback
        mock_llm_service._extract_text_locally.return_value = "Short"
        method = await extraction_service._determine_extraction_method("test.pdf", None)
        assert method == ExtractionMethod.VISION_ANALYSIS
    
    @pytest.mark.asyncio
    async def test_evidence_parsing(self, extraction_service):
        """Test evidence response parsing"""
        
        evidence_response = {
            "title_evidence": {
                "raw_text": "Test Patent Title",
                "page": 1,
                "section": "header",
                "confidence": "high"
            },
            "inventors_evidence": [
                {
                    "sequence_number": 1,
                    "given_name": {"raw_text": "Jane", "page": 1, "confidence": "high"},
                    "family_name": {"raw_text": "Smith", "page": 1, "confidence": "high"},
                    "completeness": "partial_address",
                    "confidence": "medium"
                }
            ]
        }
        
        document_evidence = await extraction_service._parse_evidence_response(
            evidence_response, ExtractionMethod.TEXT_EXTRACTION
        )
        
        assert isinstance(document_evidence, DocumentEvidence)
        assert document_evidence.title_evidence.raw_text == "Test Patent Title"
        assert len(document_evidence.inventor_evidence) == 1
        assert document_evidence.inventor_evidence[0].given_name_evidence.raw_text == "Jane"
        assert document_evidence.inventor_evidence[0].family_name_evidence.raw_text == "Smith"


class TestValidationService:
    """Test the validation service"""
    
    @pytest.fixture
    def validation_service(self):
        """Create validation service"""
        return ValidationService()
    
    @pytest.fixture
    def field_validator(self):
        """Create field validator"""
        return FieldValidator()
    
    @pytest.fixture
    def sample_inventor(self):
        """Create sample inventor for testing"""
        return EnhancedInventor(
            given_name="John",
            family_name="Doe",
            street_address="123 Main St",
            city="Springfield",
            state="IL",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.9
        )
    
    @pytest.fixture
    def sample_applicant(self):
        """Create sample applicant for testing"""
        return EnhancedApplicant(
            organization_name="TechCorp Inc",
            street_address="456 Business Ave",
            city="Springfield",
            state="IL",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.9
        )
    
    def test_name_validation(self, field_validator):
        """Test name field validation"""
        
        # Valid name
        result = field_validator.validate_name("John Doe", "given_name")
        assert result.is_valid
        assert result.normalized_value == "John Doe"
        assert result.confidence_score > 0.8
        
        # Empty name
        result = field_validator.validate_name("", "given_name")
        assert not result.is_valid
        assert "required" in result.errors[0]
        
        # Name with unusual characters
        result = field_validator.validate_name("John123", "given_name")
        assert result.is_valid  # Still valid but with warning
        assert len(result.warnings) > 0
        
        # All uppercase name
        result = field_validator.validate_name("JOHN DOE", "given_name")
        assert result.is_valid
        assert result.normalized_value == "John Doe"
        assert len(result.warnings) > 0
    
    def test_address_validation(self, field_validator):
        """Test address field validation"""
        
        # Valid address
        result = field_validator.validate_address("123 Main Street", "street_address")
        assert result.is_valid
        assert result.confidence_score > 0.8
        
        # Empty address
        result = field_validator.validate_address("", "street_address")
        assert not result.is_valid
        
        # Address without numbers (warning)
        result = field_validator.validate_address("Main Street", "street_address")
        assert result.is_valid
        assert len(result.warnings) > 0
    
    def test_state_validation(self, field_validator):
        """Test state validation"""
        
        # Valid US state code
        result = field_validator.validate_state("CA", "US")
        assert result.is_valid
        assert result.normalized_value == "CA"
        
        # Valid US state name
        result = field_validator.validate_state("California", "US")
        assert result.is_valid
        assert result.normalized_value == "CA"
        assert len(result.warnings) > 0  # Normalization warning
        
        # Invalid US state
        result = field_validator.validate_state("XX", "US")
        assert not result.is_valid
        
        # Non-US state (should pass)
        result = field_validator.validate_state("Ontario", "CA")
        assert result.is_valid
    
    def test_country_validation(self, field_validator):
        """Test country validation"""
        
        # Valid country code
        result = field_validator.validate_country("US")
        assert result.is_valid
        assert result.normalized_value == "US"
        
        # Valid country name
        result = field_validator.validate_country("United States")
        assert result.is_valid
        assert result.normalized_value == "US"
        
        # Unrecognized country
        result = field_validator.validate_country("Unknown Country")
        assert result.is_valid  # Still valid but with warning
        assert len(result.warnings) > 0
    
    def test_date_validation(self, field_validator):
        """Test date validation"""
        
        # Valid date formats
        valid_dates = [
            "2023-12-31",
            "12/31/2023",
            "December 31, 2023",
            "Dec 31, 2023"
        ]
        
        for date_str in valid_dates:
            result = field_validator.validate_date(date_str)
            assert result.is_valid
            assert result.normalized_value == "2023-12-31"
        
        # Invalid date
        result = field_validator.validate_date("invalid date")
        assert not result.is_valid
        
        # Future date (warning)
        result = field_validator.validate_date("2030-01-01")
        assert result.is_valid
        assert len(result.warnings) > 0
        
        # Empty date (optional)
        result = field_validator.validate_date("")
        assert result.is_valid
        assert result.normalized_value is None
    
    def test_email_validation(self, field_validator):
        """Test email validation"""
        
        # Valid email
        result = field_validator.validate_email("test@example.com")
        assert result.is_valid
        assert result.normalized_value == "test@example.com"
        
        # Invalid email
        result = field_validator.validate_email("invalid-email")
        assert not result.is_valid
        
        # Empty email (optional)
        result = field_validator.validate_email("")
        assert result.is_valid
        assert result.normalized_value is None
    
    def test_inventor_consistency_validation(self, validation_service, sample_inventor):
        """Test inventor consistency validation"""
        
        cross_validator = CrossFieldValidator()
        
        # Consistent inventor
        result = cross_validator.validate_inventor_consistency(sample_inventor)
        assert result.is_consistent
        assert len(result.issues) == 0
        
        # Inconsistent state/country
        sample_inventor.state = "XX"  # Invalid state
        result = cross_validator.validate_inventor_consistency(sample_inventor)
        assert not result.is_consistent
        assert len(result.issues) > 0
        
        # Missing required fields
        sample_inventor.state = "IL"  # Fix state
        sample_inventor.given_name = None  # Remove required field
        result = cross_validator.validate_inventor_consistency(sample_inventor)
        assert len(result.recommendations) > 0
    
    def test_applicant_consistency_validation(self, validation_service, sample_applicant):
        """Test applicant consistency validation"""
        
        cross_validator = CrossFieldValidator()
        
        # Consistent applicant
        result = cross_validator.validate_applicant_consistency(sample_applicant)
        assert result.is_consistent
        
        # Both organization and individual names (inconsistent)
        sample_applicant.individual_given_name = "John"
        sample_applicant.individual_family_name = "Doe"
        result = cross_validator.validate_applicant_consistency(sample_applicant)
        assert not result.is_consistent
        assert len(result.issues) > 0
    
    @pytest.mark.asyncio
    async def test_full_validation_process(self, validation_service, sample_inventor, sample_applicant):
        """Test the complete validation process"""
        
        # Create sample extraction result
        result = EnhancedExtractionResult(
            title="Test Patent",
            inventors=[sample_inventor],
            applicants=[sample_applicant],
            quality_metrics=QualityMetrics(
                completeness_score=0.0,
                accuracy_score=0.0,
                confidence_score=0.0,
                consistency_score=0.0,
                overall_quality_score=0.0,
                required_fields_populated=0,
                total_required_fields=0,
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
        
        # Validate
        validated_result = await validation_service.validate_extraction_result(result)
        
        # Check that validation was performed
        assert len(validated_result.field_validations) > 0
        assert len(validated_result.cross_field_validations) > 0
        assert validated_result.quality_metrics.overall_quality_score > 0
        assert isinstance(validated_result.manual_review_required, bool)
        assert isinstance(validated_result.recommendations, list)


class TestQualityMetrics:
    """Test quality metrics calculation"""
    
    def test_quality_metrics_calculation(self):
        """Test quality metrics calculation"""
        
        # Create sample result with good quality
        inventor = EnhancedInventor(
            given_name="John",
            family_name="Doe",
            street_address="123 Main St",
            city="Springfield",
            state="IL",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.9
        )
        
        applicant = EnhancedApplicant(
            organization_name="TechCorp Inc",
            street_address="456 Business Ave",
            city="Springfield",
            state="IL",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.9
        )
        
        result = EnhancedExtractionResult(
            title="Test Patent",
            application_number="16/123,456",
            inventors=[inventor],
            applicants=[applicant],
            quality_metrics=QualityMetrics(
                completeness_score=0.0,
                accuracy_score=0.0,
                confidence_score=0.0,
                consistency_score=0.0,
                overall_quality_score=0.0,
                required_fields_populated=0,
                total_required_fields=0,
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
        
        validation_service = ValidationService()
        metrics = validation_service._calculate_quality_metrics(result)
        
        assert metrics.completeness_score > 0.8  # Should be high with complete data
        assert metrics.confidence_score > 0.8    # Should be high with confident data
        assert metrics.overall_quality_score > 0.8  # Should be high overall
        assert metrics.required_fields_populated == 2  # title and inventors
        assert metrics.total_required_fields == 2


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_extraction_service_error_handling(self, mock_llm_service):
        """Test error handling in extraction service"""
        
        extraction_service = EnhancedExtractionService(llm_service=mock_llm_service)
        
        # Mock LLM service to raise exception
        mock_llm_service._extract_xfa_data.side_effect = Exception("Test error")
        mock_llm_service._extract_text_locally.side_effect = Exception("Test error")
        
        # Should handle error gracefully
        with pytest.raises(Exception):
            await extraction_service.extract_with_two_step_process(
                file_path="test.pdf",
                document_type="patent_application"
            )
    
    @pytest.mark.asyncio
    async def test_validation_service_error_handling(self):
        """Test error handling in validation service"""
        
        validation_service = ValidationService()
        
        # Create result with invalid data
        result = EnhancedExtractionResult(
            title=None,  # Missing required field
            inventors=[],  # Missing required field
            applicants=[],
            quality_metrics=QualityMetrics(
                completeness_score=0.0,
                accuracy_score=0.0,
                confidence_score=0.0,
                consistency_score=0.0,
                overall_quality_score=0.0,
                required_fields_populated=0,
                total_required_fields=0,
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
        
        # Should handle validation gracefully
        validated_result = await validation_service.validate_extraction_result(result)
        
        # Should flag for manual review
        assert validated_result.manual_review_required
        assert len(validated_result.recommendations) > 0


class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_extraction_and_validation(self):
        """Test complete end-to-end extraction and validation"""
        
        # Mock LLM service
        mock_llm_service = Mock()
        mock_llm_service.upload_file = AsyncMock()
        mock_llm_service._extract_text_locally = AsyncMock(return_value="Sample text")
        mock_llm_service._extract_xfa_data = AsyncMock(return_value=None)
        
        # Mock successful extraction responses
        evidence_response = {
            "title_evidence": {
                "raw_text": "Complete Patent System",
                "page": 1,
                "confidence": "high"
            },
            "inventors_evidence": [
                {
                    "given_name": {"raw_text": "Alice", "page": 1, "confidence": "high"},
                    "family_name": {"raw_text": "Johnson", "page": 1, "confidence": "high"},
                    "address_evidence": [
                        {"field_name": "street_address", "raw_text": "789 Tech Blvd", "page": 1, "confidence": "high"},
                        {"field_name": "city", "raw_text": "Innovation City", "page": 1, "confidence": "high"}
                    ],
                    "completeness": "complete",
                    "confidence": "high"
                }
            ]
        }
        
        json_response = {
            "title": "Complete Patent System",
            "inventors": [
                {
                    "given_name": "Alice",
                    "family_name": "Johnson",
                    "street_address": "789 Tech Blvd",
                    "city": "Innovation City",
                    "state": "CA",
                    "country": "US",
                    "completeness": "complete",
                    "confidence_score": 0.95
                }
            ]
        }
        
        mock_llm_service.generate_structured_content.side_effect = [evidence_response, json_response]
        
        # Create services
        extraction_service = EnhancedExtractionService(llm_service=mock_llm_service)
        validation_service = ValidationService()
        
        # Perform extraction
        extraction_result = await extraction_service.extract_with_two_step_process(
            file_path="test.pdf",
            document_type="patent_application"
        )
        
        # Perform validation
        final_result = await validation_service.validate_extraction_result(extraction_result)
        
        # Verify complete pipeline
        assert final_result.title == "Complete Patent System"
        assert len(final_result.inventors) == 1
        assert final_result.inventors[0].given_name == "Alice"
        assert final_result.quality_metrics.overall_quality_score > 0.7
        assert len(final_result.field_validations) > 0
        assert isinstance(final_result.manual_review_required, bool)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])