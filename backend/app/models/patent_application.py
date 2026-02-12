from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from app.models.common import MongoBaseModel, PyObjectId

class WorkflowStatus(str, Enum):
    UPLOADED = "uploaded"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    GENERATED = "generated"
    DOWNLOADED = "downloaded"

class Inventor(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    suffix: Optional[str] = None
    prefix: Optional[str] = None  # e.g., "Dr.", "Mr."
    name: Optional[str] = None  # Full name for backward compatibility or display
    
    # Residence information (where the inventor LIVES)
    street_address: Optional[str] = None # mailing_address
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    residence_country: Optional[str] = None  # NEW: Separate field for residence country
    
    # Citizenship (nationality) - distinct from residence
    citizenship: Optional[str] = None
    
    # Additional mailing address fields
    mail_address1: Optional[str] = None
    mail_address2: Optional[str] = None
    mail_city: Optional[str] = None
    mail_state: Optional[str] = None
    mail_postcode: Optional[str] = None
    mail_country: Optional[str] = None
    
    extraction_confidence: Optional[float] = None

class Applicant(BaseModel):
    name: Optional[str] = None
    org_name: Optional[str] = None  # Organization name
    is_organization: Optional[bool] = True  # NEW: Flag for organization vs individual
    
    # Individual name fields (for non-organization applicants)
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    
    # Authority type for applicant
    authority: Optional[str] = "assignee"  # NEW: "assignee", "legal-representative", etc.
    
    # Address information
    street_address: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    
    # Contact information
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None


# ── NEW: Correspondence Address model ──────────────────────────────────────────
class CorrespondenceAddress(BaseModel):
    """Correspondence address for patent communications (typically a law firm)."""
    name: Optional[str] = None          # Firm or person name
    name2: Optional[str] = None         # Secondary name line
    address1: Optional[str] = None      # Street address line 1
    address2: Optional[str] = None      # Street address line 2
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postcode: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    customer_number: Optional[str] = None  # USPTO customer number
# ────────────────────────────────────────────────────────────────────────────────

class PatentApplicationMetadata(BaseModel):
    title: Optional[str] = None
    application_number: Optional[str] = None
    filing_date: Optional[str] = None  # Keep as string for extraction, convert later
    entity_status: Optional[str] = None
    inventors: List[Inventor] = []
    applicant: Optional[Applicant] = None  # Keep for backward compatibility
    applicants: List[Applicant] = []  # New field for multiple applicants
    total_drawing_sheets: Optional[int] = None
    extraction_confidence: Optional[float] = None
    debug_reasoning: Optional[str] = Field(None, alias="_debug_reasoning")

    # ── NEW: 3 previously missing fields ───────────────────────────────────────
    correspondence_address: Optional[CorrespondenceAddress] = None
    application_type: Optional[str] = None       # "utility", "design", "plant", "provisional", "reissue"
    suggested_figure: Optional[str] = None        # Representative figure number, e.g. "1", "2A"
    # ───────────────────────────────────────────────────────────────────────────
    
    # ── VALIDATION: Track original inventor count for validation ───────────────
    original_inventor_count: Optional[int] = None  # Store original count from extraction
    # ───────────────────────────────────────────────────────────────────────────

class PatentApplicationBase(BaseModel):
    application_number: Optional[str] = None
    title: Optional[str] = None
    entity_status: Optional[str] = None
    filing_date: Optional[datetime] = None
    inventors: List[Inventor] = []
    applicant: Optional[Applicant] = None  # Keep for backward compatibility
    applicants: List[Applicant] = []  # New field for multiple applicants
    total_drawing_sheets: Optional[int] = None
    workflow_status: WorkflowStatus = WorkflowStatus.UPLOADED

    # ── NEW: 3 previously missing fields (persisted to DB + API response) ──────
    correspondence_address: Optional[CorrespondenceAddress] = None
    application_type: Optional[str] = None
    suggested_figure: Optional[str] = None
    # ───────────────────────────────────────────────────────────────────────────

class PatentApplicationCreate(PatentApplicationBase):
    source_document_ids: List[PyObjectId] = []

class PatentApplicationInDB(MongoBaseModel, PatentApplicationBase):
    source_document_ids: List[PyObjectId] = []
    generated_document_ids: List[PyObjectId] = []
    created_by: PyObjectId
    updated_by: Optional[PyObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PatentApplicationResponse(MongoBaseModel, PatentApplicationBase):
    source_document_ids: List[str] = []
    generated_document_ids: List[str] = []
    created_by: str
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime