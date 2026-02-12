# Comprehensive ADS Enhancement Implementation Plan

## Overview
This document provides a complete implementation plan to extract all missing USPTO Form PTO/SB/14 fields from patent documents, following the same strategy as the current working extraction system.

## Current System Analysis ✅

**Working Components:**
- Two-step extraction process (Evidence Gathering → JSON Generation)
- Basic fields: Title, Application Number, Entity Status, Inventors, Applicants
- Multi-applicant detection and extraction
- Frontend display and editing capabilities
- ADS PDF generation

**Missing Critical Fields:**
1. **Application Information**: Filing Date, Attorney Docket Number, Confirmation Number, Application Type
2. **Correspondence Information**: Law firm details, customer number, contact information
3. **Attorney/Agent Information**: Name, registration number, contact details
4. **Priority Claims**: Domestic benefit claims, foreign priority claims
5. **Enhanced Applicant Details**: Applicant type, authority to apply, entity classification
6. **Classification Information**: Art unit, classification codes

## Phase 1: Backend Data Model Extensions

### 1.1 Enhanced Application Information Model
```python
# File: backend/app/models/enhanced_extraction.py (extend existing)

class EnhancedApplicationInfo(BaseModel):
    """Enhanced application information for complete ADS support"""
    filing_date: Optional[str] = None
    attorney_docket_number: Optional[str] = None
    confirmation_number: Optional[str] = None
    application_type: Optional[str] = None  # Utility, Design, Plant, Reissue, etc.
    
class ApplicationTypeEnum(str, Enum):
    """Application types for USPTO forms"""
    UTILITY = "utility"
    DESIGN = "design"
    PLANT = "plant"
    REISSUE = "reissue"
    PROVISIONAL = "provisional"
    NONPROVISIONAL = "nonprovisional"
    PCT = "pct"
```

### 1.2 Correspondence Information Model
```python
class CorrespondenceInfo(BaseModel):
    """Correspondence address and contact information"""
    firm_name: Optional[str] = None
    attorney_name: Optional[str] = None
    street_address: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone_number: Optional[str] = None
    fax_number: Optional[str] = None
    email_address: Optional[str] = None
    customer_number: Optional[str] = None
```

### 1.3 Attorney/Agent Information Model
```python
class AttorneyAgentInfo(BaseModel):
    """Attorney or agent information"""
    name: Optional[str] = None
    registration_number: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    firm_name: Optional[str] = None
    is_attorney: bool = True  # True for attorney, False for agent
```

### 1.4 Priority Claims Models
```python
class DomesticPriorityClaim(BaseModel):
    """Domestic benefit claim information"""
    parent_application_number: Optional[str] = None
    filing_date: Optional[str] = None
    application_type: Optional[str] = None  # Provisional, Nonprovisional, PCT
    status: Optional[str] = None  # Pending, Patented, Abandoned
    relationship_type: Optional[str] = None  # Continuation, Divisional, CIP

class ForeignPriorityClaim(BaseModel):
    """Foreign priority claim information"""
    country_code: Optional[str] = None
    application_number: Optional[str] = None
    filing_date: Optional[str] = None
    certified_copy_filed: Optional[bool] = None
    certified_copy_status: Optional[str] = None
```

### 1.5 Enhanced Applicant Information
```python
class EnhancedApplicantInfo(BaseModel):
    """Enhanced applicant information with additional ADS fields"""
    applicant_type: Optional[str] = None  # Inventor, Assignee, Legal Representative
    authority_to_apply: Optional[str] = None
    country_of_incorporation: Optional[str] = None
    entity_type: Optional[str] = None  # Corporation, LLC, University, Individual, etc.
    
class ApplicantTypeEnum(str, Enum):
    """Applicant types for ADS forms"""
    INVENTOR = "inventor"
    ASSIGNEE = "assignee"
    LEGAL_REPRESENTATIVE = "legal_representative"
    PARTIAL_ASSIGNEE = "partial_assignee"

class EntityTypeEnum(str, Enum):
    """Entity types for applicants"""
    CORPORATION = "corporation"
    LLC = "llc"
    PARTNERSHIP = "partnership"
    INDIVIDUAL = "individual"
    UNIVERSITY = "university"
    GOVERNMENT = "government"
    OTHER = "other"
```

### 1.6 Classification Information Model
```python
class ClassificationInfo(BaseModel):
    """Patent classification information"""
    suggested_art_unit: Optional[str] = None
    uspc_classification: Optional[str] = None
    ipc_classification: Optional[str] = None
    cpc_classification: Optional[str] = None
```

### 1.7 Updated Main Extraction Result Model
```python
# Extend EnhancedExtractionResult in enhanced_extraction.py
class EnhancedExtractionResult(BaseModel):
    # Existing fields...
    title: Optional[str] = None
    application_number: Optional[str] = None
    filing_date: Optional[str] = None
    entity_status: Optional[str] = None
    attorney_docket_number: Optional[str] = None
    total_drawing_sheets: Optional[int] = None
    
    # NEW ENHANCED FIELDS
    confirmation_number: Optional[str] = None
    application_type: Optional[str] = None
    
    # Enhanced information objects
    correspondence_info: Optional[CorrespondenceInfo] = None
    attorney_agent_info: Optional[AttorneyAgentInfo] = None
    classification_info: Optional[ClassificationInfo] = None
    
    # Priority claims
    domestic_priority_claims: List[DomesticPriorityClaim] = []
    foreign_priority_claims: List[ForeignPriorityClaim] = []
    
    # Existing fields with enhancements
    inventors: List[EnhancedInventor] = []
    applicants: List[EnhancedApplicant] = []
    
    # Metadata and validation (existing)
    quality_metrics: QualityMetrics
    field_validations: List[FieldValidationResult] = []
    cross_field_validations: List[CrossFieldValidationResult] = []
    document_evidence: Optional[DocumentEvidence] = None
    extraction_metadata: ExtractionMetadata
```

## Phase 2: Enhanced LLM Extraction Prompts

### 2.1 Enhanced Evidence Gathering Prompts
```python
# File: backend/app/services/enhanced_extraction_service.py (extend existing)

def _get_enhanced_evidence_prompt(self) -> str:
    """Enhanced evidence gathering prompt for complete ADS extraction"""
    return """
You are a highly accurate Data Extraction Specialist analyzing a USPTO patent document. Your mission is to find ALL information required for a complete Application Data Sheet (ADS).

**CRITICAL INSTRUCTIONS:**
1. **SCAN THE ENTIRE DOCUMENT** - Check ALL pages systematically
2. **QUOTE RAW TEXT** - Extract exact text, never paraphrase or interpret
3. **NO HALLUCINATION** - Only extract what is visually present in the document
4. **DOCUMENT SOURCES** - Note page numbers and sections for all findings
5. **BE EXHAUSTIVE** - Better to over-extract than miss critical data

**COMPREHENSIVE EXTRACTION REQUIREMENTS:**

### 1. APPLICATION INFORMATION (ENHANCED)
**Search for:**
- Filing Date (various formats: MM/DD/YYYY, Month DD, YYYY, etc.)
- Attorney Docket Number (alphanumeric codes, often in headers)
- Confirmation Number (if available)
- Application Type (Utility, Design, Plant, Reissue, Provisional, etc.)

**Evidence Pattern:**
- Field Type: "[Filing Date/Attorney Docket/Confirmation Number/Application Type]"
- Text Found: "[Exact text containing the information]"
- Source Location: Page X, Section Y
- Confidence: High/Medium/Low

### 2. CORRESPONDENCE INFORMATION (CRITICAL NEW SECTION)
**Search for:**
- Law firm names (often in letterhead, headers, footers)
- Attorney names and titles
- Business addresses (separate from inventor addresses)
- Customer numbers (5-6 digit numbers, often labeled "Customer No.")
- Phone numbers, fax numbers, email addresses
- "Correspondence Address" sections

**Evidence Pattern:**
- Correspondence Type: "[Law Firm/Attorney/Address/Contact]"
- Text Found: "[Exact text with contact information]"
- Source Location: Page X, Section Y
- Confidence: High/Medium/Low

### 3. ATTORNEY/AGENT INFORMATION (NEW SECTION)
**Search for:**
- Attorney or agent names
- Registration numbers (format: 12,345 or Reg. No. 12345)
- Attorney contact information
- Bar admission information
- "Attorney of Record" or "Agent" designations

**Evidence Pattern:**
- Attorney Info Type: "[Name/Registration Number/Contact]"
- Text Found: "[Exact attorney/agent information]"
- Source Location: Page X, Section Y
- Confidence: High/Medium/Low

### 4. PRIORITY CLAIMS INFORMATION (ENHANCED)
**Search for:**
- "Claims benefit of" statements
- Parent application numbers and filing dates
- Provisional application references
- Foreign priority claims with country codes
- Continuation, divisional, or CIP relationships
- PCT application references

**Evidence Pattern:**
- Priority Type: "[Domestic Benefit/Foreign Priority]"
- Claim Details: "[Parent app number, filing date, relationship]"
- Source Location: Page X, Section Y
- Confidence: High/Medium/Low

### 5. ENHANCED APPLICANT INFORMATION
**Search for:**
- Applicant type designations (Inventor, Assignee, Legal Representative)
- Authority to apply statements
- Country of incorporation (for corporate applicants)
- Entity type (Corporation, LLC, University, etc.)
- Assignment document references

**Evidence Pattern:**
- Applicant Detail Type: "[Type/Authority/Incorporation/Entity]"
- Text Found: "[Exact applicant classification information]"
- Source Location: Page X, Section Y
- Confidence: High/Medium/Low

### 6. CLASSIFICATION INFORMATION (NEW SECTION)
**Search for:**
- Art Unit numbers
- USPC classification codes
- IPC classification codes
- CPC classification codes
- Examiner assignments

**Evidence Pattern:**
- Classification Type: "[Art Unit/USPC/IPC/CPC]"
- Code Found: "[Exact classification code or art unit]"
- Source Location: Page X, Section Y
- Confidence: High/Medium/Low

### 7. EXISTING SECTIONS (ENHANCED)
Continue with existing comprehensive extraction for:
- Title of Invention
- Application Number
- Entity Status
- Inventor Information (with complete addresses and citizenship)
- Applicant/Company Information (with complete details)

**OUTPUT FORMAT:**
Provide structured evidence for each category found, with special emphasis on the NEW sections (Correspondence, Attorney/Agent, Priority Claims, Classification).
"""
```

### 2.2 Enhanced JSON Generation Prompts
```python
def create_enhanced_json_generation_prompt(self, document_evidence: DocumentEvidence) -> str:
    """Enhanced JSON generation prompt for complete ADS data"""
    evidence_summary = self._summarize_enhanced_evidence(document_evidence)
    
    return f"""
Based ONLY on the evidence gathered below, generate a single, valid JSON object with ALL ADS information found.

**CRITICAL RULES:**
- Use `null` if a specific field is absolutely not found in the evidence
- Format all dates as "YYYY-MM-DD" (convert from any format found)
- Ensure phone numbers are in standard format
- Do NOT make up, assume, or infer any data not explicitly found in evidence

**EVIDENCE SUMMARY:**
{evidence_summary}

**COMPREHENSIVE JSON STRUCTURE:**

{{
  "title": "String from evidence or null",
  "application_number": "String from evidence or null",
  "filing_date": "YYYY-MM-DD format or null",
  "entity_status": "String from evidence or null",
  "attorney_docket_number": "String from evidence or null",
  "confirmation_number": "String from evidence or null",
  "application_type": "String from evidence or null",
  "total_drawing_sheets": "Integer from evidence or null",
  
  "correspondence_info": {{
    "firm_name": "String from evidence or null",
    "attorney_name": "String from evidence or null",
    "street_address": "String from evidence or null",
    "address_line_2": "String from evidence or null",
    "city": "String from evidence or null",
    "state": "String from evidence or null",
    "postal_code": "String from evidence or null",
    "country": "String from evidence or null",
    "phone_number": "String from evidence or null",
    "fax_number": "String from evidence or null",
    "email_address": "String from evidence or null",
    "customer_number": "String from evidence or null"
  }},
  
  "attorney_agent_info": {{
    "name": "String from evidence or null",
    "registration_number": "String from evidence or null",
    "phone_number": "String from evidence or null",
    "email_address": "String from evidence or null",
    "firm_name": "String from evidence or null",
    "is_attorney": true/false
  }},
  
  "domestic_priority_claims": [
    {{
      "parent_application_number": "String from evidence",
      "filing_date": "YYYY-MM-DD format",
      "application_type": "String from evidence",
      "status": "String from evidence or null",
      "relationship_type": "String from evidence or null"
    }}
  ],
  
  "foreign_priority_claims": [
    {{
      "country_code": "String from evidence",
      "application_number": "String from evidence",
      "filing_date": "YYYY-MM-DD format",
      "certified_copy_filed": true/false/null,
      "certified_copy_status": "String from evidence or null"
    }}
  ],
  
  "classification_info": {{
    "suggested_art_unit": "String from evidence or null",
    "uspc_classification": "String from evidence or null",
    "ipc_classification": "String from evidence or null",
    "cpc_classification": "String from evidence or null"
  }},
  
  "inventors": [
    {{
      "given_name": "String from evidence",
      "middle_name": "Complete middle name - DO NOT TRUNCATE",
      "family_name": "String from evidence",
      "full_name": "String from evidence or null",
      "street_address": "String from evidence",
      "city": "String from evidence",
      "state": "String from evidence",
      "postal_code": "Complete postal code",
      "country": "String from evidence",
      "citizenship": "REQUIRED - String from evidence",
      "completeness": "complete|partial_name|partial_address|incomplete",
      "confidence_score": "0.0-1.0 (float)"
    }}
  ],
  
  "applicants": [
    {{
      "applicant_sequence": 1,
      "is_assignee": true/false,
      "organization_name": "String from evidence or null",
      "individual_given_name": "String from evidence or null",
      "individual_family_name": "String from evidence or null",
      "street_address": "String from evidence",
      "city": "String from evidence",
      "state": "String from evidence",
      "postal_code": "String from evidence",
      "country": "String from evidence",
      "customer_number": "String from evidence or null",
      "email_address": "String from evidence or null",
      "applicant_type": "inventor|assignee|legal_representative|null",
      "authority_to_apply": "String from evidence or null",
      "country_of_incorporation": "String from evidence or null",
      "entity_type": "corporation|llc|individual|university|other|null",
      "relationship_to_inventors": "same_as_inventor|separate_entity|unclear",
      "completeness": "complete|partial_name|partial_address|incomplete",
      "confidence_score": "0.0-1.0 (float)"
    }}
  ]
}}
"""
```

## Phase 3: Frontend Component Extensions

### 3.1 Enhanced Application Wizard Interface
```typescript
// File: frontend/src/lib/types.ts (extend existing)

interface CorrespondenceInfo {
  firm_name?: string;
  attorney_name?: string;
  street_address?: string;
  address_line_2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  phone_number?: string;
  fax_number?: string;
  email_address?: string;
  customer_number?: string;
}

interface AttorneyAgentInfo {
  name?: string;
  registration_number?: string;
  phone_number?: string;
  email_address?: string;
  firm_name?: string;
  is_attorney?: boolean;
}

interface DomesticPriorityClaim {
  parent_application_number?: string;
  filing_date?: string;
  application_type?: string;
  status?: string;
  relationship_type?: string;
}

interface ForeignPriorityClaim {
  country_code?: string;
  application_number?: string;
  filing_date?: string;
  certified_copy_filed?: boolean;
  certified_copy_status?: string;
}

interface ClassificationInfo {
  suggested_art_unit?: string;
  uspc_classification?: string;
  ipc_classification?: string;
  cpc_classification?: string;
}

interface EnhancedApplicationMetadata {
  // Existing fields
  title?: string;
  application_number?: string;
  filing_date?: string;
  entity_status?: string;
  attorney_docket_number?: string;
  total_drawing_sheets?: number;
  
  // New enhanced fields
  confirmation_number?: string;
  application_type?: string;
  
  // Enhanced information objects
  correspondence_info?: CorrespondenceInfo;
  attorney_agent_info?: AttorneyAgentInfo;
  classification_info?: ClassificationInfo;
  
  // Priority claims
  domestic_priority_claims?: DomesticPriorityClaim[];
  foreign_priority_claims?: ForeignPriorityClaim[];
  
  // Existing arrays
  inventors: Inventor[];
  applicants: Applicant[];
}
```

### 3.2 New Frontend Components

#### 3.2.1 Correspondence Information Card
```typescript
// File: frontend/src/components/wizard/CorrespondenceInfoCard.tsx

export const CorrespondenceInfoCard: React.FC<{
  correspondenceInfo: CorrespondenceInfo;
  setCorrespondenceInfo: (info: CorrespondenceInfo) => void;
}> = ({ correspondenceInfo, setCorrespondenceInfo }) => {
  // Component for editing correspondence address and contact information
  // Includes fields for law firm, attorney name, address, phone, email, customer number
};
```

#### 3.2.2 Attorney/Agent Information Card
```typescript
// File: frontend/src/components/wizard/AttorneyAgentInfoCard.tsx

export const AttorneyAgentInfoCard: React.FC<{
  attorneyInfo: AttorneyAgentInfo;
  setAttorneyInfo: (info: AttorneyAgentInfo) => void;
}> = ({ attorneyInfo, setAttorneyInfo }) => {
  // Component for editing attorney/agent information
  // Includes name, registration number, contact details
};
```

#### 3.2.3 Priority Claims Table
```typescript
// File: frontend/src/components/wizard/PriorityClaimsTable.tsx

export const PriorityClaimsTable: React.FC<{
  domesticClaims: DomesticPriorityClaim[];
  foreignClaims: ForeignPriorityClaim[];
  setDomesticClaims: (claims: DomesticPriorityClaim[]) => void;
  setForeignClaims: (claims: ForeignPriorityClaim[]) => void;
}> = ({ domesticClaims, foreignClaims, setDomesticClaims, setForeignClaims }) => {
  // Component for managing priority claims
  // Separate sections for domestic and foreign claims
};
```

#### 3.2.4 Enhanced Application Details Card
```typescript
// File: frontend/src/components/wizard/ApplicationDetailsCard.tsx

export const ApplicationDetailsCard: React.FC<{
  metadata: EnhancedApplicationMetadata;
  setMetadata: (metadata: EnhancedApplicationMetadata) => void;
}> = ({ metadata, setMetadata }) => {
  // Enhanced component for application details
  // Includes all new fields: filing date, attorney docket, confirmation number, application type
};
```

#### 3.2.5 Classification Information Card
```typescript
// File: frontend/src/components/wizard/ClassificationInfoCard.tsx

export const ClassificationInfoCard: React.FC<{
  classificationInfo: ClassificationInfo;
  setClassificationInfo: (info: ClassificationInfo) => void;
}> = ({ classificationInfo, setClassificationInfo }) => {
  // Component for patent classification information
  // Art unit, USPC, IPC, CPC codes
};
```

### 3.3 Enhanced Application Wizard Layout
```typescript
// File: frontend/src/components/wizard/ApplicationWizard.tsx (extend existing)

// Add new sections to the review step:
{step === 'review' && (
  <Card>
    <CardContent className="space-y-8">
      {/* Existing Application Details - Enhanced */}
      <ApplicationDetailsCard 
        metadata={metadata} 
        setMetadata={setMetadata} 
      />
      
      {/* NEW: Correspondence Information */}
      <div className="space-y-4 border border-neutral-200 rounded-xl p-4 bg-blue-50/50">
        <h3 className="font-medium text-base text-neutral-900">
          Correspondence Information
        </h3>
        <CorrespondenceInfoCard
          correspondenceInfo={metadata.correspondence_info || {}}
          setCorrespondenceInfo={(info) => setMetadata({...metadata, correspondence_info: info})}
        />
      </div>

      {/* NEW: Attorney/Agent Information */}
      <div className="space-y-4 border border-neutral-200 rounded-xl p-4 bg-green-50/50">
        <h3 className="font-medium text-base text-neutral-900">
          Attorney/Agent Information
        </h3>
        <AttorneyAgentInfoCard
          attorneyInfo={metadata.attorney_agent_info || {}}
          setAttorneyInfo={(info) => setMetadata({...metadata, attorney_agent_info: info})}
        />
      </div>

      {/* NEW: Priority Claims */}
      <div className="space-y-4 border border-neutral-200 rounded-xl p-4 bg-purple-50/50">
        <h3 className="font-medium text-base text-neutral-900">
          Priority Claims
        </h3>
        <PriorityClaimsTable
          domesticClaims={metadata.domestic_priority_claims || []}
          foreignClaims={metadata.foreign_priority_claims || []}
          setDomesticClaims={(claims) => setMetadata({...metadata, domestic_priority_claims: claims})}
          setForeignClaims={(claims) => setMetadata({...metadata, foreign_priority_claims: claims})}
        />
      </div>

      {/* NEW: Classification Information */}
      <div className="space-y-4 border border-neutral-200 rounded-xl p-4 bg-yellow-50/50">
        <h3 className="font-medium text-base text-neutral-900">
          Classification Information
        </h3>
        <ClassificationInfoCard
          classificationInfo={metadata.classification_info || {}}
          setClassificationInfo={(info) => setMetadata({...metadata, classification_info: info})}
        />
      </div>

      {/* Existing Applicant Information - Enhanced */}
      <div className="space-y-4 border border-neutral-200 rounded-xl p-4 bg-neutral-50/50">
        <h3 className="font-medium text-base text-neutral-900">
          Applicant / Company Information ({metadata.applicants.length})
        </h3>
        <ApplicantTable
          applicants={metadata.applicants}
          setApplicants={(applicants) => setMetadata({...metadata, applicants})}
        />
      </div>

      {/* Existing Inventor Information */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">
          Inventors ({metadata.inventors.length})
        </label>
        <InventorTable
          inventors={metadata.inventors}
          setInventors={(invs) => setMetadata({...metadata, inventors: invs})}
        />
      </div>
    </CardContent>
  </Card>
)}
```

## Phase 4: Enhanced ADS Generator

### 4.1 Updated ADS Generator with All Fields
```python
# File: backend/app/services/ads_generator.py (extend existing)

class EnhancedADSGenerator:
    def generate_enhanced_ads_pdf(self, data: EnhancedApplicationMetadata, output_path: str) -> str:
        """
        Generates a complete ADS PDF with all available fields populated
        """
        # Enhanced field mapping for all new fields
        enhanced_field_data = {
            # Existing basic fields
            'Title': data.title or "",
            'ApplicationNumber': data.application_number or "",
            'FilingDate': data.filing_date or "",
            'EntityStatus': data.entity_status or "",
            'AttorneyDocketNumber': data.attorney_docket_number or "",
            'ConfirmationNumber': data.confirmation_number or "",
            'ApplicationType': data.application_type or "",
            'TotalDrawingSheets': str(data.total_drawing_sheets or ""),
            
            # Correspondence information
            'CorrespondenceFirmName': data.correspondence_info.firm_name if data.correspondence_info else "",
            'CorrespondenceAttorneyName': data.correspondence_info.attorney_name if data.correspondence_info else "",
            'CorrespondenceStreetAddress': data.correspondence_info.street_address if data.correspondence_info else "",
            'CorrespondenceCity': data.correspondence_info.city if data.correspondence_info else "",
            'CorrespondenceState': data.correspondence_info.state if data.correspondence_info else "",
            'CorrespondencePostalCode': data.correspondence_info.postal_code if data.correspondence_info else "",
            'CorrespondenceCountry': data.correspondence_info.country if data.correspondence_info else "",
            'CorrespondencePhone': data.correspondence_info.phone_number if data.correspondence_info else "",
            'CorrespondenceFax': data.correspondence_info.fax_number if data.correspondence_info else "",
            'CorrespondenceEmail': data.correspondence_info.email_address if data.correspondence_info else "",
            'CustomerNumber': data.correspondence_info.customer_number if data.correspondence_info else "",
            
            # Attorney/Agent information
            'AttorneyName': data.attorney_agent_info.name if data.attorney_agent_info else "",
            'RegistrationNumber': data.attorney_agent_info.registration_number if data.attorney_agent_info else "",
            'AttorneyPhone': data.attorney_agent_info.phone_number if data.attorney_agent_info else "",
            'AttorneyEmail': data.attorney_agent_info.email_address if data.attorney_agent_info else "",
            
            # Classification information
            'ArtUnit': data.classification_info.suggested_art_unit if data.classification_info else "",
            'USPCClassification': data.classification_info.uspc_classification if data.classification_info else "",
            'IPCClassification': data.classification_info.ipc_classification if data.classification_info else "",
            'CPCClassification': data.classification_info.cpc_classification if data.classification_info else "",
        }
        
        # Handle priority claims (multiple entries)
        if data.domestic_priority_claims:
            for i, claim in enumerate(data.domestic_priority_claims[:5]):  # Limit to 5 claims
                enhanced_field_data[f'DomesticClaim_{i+1}_AppNumber'] = claim.parent_application_number or ""
                enhanced_field_data[f'DomesticClaim_{i+1}_FilingDate'] = claim.filing_date or ""
                enhanced_field_data[f'DomesticClaim_{i+1}_Type'] = claim.application_type or ""
                enhanced_field_data[f'DomesticClaim_{i+1}_Status'] = claim.status or ""
        
        if data.foreign_priority_claims:
            for i, claim in enumerate(data.foreign_priority_claims[:5]):  # Limit to 5 claims
                enhanced_field_data[f'ForeignClaim_{i+1}_Country'] = claim.country_code or ""
                enhanced_field_data[f'ForeignClaim_{i+1}_AppNumber'] = claim.application_number or ""
                enhanced_field_data[f'ForeignClaim_{i+1}_FilingDate'] = claim.filing_date or ""
                enhanced_field_data[f'ForeignClaim_{i+1}_CertifiedCopy'] = "Yes" if claim.certified_copy_filed else "No"
        
        # Enhanced inventor mapping (existing logic with new fields)
        main_inventors = data.inventors[:self.MAX_INVENTORS_ON_MAIN_FORM] if data.inventors else []
        for idx, inv in enumerate(main_inventors):
            i = idx + 1
            enhanced_field_data[f'GivenName_{i}'] = inv.first_name or ""
            enhanced_field_data[f'MiddleName_{i}'] = inv.middle_name or ""
            enhanced_field_data[f'FamilyName_{i}'] = inv.last_name or ""
            enhanced_field_data[f'City_{i}'] = inv.city or ""
            enhanced_field_data[f'State_{i}'] = inv.state or ""
            enhanced_field_data[f'Country_{i}'] = inv.country or ""
            enhanced_field_data[f'PostalCode_{i}'] = inv.zip_code or ""
            enhanced_field_data[f'Citizenship_{i}'] = inv.citizenship or ""
            enhanced_field_data[f'Address_{i}'] = inv.street_address or ""
        
        # Enhanced applicant mapping with new fields
        main_applicants = data.applicants[:3] if data.applicants else []  # Limit to 3 applicants on main form
        for idx, app in enumerate(main_applicants):
            i = idx + 1
            enhanced_field_data[f'ApplicantName_{i}'] = app.organization_name or f"{app.individual_given_name or ''} {app.individual_family_name or ''}".strip()
            enhanced_field_data[f'ApplicantAddress_{i}'] = app.street_address or ""
            enhanced_field_data[f'ApplicantCity_{i}'] = app.city or ""
            enhanced_field_data[f'ApplicantState_{i}'] = app.state or ""
            enhanced_field_data[f'ApplicantPostalCode_{i}'] = app.postal_code or ""
            enhanced_field_data[f'ApplicantCountry_{i}'] = app.country or ""
            enhanced_field_data[f'ApplicantType_{i}'] = app.applicant_type or ""


## Phase 4: Enhanced ADS Generator

### 4.1 Updated ADS Generator with All Fields
```python
# File: backend/app/services/ads_generator.py (extend existing)

class EnhancedADSGenerator:
    def generate_enhanced_ads_pdf(self, data: EnhancedApplicationMetadata, output_path: str) -> str:
        """
        Generates a complete ADS PDF with all available fields populated
        """
        # Enhanced field mapping for all new fields
        enhanced_field_data = {
            # Existing basic fields
            'Title': data.title or "",
            'ApplicationNumber': data.application_number or "",
            'FilingDate': data.filing_date or "",
            'EntityStatus': data.entity_status or "",
            'AttorneyDocketNumber': data.attorney_docket_number or "",
            'ConfirmationNumber': data.confirmation_number or "",
            'ApplicationType': data.application_type or "",
            'TotalDrawingSheets': str(data.total_drawing_sheets or ""),
            
            # Correspondence information
            'CorrespondenceFirmName': data.correspondence_info.firm_name if data.correspondence_info else "",
            'CorrespondenceAttorneyName': data.correspondence_info.attorney_name if data.correspondence_info else "",
            'CorrespondenceStreetAddress': data.correspondence_info.street_address if data.correspondence_info else "",
            'CorrespondenceCity': data.correspondence_info.city if data.correspondence_info else "",
            'CorrespondenceState': data.correspondence_info.state if data.correspondence_info else "",
            'CorrespondencePostalCode': data.correspondence_info.postal_code if data.correspondence_info else "",
            'CorrespondenceCountry': data.correspondence_info.country if data.correspondence_info else "",
            'CorrespondencePhone': data.correspondence_info.phone_number if data.correspondence_info else "",
            'CorrespondenceFax': data.correspondence_info.fax_number if data.correspondence_info else "",
            'CorrespondenceEmail': data.correspondence_info.email_address if data.correspondence_info else "",
            'CustomerNumber': data.correspondence_info.customer_number if data.correspondence_info else "",
            
            # Attorney/Agent information
            'AttorneyName': data.attorney_agent_info.name if data.attorney_agent_info else "",
            'RegistrationNumber': data.attorney_agent_info.registration_number if data.attorney_agent_info else "",
            'AttorneyPhone': data.attorney_agent_info.phone_number if data.attorney_agent_info else "",
            'AttorneyEmail': data.attorney_agent_info.email_address if data.attorney_agent_info else "",
            
            # Classification information
            'ArtUnit': data.classification_info.suggested_art_unit if data.classification_info else "",
            'USPCClassification': data.classification_info.uspc_classification if data.classification_info else "",
            'IPCClassification': data.classification_info.ipc_classification if data.classification_info else "",
            'CPCClassification': data.classification_info.cpc_classification if data.classification_info else "",
        }
        
        # Handle priority claims (multiple entries)
        if data.domestic_priority_claims:
            for i, claim in enumerate(data.domestic_priority_claims[:5]):  # Limit to 5 claims
                enhanced_field_data[f'DomesticClaim_{i+1}_AppNumber'] = claim.parent_application_number or ""
                enhanced_field_data[f'DomesticClaim_{i+1}_FilingDate'] = claim.filing_date or ""
                enhanced_field_data[f'DomesticClaim_{i+1}_Type'] = claim.application_type or ""
                enhanced_field_data[f'DomesticClaim_{i+1}_Status'] = claim.status or ""
        
        if data.foreign_priority_claims:
            for i, claim in enumerate(data.foreign_priority_claims[:5]):  # Limit to 5 claims
                enhanced_field_data[f'ForeignClaim_{i+1}_Country'] = claim.country_code or ""
                enhanced_field_data[f'ForeignClaim_{i+1}_AppNumber'] = claim.application_number or ""
                enhanced_field_data[f'ForeignClaim_{i+1}_FilingDate'] = claim.filing_date or ""
                enhanced_field_data[f'ForeignClaim_{i+1}_CertifiedCopy'] = "Yes" if claim.certified_copy_filed else "No"
        
        # Continue with existing inventor and applicant mapping...
        return self._generate_pdf_with_enhanced_fields(enhanced_field_data, output_path)
```

## Phase 5: Enhanced Validation Framework

### 5.1 Field Validation Extensions
```python
# File: backend/app/services/validation_service.py (extend existing)

class EnhancedFieldValidator:
    def validate_attorney_docket_number(self, value: str) -> ValidationResult:
        """Validate attorney docket number format"""
        if not value:
            return ValidationResult(is_valid=True, normalized_value=None, confidence_score=1.0)
        
        # Common patterns: alphanumeric with hyphens, dots, underscores
        import re
        pattern = r'^[A-Za-z0-9._-]+$'
        is_valid = bool(re.match(pattern, value))
        
        return ValidationResult(
            is_valid=is_valid,
            errors=[] if is_valid else ["Invalid attorney docket number format"],
            normalized_value=value.strip() if is_valid else None,
            confidence_score=0.9 if is_valid else 0.1
        )
    
    def validate_confirmation_number(self, value: str) -> ValidationResult:
        """Validate USPTO confirmation number"""
        if not value:
            return ValidationResult(is_valid=True, normalized_value=None, confidence_score=1.0)
        
        # USPTO confirmation numbers are typically 4-digit numbers
        import re
        pattern = r'^\d{4}$'
        is_valid = bool(re.match(pattern, value))
        
        return ValidationResult(
            is_valid=is_valid,
            errors=[] if is_valid else ["Confirmation number should be 4 digits"],
            normalized_value=value.strip() if is_valid else None,
            confidence_score=0.9 if is_valid else 0.3
        )
    
    def validate_customer_number(self, value: str) -> ValidationResult:
        """Validate USPTO customer number"""
        if not value:
            return ValidationResult(is_valid=True, normalized_value=None, confidence_score=1.0)
        
        # Customer numbers are typically 5-6 digit numbers
        import re
        pattern = r'^\d{5,6}$'
        is_valid = bool(re.match(pattern, value))
        
        return ValidationResult(
            is_valid=is_valid,
            errors=[] if is_valid else ["Customer number should be 5-6 digits"],
            normalized_value=value.strip() if is_valid else None,
            confidence_score=0.9 if is_valid else 0.3
        )
    
    def validate_registration_number(self, value: str) -> ValidationResult:
        """Validate attorney registration number"""
        if not value:
            return ValidationResult(is_valid=True, normalized_value=None, confidence_score=1.0)
        
        # Registration numbers are typically 5-digit numbers, sometimes with commas
        import re
        # Remove commas and validate
        clean_value = value.replace(',', '').strip()
        pattern = r'^\d{5}$'
        is_valid = bool(re.match(pattern, clean_value))
        
        return ValidationResult(
            is_valid=is_valid,
            errors=[] if is_valid else ["Registration number should be 5 digits"],
            normalized_value=clean_value if is_valid else None,
            confidence_score=0.9 if is_valid else 0.3
        )
```

## Phase 6: API Endpoint Extensions

### 6.1 Enhanced Application Endpoint
```python
# File: backend/app/api/endpoints/applications.py (extend existing)

@router.post("/generate-enhanced-ads")
async def generate_enhanced_ads(
    application_data: EnhancedApplicationMetadata,
    current_user: User = Depends(get_current_user)
):
    """
    Generate ADS PDF with all enhanced fields
    """
    try:
        # Validate enhanced data
        validation_service = EnhancedValidationService()
        validation_result = await validation_service.validate_enhanced_application(application_data)
        
        if validation_result.has_errors:
            raise HTTPException(
                status_code=400,
                detail=f"Validation failed: {validation_result.error_summary}"
            )
        
        # Generate enhanced ADS
        ads_generator = EnhancedADSGenerator()
        output_path = f"temp_ads_{datetime.utcnow().timestamp()}.pdf"
        
        generated_path = ads_generator.generate_enhanced_ads_pdf(
            application_data, 
            output_path
        )
        
        # Return PDF file
        return FileResponse(
            generated_path,
            media_type="application/pdf",
            filename=f"Enhanced_ADS_{application_data.application_number or 'Draft'}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Enhanced ADS generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

## Phase 7: Testing Strategy

### 7.1 Test Document Requirements
Create test documents containing all new field types:
- Documents with correspondence addresses
- Documents with attorney/agent information
- Documents with priority claims (both domestic and foreign)
- Documents with classification information
- Documents with enhanced applicant details

### 7.2 Test Cases
```python
# File: backend/app/tests/test_enhanced_ads_extraction.py

class TestEnhancedADSExtraction:
    async def test_correspondence_info_extraction(self):
        """Test extraction of correspondence information"""
        # Test with document containing law firm letterhead
        pass
    
    async def test_attorney_agent_extraction(self):
        """Test extraction of attorney/agent information"""
        # Test with document containing registration numbers
        pass
    
    async def test_priority_claims_extraction(self):
        """Test extraction of priority claims"""
        # Test with document containing benefit claims
        pass
    
    async def test_classification_extraction(self):
        """Test extraction of classification codes"""
        # Test with document containing art unit and classification codes
        pass
    
    async def test_enhanced_validation(self):
        """Test validation of all new field types"""
        # Test validation rules for new fields
        pass
```

## Phase 8: Implementation Sequence

### 8.1 Development Order
1. **Backend Models** (Phase 1) - Extend data models first
2. **LLM Prompts** (Phase 2) - Enhance extraction prompts
3. **Extraction Service** (Phase 2) - Update parsing logic
4. **Validation** (Phase 5) - Add validation for new fields
5. **Frontend Components** (Phase 3) - Create UI components
6. **ADS Generator** (Phase 4) - Update PDF generation
7. **API Endpoints** (Phase 6) - Extend API
8. **Testing** (Phase 7) - Comprehensive testing

### 8.2 Rollout Strategy
- **Phase A**: Backend implementation (Models, Prompts, Validation)
- **Phase B**: Frontend implementation (Components, UI)
- **Phase C**: Integration and testing
- **Phase D**: Production deployment

## Expected Outcomes

### 8.1 Enhanced Extraction Capabilities
- **Complete ADS Coverage**: Extract all USPTO Form PTO/SB/14 required fields
- **Professional Quality**: Match commercial patent software capabilities
- **High Accuracy**: Leverage existing two-step extraction process
- **User-Friendly**: Organized display and editing of all extracted data

### 8.2 Business Benefits
- **Reduced Manual Entry**: Significantly less manual data entry required
- **Improved Accuracy**: Automated extraction reduces human errors
- **Time Savings**: Faster ADS preparation process
- **Professional Output**: Complete, properly formatted ADS forms

### 8.3 Technical Benefits
- **Backward Compatibility**: All changes are additive
- **Scalable Architecture**: Follows existing patterns
- **Maintainable Code**: Well-structured, documented implementation
- **Robust Validation**: Comprehensive error checking and data validation

## Risk Mitigation

### 8.1 Technical Risks
- **LLM Response Variability**: Use structured prompts and validation
- **Field Mapping Complexity**: Comprehensive testing with various document types
- **Performance Impact**: Optimize prompts and processing

### 8.2 Implementation Risks
- **Breaking Changes**: All new fields are optional
- **Data Migration**: No existing data migration required
- **User Adoption**: Gradual rollout with training

## Success Metrics

### 8.1 Extraction Quality
- **Field Coverage**: >90% of available fields extracted correctly
- **Accuracy Rate**: >95% accuracy for extracted fields
- **Processing Time**: <30 seconds for typical documents

### 8.2 User Experience
- **User Satisfaction**: Positive feedback on enhanced functionality
- **Time Savings**: Measurable reduction in manual data entry time
- **Error Reduction**: Fewer errors in generated ADS forms

This comprehensive implementation plan provides a complete roadmap for enhancing the ADS extraction system to support all USPTO Form PTO/SB/14 requirements while maintaining the existing architecture and ensuring backward compatibility.
