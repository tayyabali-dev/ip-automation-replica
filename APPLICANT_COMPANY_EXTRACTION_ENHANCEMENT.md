# Applicant/Company Information Extraction Enhancement

## Overview

This document addresses the critical issue of applicant/company information being frequently missed or extracted incorrectly in patent documents. The current system lacks systematic strategies for locating and extracting company information that appears in various sections and formats throughout patent documents.

## Current Issues Analysis

### 1. Inconsistent Field Mapping
- **Variable Section Names**: "Applicant", "Assignee", "Company", "Organization" used interchangeably
- **Multiple Locations**: Company info appears in headers, correspondence sections, assignment blocks
- **Format Variations**: Different document types use different layouts for company information
- **Schema Misalignment**: Extracted data doesn't align with USPTO ADS requirements

### 2. Missing Fallback Logic
- **Single Strategy Failure**: If primary extraction fails, no alternative approaches attempted
- **Section-Specific Searches**: No systematic search across all possible document sections
- **Context Awareness**: Lack of understanding when applicant is same as inventor vs. separate entity
- **Relationship Detection**: Poor detection of inventor-applicant relationships

### 3. Data Quality Issues
- **Incomplete Addresses**: Company addresses often partially extracted
- **Name Variations**: Company name variations not recognized as same entity
- **Contact Information**: Missing customer numbers, email addresses
- **Legal Entity Types**: Inconsistent handling of "Inc.", "LLC", "Corp." variations

## Enhanced Applicant/Company Extraction Strategy

### 1. Multi-Section Search Strategy

#### A. Comprehensive Section Mapping

```python
class ApplicantSectionMapper:
    """Maps all possible locations of applicant/company information"""
    
    APPLICANT_SECTIONS = {
        'primary_sections': [
            'applicant_information',
            'assignee_information', 
            'correspondence_address',
            'company_information'
        ],
        'secondary_sections': [
            'document_header',
            'footer_information',
            'assignment_block',
            'attorney_information'
        ],
        'form_fields': [
            'applicant_name',
            'company_name',
            'organization_name',
            'assignee_name',
            'entity_name'
        ],
        'contextual_indicators': [
            'customer_number',
            'correspondence_address',
            'business_address',
            'corporate_address'
        ]
    }
    
    def map_applicant_locations(self, document_structure: DocumentStructure) -> ApplicantLocationMap:
        """Identify all potential applicant information locations"""
        
    def prioritize_sections(self, locations: ApplicantLocationMap) -> List[SectionPriority]:
        """Prioritize sections based on reliability and completeness"""

class ApplicantLocationMap:
    """Maps potential applicant information across document"""
    primary_locations: List[SectionLocation]
    secondary_locations: List[SectionLocation]
    form_field_locations: List[FieldLocation]
    contextual_locations: List[ContextLocation]
    confidence_scores: Dict[str, float]
```

#### B. Section-Specific Extraction Strategies

```python
class SectionSpecificExtractor:
    """Tailored extraction for different document sections"""
    
    def extract_from_header(self, header_content: str) -> ApplicantCandidate:
        """Extract applicant info from document header"""
        
    def extract_from_correspondence_section(self, content: str) -> ApplicantCandidate:
        """Extract from correspondence/attorney information"""
        
    def extract_from_assignment_block(self, content: str) -> ApplicantCandidate:
        """Extract from assignment or transfer information"""
        
    def extract_from_form_fields(self, form_data: Dict[str, str]) -> ApplicantCandidate:
        """Extract from structured form fields"""
        
    def extract_from_footer(self, footer_content: str) -> ApplicantCandidate:
        """Extract from document footer information"""

class ApplicantCandidate:
    """Potential applicant with source and confidence information"""
    organization_name: Optional[str]
    individual_name: Optional[Dict[str, str]]  # given_name, family_name
    address_components: Dict[str, str]
    contact_information: Dict[str, str]
    source_section: str
    source_page: int
    extraction_method: str
    confidence_score: float
    completeness_score: float
    is_assignee: bool
    relationship_to_inventors: str
```

### 2. Enhanced Applicant Detection Prompts

#### A. Comprehensive Applicant Search Prompt

```markdown
**APPLICANT/COMPANY INFORMATION EXTRACTION PROMPT:**

You are systematically searching for applicant/company information in a patent document.

**CRITICAL INSTRUCTIONS:**
1. **Search ALL Sections**: Check every part of the document for company information
2. **Multiple Strategies**: Use different approaches for different document areas
3. **Distinguish Entities**: Separate company information from inventor information
4. **Complete Addresses**: Extract full business addresses, not just company names
5. **Relationship Detection**: Determine if applicant is same as inventor or separate entity

**SYSTEMATIC SEARCH STRATEGY:**

### Section 1: Primary Applicant Sections
**Search Locations:**
- "Applicant Information" sections
- "Assignee Information" blocks  
- "Company Information" areas
- "Organization" sections

**Evidence to Extract:**
- Organization/Company Name: "[Quote exact name]"
- Business Address: "[Quote complete address]"
- Contact Information: "[Customer number, email, phone]"
- Legal Entity Type: "[Inc., LLC, Corp., etc.]"
- Source Location: Page X, Section Y

### Section 2: Correspondence Information
**Search Locations:**
- "Correspondence Address" sections
- "Attorney Information" blocks
- "Customer Number" references
- "Email Address" fields

**Evidence to Extract:**
- Correspondence Entity: "[Company or law firm name]"
- Customer Number: "[USPTO customer number]"
- Email Address: "[Contact email]"
- Mailing Address: "[Complete correspondence address]"
- Source Location: Page X, Section Y

### Section 3: Document Headers and Footers
**Search Locations:**
- Document headers with company information
- Footer information with entity details
- Letterhead information
- Document metadata

**Evidence to Extract:**
- Header Company Info: "[Any company names in headers]"
- Footer Entity Info: "[Any entity information in footers]"
- Letterhead Details: "[Company information from letterhead]"
- Source Location: Page X, Header/Footer

### Section 4: Assignment and Transfer Information
**Search Locations:**
- Assignment statements
- Transfer of rights information
- Ownership declarations
- Entity relationship statements

**Evidence to Extract:**
- Assignee Name: "[Entity receiving assignment]"
- Assignment Details: "[Transfer or assignment information]"
- Ownership Structure: "[Relationship to inventors]"
- Source Location: Page X, Section Y

### Section 5: Form Field Analysis
**Search Locations:**
- Structured form fields
- XFA form data
- AcroForm field values
- Dynamic form elements

**Evidence to Extract:**
- Form Field Values: "[All company-related field values]"
- Field Names: "[Field identifiers for company data]"
- Field Relationships: "[How fields relate to each other]"
- Source Location: Form field names and values

**RELATIONSHIP ANALYSIS:**
After gathering all evidence, analyze:
1. **Entity Relationships**: Is applicant same as inventor or separate company?
2. **Address Consistency**: Do addresses match between sections?
3. **Name Variations**: Are different company names the same entity?
4. **Completeness Assessment**: Which source provides most complete information?

**OUTPUT FORMAT:**
```json
{
  "applicant_candidates": [
    {
      "candidate_id": "primary|secondary|correspondence|assignment",
      "organization_name": "exact company name or null",
      "individual_applicant": {
        "given_name": "if individual applicant",
        "family_name": "if individual applicant"
      },
      "business_address": {
        "address_line_1": "street address",
        "address_line_2": "suite/unit or null",
        "city": "city name",
        "state_province": "state or province",
        "postal_code": "zip or postal code",
        "country": "country name or code"
      },
      "contact_information": {
        "customer_number": "USPTO customer number or null",
        "email_address": "contact email or null",
        "phone_number": "phone number or null"
      },
      "source_evidence": {
        "source_section": "section where found",
        "source_page": "page number",
        "raw_text": "quoted text evidence",
        "extraction_method": "header|form_field|correspondence|assignment"
      },
      "entity_analysis": {
        "is_assignee": true/false,
        "relationship_to_inventors": "same_as_inventor|separate_entity|unclear",
        "legal_entity_type": "corporation|llc|individual|partnership|other",
        "confidence_score": 0.0-1.0,
        "completeness_score": 0.0-1.0
      }
    }
  ],
  "analysis_summary": {
    "total_candidates_found": "number",
    "primary_applicant_identified": true/false,
    "conflicting_information": true/false,
    "missing_required_fields": ["list of missing fields"],
    "recommendations": ["list of recommendations"]
  }
}
```
```

#### B. Applicant Validation and Consolidation Prompt

```markdown
**APPLICANT INFORMATION CONSOLIDATION PROMPT:**

You have extracted multiple applicant candidates. Now consolidate into final applicant information.

**CONSOLIDATION RULES:**
1. **Primary Source Priority**: Prefer dedicated applicant sections over headers/footers
2. **Completeness Priority**: Choose most complete information when sources conflict
3. **Consistency Check**: Ensure addresses and names are consistent
4. **Relationship Clarity**: Clearly identify if applicant is inventor or separate entity

**CONSOLIDATION PROCESS:**
1. **Identify Primary Applicant**: Select most reliable candidate as primary
2. **Merge Complementary Data**: Combine information from multiple sources
3. **Resolve Conflicts**: Choose most reliable data when sources disagree
4. **Validate Completeness**: Ensure all required fields are populated
5. **Document Decisions**: Explain consolidation choices

**FINAL OUTPUT:**
```json
{
  "final_applicant": {
    "is_assignee": true/false,
    "organization_name": "final company name or null",
    "legal_name": {
      "given_name": "if individual applicant or null",
      "family_name": "if individual applicant or null"
    },
    "mailing_address": {
      "address_1": "final street address",
      "address_2": "suite/unit or null",
      "city": "final city",
      "state_province": "final state/province",
      "postal_code": "final postal code",
      "country": "final country"
    },
    "contact_information": {
      "customer_number": "final customer number or null",
      "email_address": "final email or null"
    }
  },
  "consolidation_metadata": {
    "primary_source": "section used as primary source",
    "merged_sources": ["list of sources merged"],
    "conflicts_resolved": ["list of conflicts and resolutions"],
    "confidence_score": 0.0-1.0,
    "completeness_score": 0.0-1.0,
    "validation_notes": ["any validation concerns"]
  }
}
```
```

### 3. Advanced Applicant Detection and Validation

#### A. Multi-Strategy Applicant Detection

```python
class ApplicantDetectionEngine:
    """Multiple strategies for detecting applicant information"""
    
    def detect_by_section_headers(self, content: str) -> List[ApplicantCandidate]:
        """Detect using section header analysis"""
        
    def detect_by_form_structure(self, form_data: Dict) -> List[ApplicantCandidate]:
        """Detect using form field structure"""
        
    def detect_by_address_patterns(self, content: str) -> List[ApplicantCandidate]:
        """Detect using business address patterns"""
        
    def detect_by_legal_entity_indicators(self, content: str) -> List[ApplicantCandidate]:
        """Detect using legal entity type indicators (Inc., LLC, etc.)"""
        
    def detect_by_correspondence_context(self, content: str) -> List[ApplicantCandidate]:
        """Detect using correspondence and customer number context"""
        
    def combine_detection_strategies(
        self, 
        results: List[List[ApplicantCandidate]]
    ) -> List[ApplicantCandidate]:
        """Combine and rank results from multiple strategies"""
```

#### B. Applicant-Inventor Relationship Analysis

```python
class ApplicantInventorAnalyzer:
    """Analyzes relationships between applicants and inventors"""
    
    def analyze_entity_relationships(
        self, 
        applicant_candidates: List[ApplicantCandidate],
        inventors: List[Inventor]
    ) -> RelationshipAnalysis:
        """Determine relationships between applicants and inventors"""
        
    def detect_individual_applicant_inventor_match(
        self, 
        applicant: ApplicantCandidate,
        inventors: List[Inventor]
    ) -> MatchResult:
        """Check if individual applicant matches an inventor"""
        
    def detect_corporate_applicant(
        self, 
        applicant: ApplicantCandidate
    ) -> CorporateAnalysis:
        """Analyze if applicant is a corporate entity"""
        
    def validate_applicant_inventor_consistency(
        self, 
        applicant: ApplicantCandidate,
        inventors: List[Inventor]
    ) -> ConsistencyResult:
        """Validate consistency between applicant and inventor data"""

class RelationshipAnalysis:
    """Analysis of applicant-inventor relationships"""
    relationship_type: str  # same_entity, separate_entity, mixed, unclear
    individual_applicants: List[ApplicantCandidate]
    corporate_applicants: List[ApplicantCandidate]
    inventor_matches: List[MatchResult]
    confidence_score: float
    analysis_notes: List[str]
```

### 4. Applicant Data Quality Enhancement

#### A. Address Completion and Validation

```python
class ApplicantAddressEnhancer:
    """Enhances and validates applicant address information"""
    
    def complete_partial_addresses(
        self, 
        address_data: Dict[str, str]
    ) -> EnhancedAddress:
        """Complete partial address information using external validation"""
        
    def standardize_address_format(
        self, 
        address_data: Dict[str, str]
    ) -> StandardizedAddress:
        """Standardize address format for consistency"""
        
    def validate_business_address(
        self, 
        address_data: Dict[str, str]
    ) -> AddressValidationResult:
        """Validate that address appears to be a business address"""
        
    def detect_po_box_addresses(
        self, 
        address_data: Dict[str, str]
    ) -> POBoxAnalysis:
        """Detect and handle P.O. Box addresses appropriately"""

class EnhancedAddress:
    """Enhanced address with completion and validation"""
    original_address: Dict[str, str]
    enhanced_address: Dict[str, str]
    completion_sources: List[str]
    validation_status: str
    confidence_score: float
```

#### B. Company Name Normalization

```python
class CompanyNameNormalizer:
    """Normalizes and standardizes company names"""
    
    def normalize_legal_entity_suffixes(self, company_name: str) -> str:
        """Standardize Inc., LLC, Corp., etc."""
        
    def detect_name_variations(
        self, 
        candidates: List[ApplicantCandidate]
    ) -> List[NameVariationGroup]:
        """Group company name variations that refer to same entity"""
        
    def standardize_company_name_format(self, company_name: str) -> str:
        """Apply consistent formatting to company names"""
        
    def validate_company_name_completeness(self, company_name: str) -> ValidationResult:
        """Ensure company name appears complete and valid"""

class NameVariationGroup:
    """Group of company name variations"""
    canonical_name: str
    variations: List[str]
    confidence_score: float
    normalization_rules_applied: List[str]
```

### 5. Integration with Existing System

#### A. Enhanced LLM Service Methods

```python
# Add to LLMService class
async def extract_applicant_information_comprehensive(
    self, 
    document_content: str,
    inventors: List[Inventor] = None
) -> ApplicantExtractionResult:
    """
    Comprehensive applicant extraction using multi-section strategy
    """
    
async def validate_applicant_inventor_relationships(
    self, 
    applicant_data: Dict,
    inventor_data: List[Dict]
) -> RelationshipValidationResult:
    """
    Validate relationships between applicants and inventors
    """
    
async def consolidate_applicant_candidates(
    self, 
    candidates: List[ApplicantCandidate]
) -> ConsolidatedApplicant:
    """
    Consolidate multiple applicant candidates into final result
    """
```

#### B. Updated Schema Integration

```python
# Enhanced Applicant model
class EnhancedApplicant(BaseModel):
    """Enhanced applicant model with comprehensive information"""
    organization_name: Optional[str] = None
    individual_name: Optional[Dict[str, str]] = None
    business_address: Dict[str, str]
    contact_information: Dict[str, str]
    legal_entity_type: Optional[str] = None
    is_assignee: bool = False
    relationship_to_inventors: str = "separate_entity"
    extraction_metadata: ExtractionMetadata
    validation_results: ValidationResults
    confidence_scores: ConfidenceScores

class ExtractionMetadata:
    """Metadata about applicant extraction process"""
    primary_source_section: str
    all_sources_used: List[str]
    extraction_strategies: List[str]
    conflicts_resolved: List[str]
    completion_enhancements: List[str]
```

## Implementation Phases

### Phase 1: Multi-Section Detection
- [ ] Implement comprehensive section mapping
- [ ] Create section-specific extractors
- [ ] Build applicant candidate system
- [ ] Test detection across document types

### Phase 2: Enhanced Extraction Prompts
- [ ] Implement systematic search prompts
- [ ] Create consolidation prompts
- [ ] Build validation prompts
- [ ] Test prompt effectiveness

### Phase 3: Relationship Analysis
- [ ] Implement applicant-inventor analyzer
- [ ] Create entity relationship detection
- [ ] Build consistency validation
- [ ] Test relationship accuracy

### Phase 4: Data Quality Enhancement
- [ ] Implement address enhancement
- [ ] Create company name normalization
- [ ] Build validation systems
- [ ] Test data quality improvements

### Phase 5: System Integration
- [ ] Integrate with existing LLM service
- [ ] Update data models and schemas
- [ ] Create comprehensive testing
- [ ] Deploy and monitor performance

## Expected Improvements

### Quantitative Metrics
- **Applicant Detection Rate**: Target 95%+ of documents with applicant information
- **Address Completeness**: Target 90%+ complete business addresses
- **Relationship Accuracy**: Target 95%+ correct applicant-inventor relationships
- **Data Quality Score**: Target 90%+ validated and normalized applicant data

### Qualitative Improvements
- **Reduced Missing Applicants**: Systematic search reduces missed company information
- **Better Address Quality**: Enhanced addresses suitable for USPTO submission
- **Clear Entity Relationships**: Proper distinction between inventors and applicants
- **Consistent Data Format**: Standardized company names and addresses

This enhanced applicant/company extraction system provides comprehensive coverage of all potential sources of company information while ensuring high-quality, complete, and properly validated applicant data for USPTO submissions.