"""
Enhanced extraction models for the two-step extraction process.
Provides comprehensive data structures for evidence gathering and validation.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime

class ConfidenceLevel(str, Enum):
    """Confidence levels for extracted data"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ExtractionMethod(str, Enum):
    """Methods used for data extraction"""
    XFA_FORM = "xfa_form"
    TEXT_EXTRACTION = "text_extraction"
    VISION_ANALYSIS = "vision_analysis"
    FORM_FIELDS = "form_fields"
    PATTERN_MATCHING = "pattern_matching"

class DataCompleteness(str, Enum):
    """Completeness levels for extracted data"""
    COMPLETE = "complete"
    PARTIAL_NAME = "partial_name"
    PARTIAL_ADDRESS = "partial_address"
    NAME_ONLY = "name_only"
    ADDRESS_ONLY = "address_only"
    INCOMPLETE = "incomplete"

class SourceLocation(BaseModel):
    """Location information for extracted data"""
    page: int
    section: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    raw_text: str
    extraction_method: ExtractionMethod

class EvidenceItem(BaseModel):
    """Individual piece of evidence gathered during extraction"""
    field_name: str
    raw_text: str
    source_location: SourceLocation
    confidence: ConfidenceLevel
    extraction_notes: Optional[str] = None

class InventorEvidence(BaseModel):
    """Evidence gathered for a single inventor"""
    sequence_number: Optional[int] = None
    given_name_evidence: Optional[EvidenceItem] = None
    middle_name_evidence: Optional[EvidenceItem] = None
    family_name_evidence: Optional[EvidenceItem] = None
    full_name_evidence: Optional[EvidenceItem] = None
    address_evidence: List[EvidenceItem] = []
    city_evidence: Optional[EvidenceItem] = None
    state_evidence: Optional[EvidenceItem] = None
    country_evidence: Optional[EvidenceItem] = None
    citizenship_evidence: Optional[EvidenceItem] = None
    completeness: DataCompleteness
    overall_confidence: ConfidenceLevel

class ApplicantEvidence(BaseModel):
    """Evidence gathered for applicant/company information"""
    organization_name_evidence: Optional[EvidenceItem] = None
    individual_name_evidence: List[EvidenceItem] = []
    address_evidence: List[EvidenceItem] = []
    contact_evidence: List[EvidenceItem] = []
    relationship_evidence: Optional[EvidenceItem] = None
    completeness: DataCompleteness
    overall_confidence: ConfidenceLevel

class DocumentEvidence(BaseModel):
    """Complete evidence gathered from document"""
    title_evidence: Optional[EvidenceItem] = None
    application_number_evidence: Optional[EvidenceItem] = None
    filing_date_evidence: Optional[EvidenceItem] = None
    entity_status_evidence: Optional[EvidenceItem] = None
    attorney_docket_evidence: Optional[EvidenceItem] = None
    inventor_evidence: List[InventorEvidence] = []
    applicant_evidence: List[ApplicantEvidence] = []
    correspondence_evidence: List[EvidenceItem] = []
    priority_evidence: List[EvidenceItem] = []
    
    # Metadata
    document_pages: int
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    extraction_duration: Optional[float] = None
    evidence_quality_score: Optional[float] = None

class ValidationResult(BaseModel):
    """Result of field validation"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    normalized_value: Optional[Any] = None
    confidence_score: float

class FieldValidationResult(BaseModel):
    """Validation result for a specific field"""
    field_name: str
    original_value: Any
    validation_result: ValidationResult
    enhancement_applied: bool = False
    enhancement_notes: Optional[str] = None

class CrossFieldValidationResult(BaseModel):
    """Result of cross-field validation"""
    validation_type: str
    fields_involved: List[str]
    is_consistent: bool
    issues: List[str] = []
    recommendations: List[str] = []
    confidence_impact: float = 0.0

class QualityMetrics(BaseModel):
    """Quality metrics for extraction result"""
    completeness_score: float = Field(ge=0.0, le=1.0)
    accuracy_score: float = Field(ge=0.0, le=1.0)
    confidence_score: float = Field(ge=0.0, le=1.0)
    consistency_score: float = Field(ge=0.0, le=1.0)
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    
    # Detailed metrics
    required_fields_populated: int
    total_required_fields: int
    optional_fields_populated: int
    total_optional_fields: int
    validation_errors: int
    validation_warnings: int

class ExtractionMetadata(BaseModel):
    """Metadata about the extraction process"""
    extraction_method: ExtractionMethod
    document_type: str
    processing_time: float
    llm_tokens_used: Optional[int] = None
    fallback_level_used: Optional[str] = None
    manual_review_required: bool = False
    extraction_notes: List[str] = []

class EnhancedInventor(BaseModel):
    """Enhanced inventor model with validation and confidence"""
    # Core data
    given_name: Optional[str] = None
    middle_name: Optional[str] = None
    family_name: Optional[str] = None
    full_name: Optional[str] = None
    
    # Address information
    street_address: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    citizenship: Optional[str] = None
    
    # Metadata
    sequence_number: Optional[int] = None
    completeness: DataCompleteness
    confidence_score: float = Field(ge=0.0, le=1.0)
    validation_results: List[FieldValidationResult] = []
    source_evidence: Optional[InventorEvidence] = None

class EnhancedApplicant(BaseModel):
    """Enhanced applicant model with validation and confidence"""
    # Core data
    is_assignee: bool = False
    organization_name: Optional[str] = None
    individual_given_name: Optional[str] = None
    individual_family_name: Optional[str] = None
    
    # Address information
    street_address: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    # Contact information
    customer_number: Optional[str] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    
    # Metadata
    relationship_to_inventors: str = "separate_entity"
    legal_entity_type: Optional[str] = None
    completeness: DataCompleteness
    confidence_score: float = Field(ge=0.0, le=1.0)
    validation_results: List[FieldValidationResult] = []
    source_evidence: Optional[ApplicantEvidence] = None

class PriorityClaimInfo(BaseModel):
    """Priority claim information"""
    application_number: str
    filing_date: str
    country: Optional[str] = None
    continuity_type: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0)

class EnhancedExtractionResult(BaseModel):
    """Enhanced extraction result with comprehensive validation and metadata"""
    
    # Core application data
    title: Optional[str] = None
    application_number: Optional[str] = None
    filing_date: Optional[str] = None
    entity_status: Optional[str] = None
    attorney_docket_number: Optional[str] = None
    total_drawing_sheets: Optional[int] = None
    
    # Inventor and applicant data
    inventors: List[EnhancedInventor] = []
    applicants: List[EnhancedApplicant] = []
    
    # Priority and correspondence
    domestic_priority_claims: List[PriorityClaimInfo] = []
    foreign_priority_claims: List[PriorityClaimInfo] = []
    customer_number: Optional[str] = None
    correspondence_email: Optional[str] = None
    
    # Quality and validation
    quality_metrics: QualityMetrics
    field_validations: List[FieldValidationResult] = []
    cross_field_validations: List[CrossFieldValidationResult] = []
    
    # Evidence and metadata
    document_evidence: Optional[DocumentEvidence] = None
    extraction_metadata: ExtractionMetadata
    
    # Flags and recommendations
    manual_review_required: bool = False
    extraction_warnings: List[str] = []
    recommendations: List[str] = []

    @validator('inventors')
    def validate_inventors_not_empty(cls, v):
        """Ensure at least one inventor is present"""
        if not v:
            raise ValueError("At least one inventor is required")
        return v

    @validator('quality_metrics')
    def validate_quality_metrics(cls, v):
        """Ensure quality metrics are reasonable"""
        if v.overall_quality_score < 0.0 or v.overall_quality_score > 1.0:
            raise ValueError("Overall quality score must be between 0.0 and 1.0")
        return v

class ExtractionError(Exception):
    """Base exception for extraction errors"""
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}

class ValidationError(ExtractionError):
    """Exception for validation errors"""
    pass

class EvidenceGatheringError(ExtractionError):
    """Exception for evidence gathering errors"""
    pass

class DataProcessingError(ExtractionError):
    """Exception for data processing errors"""
    pass