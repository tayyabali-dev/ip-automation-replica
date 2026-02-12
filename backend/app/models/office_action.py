from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import date
from app.models.common import MongoBaseModel


# ============================================================================
# ENUMS - Rejection and Objection Types
# ============================================================================

class RejectionType(str, Enum):
    """Normalized rejection type enumeration covering AIA and pre-AIA statutes."""
    # 35 U.S.C. 101 - Patent Eligibility
    SEC_101 = "101"

    # 35 U.S.C. 102 - Novelty (AIA)
    SEC_102_A1 = "102(a)(1)"  # Prior art from publications/public use
    SEC_102_A2 = "102(a)(2)"  # Prior art from earlier filed applications

    # 35 U.S.C. 102 - Novelty (pre-AIA)
    SEC_102_A = "102(a)"
    SEC_102_B = "102(b)"
    SEC_102_E = "102(e)"
    SEC_102_G = "102(g)"

    # 35 U.S.C. 103 - Obviousness
    SEC_103 = "103"
    SEC_103_A = "103(a)"  # pre-AIA

    # 35 U.S.C. 112 - Specification Requirements
    SEC_112_A = "112(a)"  # Written description, enablement
    SEC_112_B = "112(b)"  # Definiteness
    SEC_112_D = "112(d)"  # Dependent claim issues
    SEC_112_F = "112(f)"  # Means-plus-function
    SEC_112_1 = "112 first paragraph"  # pre-AIA
    SEC_112_2 = "112 second paragraph"  # pre-AIA

    # Double Patenting
    DOUBLE_PATENTING_STATUTORY = "statutory_double_patenting"
    DOUBLE_PATENTING_ODP = "obviousness_double_patenting"
    DOUBLE_PATENTING_PROVISIONAL = "provisional_double_patenting"

    # Other
    UNKNOWN = "unknown"


class ObjectionType(str, Enum):
    """Normalized objection type enumeration."""
    CLAIM = "claim"
    SPECIFICATION = "specification"
    DRAWINGS = "drawings"
    TITLE = "title"
    ABSTRACT = "abstract"
    FORMALITY = "formality"
    UNKNOWN = "unknown"


# ============================================================================
# PRIORITY AND CONTINUITY DATA
# ============================================================================

class ForeignPriorityInfo(BaseModel):
    """Foreign priority claim under 35 U.S.C. 119."""
    country: Optional[str] = None
    application_number: Optional[str] = None
    filing_date: Optional[str] = None
    certified_copy_attached: Optional[bool] = None


class ParentApplicationInfo(BaseModel):
    """Parent application continuity data."""
    parent_application_number: Optional[str] = None
    parent_filing_date: Optional[str] = None
    relationship_type: Optional[str] = None  # "continuation", "continuation-in-part", "divisional"
    status: Optional[str] = None  # "pending", "patented", "abandoned"
    patent_number: Optional[str] = None  # If patented


# ============================================================================
# PRIOR ART AND REFERENCES
# ============================================================================

class PriorArtReference(BaseModel):
    """Prior art reference with enhanced extraction fields."""
    reference_id: Optional[str] = None  # Unique ID for cross-referencing (e.g., "ref_1")
    reference_type: str  # "US Patent", "US Publication", "Foreign Patent", "NPL"
    identifier: str  # e.g., "US 9,999,999 B2", "US 2017/0060574 A1"
    short_name: Optional[str] = None  # Examiner's shorthand (e.g., "Smith", "the '574 publication")
    inventor_author: Optional[str] = None  # First named inventor or author
    title: Optional[str] = None
    date: Optional[str] = None
    relevant_sections: Optional[str] = None  # e.g., "[0045-0048]", "Col. 3, lines 15-30"
    relevant_claims: List[str] = Field(default_factory=list)
    citation_details: Optional[str] = None
    used_in_rejection_indices: List[int] = Field(default_factory=list)  # Cross-reference to rejections

    @field_validator('relevant_claims', 'used_in_rejection_indices', mode='before')
    @classmethod
    def convert_none_to_list(cls, v):
        return v if v is not None else []


class RejectionReferenceLink(BaseModel):
    """Links a reference to a specific rejection with role information."""
    rejection_index: int
    reference_id: str
    role: str  # "primary", "secondary", "teaching"
    relevance_explanation: Optional[str] = None


class PriorArtCombination(BaseModel):
    """Groups prior art references for Section 103 obviousness rejections."""
    primary_reference_id: str
    secondary_reference_ids: List[str] = Field(default_factory=list)
    motivation_to_combine: Optional[str] = None  # Examiner's rationale
    teaching_suggestion_motivation: Optional[str] = None  # TSM reasoning
    affected_claim_elements: Optional[List[str]] = None  # Which claim elements each ref teaches


# ============================================================================
# REJECTIONS
# ============================================================================

class Rejection(BaseModel):
    """Rejection with enhanced type detection and 103 combination grouping."""
    rejection_type: str  # Original extracted type (e.g., "102", "103", "112")
    rejection_type_normalized: Optional[RejectionType] = None  # Normalized enum value
    statutory_basis: Optional[str] = None  # e.g., "35 U.S.C. 103"
    is_aia: Optional[bool] = None  # True if AIA statute, False if pre-AIA
    affected_claims: List[str] = Field(default_factory=list)
    examiner_reasoning: str
    cited_prior_art: List[PriorArtReference] = Field(default_factory=list)
    relevant_claim_language: Optional[str] = None
    page_number: Optional[str] = None

    # Section 103 specific - prior art combinations
    prior_art_combinations: List[PriorArtCombination] = Field(default_factory=list)


# ============================================================================
# CLAIMS
# ============================================================================

class ClaimStatus(BaseModel):
    """Claim status with optional full text extraction."""
    claim_number: str
    status: str  # "Rejected", "Allowed", "Objected to", "Cancelled", "Withdrawn", "Pending"
    dependency_type: str  # "Independent" or "Dependent"
    parent_claim: Optional[str] = None  # For dependent claims

    # Full claim text extraction (optional)
    claim_text: Optional[str] = None  # Complete claim text
    claim_preamble: Optional[str] = None  # The introductory phrase (e.g., "A method for...")
    claim_body: Optional[str] = None  # The claim elements/limitations


# ============================================================================
# OBJECTIONS
# ============================================================================

class Objection(BaseModel):
    """Objection with normalized type."""
    objected_item: str  # e.g., "Drawings", "Specification", "Claim 1"
    objection_type: Optional[ObjectionType] = None  # Normalized type
    reason: str
    corrective_action: Optional[str] = None
    page_number: Optional[str] = None


# ============================================================================
# EXAMINER STATEMENTS
# ============================================================================

class ExaminerStatement(BaseModel):
    """Examiner statements including allowable subject matter."""
    statement_type: str  # "Allowable Subject Matter", "Suggestion", "Interview Summary"
    content: str
    page_number: Optional[str] = None


# ============================================================================
# DEADLINE CALCULATION
# ============================================================================

class DeadlineTier(BaseModel):
    """A single deadline tier with extension fee information."""
    deadline_date: str  # ISO format date string
    months_from_mailing: int
    months_extension: int  # 0 = no extension, 1-5 = extension months
    extension_fee_micro: int  # Micro entity fee in USD
    extension_fee_small: int  # Small entity fee in USD
    extension_fee_large: int  # Large entity fee in USD
    is_past: bool = False  # Whether this deadline has passed


class DeadlineCalculation(BaseModel):
    """Complete deadline calculation with all tiers."""
    mailing_date: str  # ISO format date string
    shortened_statutory_period: int  # Usually 3 months
    statutory_deadline: str  # The SSP deadline (no extension fee)
    maximum_deadline: str  # 6 months absolute deadline
    tiers: List[DeadlineTier] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)  # Any special notes (holiday adjustments, etc.)
    is_final_action: bool = False  # Final OA has different extension rules


# ============================================================================
# IDS (Information Disclosure Statement) Data
# ============================================================================

class IDSSubmission(BaseModel):
    """Information Disclosure Statement submission record."""
    submission_date: str  # Date the IDS was submitted
    paper_number: Optional[str] = None  # Paper number if assigned
    was_considered: bool = True  # Whether the IDS was considered by examiner


# ============================================================================
# Applicant Arguments Status
# ============================================================================

class ApplicantArgumentsStatus(BaseModel):
    """Status of applicant's prior arguments."""
    status: str  # "moot", "persuasive", "not persuasive", "considered"
    affected_claims: List[str] = Field(default_factory=list)
    reason: Optional[str] = None  # e.g., "moot in view of the new grounds of rejection"


# ============================================================================
# HEADER - ENHANCED with new fields
# ============================================================================

class OfficeActionHeader(BaseModel):
    """Office Action header with complete field extraction."""
    application_number: Optional[str] = None
    filing_date: Optional[str] = None
    patent_office: str = "USPTO"
    office_action_date: Optional[str] = None  # Mailing date
    office_action_type: Optional[str] = None  # "Non-Final", "Final", "Advisory", "Restriction"
    examiner_name: Optional[str] = None
    art_unit: Optional[str] = None
    attorney_docket_number: Optional[str] = None
    confirmation_number: Optional[str] = None
    response_deadline: Optional[str] = None

    # Inventor and applicant info
    first_named_inventor: Optional[str] = None
    applicant_name: Optional[str] = None
    title_of_invention: Optional[str] = None

    # Contact info
    customer_number: Optional[str] = None
    examiner_phone: Optional[str] = None
    examiner_email: Optional[str] = None
    examiner_type: Optional[str] = None  # "Primary Examiner" or "Assistant Examiner"

    # ══════════════════════════════════════════════════════════════════════════
    # NEW FIELDS - Supervisor and additional contact info
    # ══════════════════════════════════════════════════════════════════════════
    supervisor_name: Optional[str] = None  # Supervisory Patent Examiner name
    supervisor_phone: Optional[str] = None  # Supervisor's phone number
    fax_number: Optional[str] = None  # USPTO fax number for the art unit

    # ══════════════════════════════════════════════════════════════════════════
    # NEW FIELDS - Extension and deadline details
    # ══════════════════════════════════════════════════════════════════════════
    statutory_period_months: Optional[int] = None  # Usually 3 months
    max_extension_months: Optional[int] = None  # Usually 6 months total

    # Priority and continuity data
    foreign_priority: List[ForeignPriorityInfo] = Field(default_factory=list)
    parent_applications: List[ParentApplicationInfo] = Field(default_factory=list)


# ============================================================================
# MAIN EXTRACTED DATA MODEL - ENHANCED
# ============================================================================

class OfficeActionExtractedData(MongoBaseModel):
    """Complete extracted data from an Office Action."""
    header: OfficeActionHeader
    claims_status: List[ClaimStatus] = Field(default_factory=list)
    rejections: List[Rejection] = Field(default_factory=list)
    objections: List[Objection] = Field(default_factory=list)
    other_statements: List[ExaminerStatement] = Field(default_factory=list)
    prosecution_history_summary: Optional[str] = None

    # Consolidated reference list with cross-references
    all_references: List[PriorArtReference] = Field(default_factory=list)
    reference_links: List[RejectionReferenceLink] = Field(default_factory=list)

    # Calculated deadlines
    deadline_calculation: Optional[DeadlineCalculation] = None

    # ══════════════════════════════════════════════════════════════════════════
    # NEW FIELDS - Amended claims tracking
    # ══════════════════════════════════════════════════════════════════════════
    amended_claims: List[str] = Field(default_factory=list)  # Claims that were amended in this response
    previously_amended_claims: List[str] = Field(default_factory=list)  # Claims previously amended
    new_claims: List[str] = Field(default_factory=list)  # Newly added claims
    cancelled_claims: List[str] = Field(default_factory=list)  # Cancelled claim numbers

    # ══════════════════════════════════════════════════════════════════════════
    # NEW FIELDS - IDS tracking
    # ══════════════════════════════════════════════════════════════════════════
    ids_submissions: List[IDSSubmission] = Field(default_factory=list)  # All IDS submissions

    # ══════════════════════════════════════════════════════════════════════════
    # NEW FIELDS - Applicant arguments status
    # ══════════════════════════════════════════════════════════════════════════
    applicant_arguments: List[ApplicantArgumentsStatus] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "header": {
                    "application_number": "16/123,456",
                    "filing_date": "2020-01-15",
                    "office_action_date": "2023-01-01",
                    "office_action_type": "Non-Final",
                    "response_deadline": "2023-04-01",
                    "title_of_invention": "Method and System for Data Processing",
                    "first_named_inventor": "John Smith",
                    "examiner_name": "Jane Doe",
                    "art_unit": "2123",
                    "supervisor_name": "Boris Gorney",
                    "supervisor_phone": "5712705626",
                    "fax_number": "571-273-8300",
                    "statutory_period_months": 3,
                    "max_extension_months": 6
                },
                "claims_status": [
                    {"claim_number": "1", "status": "Rejected", "dependency_type": "Independent"},
                    {"claim_number": "2", "status": "Rejected", "dependency_type": "Dependent", "parent_claim": "1"}
                ],
                "amended_claims": ["1", "8", "12", "16", "17", "18"],
                "ids_submissions": [
                    {"submission_date": "5/11/2020", "was_considered": True},
                    {"submission_date": "11/17/2020", "was_considered": True}
                ],
                "applicant_arguments": [
                    {
                        "status": "moot",
                        "affected_claims": ["1", "2", "19", "23"],
                        "reason": "moot in view of the new grounds of rejection"
                    }
                ],
                "rejections": [
                    {
                        "rejection_type": "103",
                        "rejection_type_normalized": "103",
                        "statutory_basis": "35 U.S.C. 103",
                        "is_aia": True,
                        "affected_claims": ["1", "2"],
                        "examiner_reasoning": "Claims 1-2 are obvious over Smith in view of Jones.",
                        "cited_prior_art": [
                            {
                                "reference_id": "ref_1",
                                "reference_type": "US Patent",
                                "identifier": "US 9,999,999 B2",
                                "short_name": "Smith"
                            }
                        ],
                        "prior_art_combinations": [
                            {
                                "primary_reference_id": "ref_1",
                                "secondary_reference_ids": ["ref_2"],
                                "motivation_to_combine": "One of ordinary skill would have been motivated to combine..."
                            }
                        ]
                    }
                ],
                "all_references": [
                    {
                        "reference_id": "ref_1",
                        "reference_type": "US Patent",
                        "identifier": "US 9,999,999 B2",
                        "short_name": "Smith",
                        "used_in_rejection_indices": [0]
                    }
                ]
            }
        }
