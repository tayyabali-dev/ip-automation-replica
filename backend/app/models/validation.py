"""
ADS Data Integrity Validation Models

This module defines all data structures for the ADS validation system,
including validation reports, field mismatches, and extracted XFA data models.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.common import MongoBaseModel

class ValidationSeverity(str, Enum):
    """Severity levels for validation issues"""
    ERROR = "ERROR"      # Critical - blocks PDF generation
    WARNING = "WARNING"  # Advisory - allows PDF generation
    INFO = "INFO"        # Informational - minor normalization

class ValidationCategory(str, Enum):
    """Categories of validation checks"""
    INVENTOR_DATA = "inventor_data"
    APPLICANT_DATA = "applicant_data"
    APPLICATION_INFO = "application_info"
    CORRESPONDENCE = "correspondence"
    STRUCTURAL = "structural"

class FieldMismatch(BaseModel):
    """Represents a single field validation mismatch"""
    field_path: str = Field(..., description="Dot notation path to field, e.g. 'inventors[0].last_name'")
    expected_value: Optional[str] = Field(None, description="Original value from source metadata")
    actual_value: Optional[str] = Field(None, description="Value found in generated XFA XML")
    severity: ValidationSeverity = Field(..., description="Severity level of the mismatch")
    description: str = Field(..., description="Human-readable explanation of the issue")
    auto_corrected: bool = Field(False, description="Whether the issue was automatically corrected")
    correction_applied: Optional[str] = Field(None, description="The correction that was applied")
    category: ValidationCategory = Field(ValidationCategory.STRUCTURAL, description="Category of validation")

class ValidationSummary(BaseModel):
    """Summary statistics for validation results"""
    total_fields_checked: int = Field(0, description="Total number of fields validated")
    errors_count: int = Field(0, description="Number of critical errors found")
    warnings_count: int = Field(0, description="Number of warnings found")
    info_count: int = Field(0, description="Number of informational messages")
    auto_corrections_count: int = Field(0, description="Number of automatic corrections applied")
    validation_score: float = Field(1.0, description="Overall validation score (0.0-1.0)")
    categories_checked: List[ValidationCategory] = Field(default_factory=list, description="Categories that were validated")

class ValidationReport(BaseModel):
    """Complete validation report for an ADS generation"""
    is_valid: bool = Field(..., description="True if no critical errors (allows PDF generation)")
    summary: ValidationSummary = Field(..., description="Summary statistics")
    mismatches: List[FieldMismatch] = Field(default_factory=list, description="All field mismatches found")
    processing_time_ms: int = Field(..., description="Time taken for validation in milliseconds")
    checked_at: datetime = Field(default_factory=datetime.utcnow, description="When validation was performed")
    xfa_xml_size: int = Field(0, description="Size of the XFA XML that was validated")
    source_metadata_hash: Optional[str] = Field(None, description="Hash of source metadata for tracking")

class ADSGenerationResponse(BaseModel):
    """Response from ADS generation including validation results"""
    success: bool = Field(..., description="Whether the operation was successful")
    pdf_generated: bool = Field(False, description="Whether PDF was successfully generated")
    pdf_size_bytes: Optional[int] = Field(None, description="Size of generated PDF")
    filename: Optional[str] = Field(None, description="Generated filename")
    validation_report: ValidationReport = Field(..., description="Detailed validation report")
    generation_blocked: bool = Field(False, description="Whether generation was blocked due to critical errors")
    blocking_errors: List[FieldMismatch] = Field(default_factory=list, description="Critical errors that blocked generation")
    message: str = Field("", description="Human-readable status message")

# XFA Field Extraction Models

class ExtractedInventor(BaseModel):
    """Inventor data extracted from XFA XML"""
    sequence: int = Field(..., description="Inventor sequence number")
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    
    # Residence information
    residence_city: Optional[str] = None
    residence_state: Optional[str] = None
    residence_country: Optional[str] = None
    residency_type: Optional[str] = None  # "us-residency" or "non-us-residency"
    
    # Citizenship
    citizenship: Optional[str] = None
    
    # Mailing address
    mail_address1: Optional[str] = None
    mail_address2: Optional[str] = None
    mail_city: Optional[str] = None
    mail_state: Optional[str] = None
    mail_postcode: Optional[str] = None
    mail_country: Optional[str] = None

class ExtractedApplicant(BaseModel):
    """Applicant data extracted from XFA XML"""
    sequence: int = Field(..., description="Applicant sequence number")
    is_organization: bool = Field(True, description="Whether this is an organization")
    organization_name: Optional[str] = None
    
    # Individual fields
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    
    # Authority and address
    authority_type: Optional[str] = None  # "assignee", "legal-representative", etc.
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None

class ExtractedXFAData(BaseModel):
    """Complete data structure extracted from XFA XML"""
    # Application information
    title: Optional[str] = None
    attorney_docket_number: Optional[str] = None
    application_type: Optional[str] = None
    entity_status: Optional[str] = None
    total_drawing_sheets: Optional[str] = None
    suggested_figure: Optional[str] = None
    
    # Inventors and applicants
    inventors: List[ExtractedInventor] = Field(default_factory=list)
    applicants: List[ExtractedApplicant] = Field(default_factory=list)
    
    # Correspondence
    correspondence_customer_number: Optional[str] = None
    correspondence_name1: Optional[str] = None
    correspondence_name2: Optional[str] = None
    correspondence_address1: Optional[str] = None
    correspondence_address2: Optional[str] = None
    correspondence_city: Optional[str] = None
    correspondence_state: Optional[str] = None
    correspondence_country: Optional[str] = None
    correspondence_postcode: Optional[str] = None
    correspondence_phone: Optional[str] = None
    correspondence_fax: Optional[str] = None
    correspondence_email: Optional[str] = None
    
    # Metadata
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    xml_structure_valid: bool = Field(True, description="Whether XML structure was valid")
    extraction_warnings: List[str] = Field(default_factory=list)

class ValidationRule(BaseModel):
    """Defines a specific validation rule"""
    rule_id: str = Field(..., description="Unique identifier for the rule")
    category: ValidationCategory = Field(..., description="Category this rule belongs to")
    description: str = Field(..., description="Description of what this rule validates")
    severity: ValidationSeverity = Field(..., description="Default severity for violations")
    is_enabled: bool = Field(True, description="Whether this rule is currently active")

# Predefined validation rules
VALIDATION_RULES = [
    ValidationRule(
        rule_id="inventor_name_required",
        category=ValidationCategory.INVENTOR_DATA,
        description="Inventor must have both first and last name",
        severity=ValidationSeverity.ERROR
    ),
    ValidationRule(
        rule_id="inventor_address_complete",
        category=ValidationCategory.INVENTOR_DATA,
        description="Inventor must have complete address (city, state, country)",
        severity=ValidationSeverity.ERROR
    ),
    ValidationRule(
        rule_id="name_case_normalization",
        category=ValidationCategory.INVENTOR_DATA,
        description="Name case has been normalized to title case",
        severity=ValidationSeverity.INFO
    ),
    ValidationRule(
        rule_id="country_code_standardization",
        category=ValidationCategory.INVENTOR_DATA,
        description="Country name standardized to 2-letter ISO code",
        severity=ValidationSeverity.WARNING
    ),
    ValidationRule(
        rule_id="applicant_organization_required",
        category=ValidationCategory.APPLICANT_DATA,
        description="Applicant must have organization name or individual names",
        severity=ValidationSeverity.ERROR
    ),
    ValidationRule(
        rule_id="application_title_required",
        category=ValidationCategory.APPLICATION_INFO,
        description="Application title is required for USPTO submission",
        severity=ValidationSeverity.ERROR
    ),
    ValidationRule(
        rule_id="state_code_normalization",
        category=ValidationCategory.INVENTOR_DATA,
        description="State name normalized to 2-letter code",
        severity=ValidationSeverity.WARNING
    ),
    ValidationRule(
        rule_id="entity_status_normalization",
        category=ValidationCategory.APPLICATION_INFO,
        description="Entity status normalized to standard values",
        severity=ValidationSeverity.WARNING
    )
]