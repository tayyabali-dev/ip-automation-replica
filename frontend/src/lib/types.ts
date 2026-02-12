// ============================================================================
// OFFICE ACTION TYPES
// ============================================================================

// Foreign Priority Information
export interface ForeignPriorityInfo {
  country?: string;
  application_number?: string;
  filing_date?: string;
  certified_copy_attached?: boolean;
}

// Parent Application Information (Continuity Data)
export interface ParentApplicationInfo {
  parent_application_number?: string;
  parent_filing_date?: string;
  relationship_type?: string;
  status?: string;
  patent_number?: string;
}

// Prior Art Reference with enhanced fields
export interface PriorArtReference {
  reference_id?: string;
  reference_type: string;
  identifier: string;
  short_name?: string;
  inventor_author?: string;
  title?: string;
  date?: string;
  relevant_sections?: string;
  relevant_claims: string[];
  citation_details?: string;
  used_in_rejection_indices?: number[];
}

// Prior Art Combination for Section 103 rejections
export interface PriorArtCombination {
  primary_reference_id: string;
  secondary_reference_ids: string[];
  motivation_to_combine?: string;
  teaching_suggestion_motivation?: string;
  affected_claim_elements?: string[];
}

// Rejection Reference Link
export interface RejectionReferenceLink {
  rejection_index: number;
  reference_id: string;
  role: string;
  relevance_explanation?: string;
}

// Rejection with enhanced type detection and 103 combination grouping
export interface Rejection {
  rejection_type: string;
  rejection_type_normalized?: string;
  statutory_basis?: string;
  is_aia?: boolean;
  affected_claims: string[];
  examiner_reasoning: string;
  cited_prior_art: PriorArtReference[];
  relevant_claim_language?: string;
  page_number?: string;
  prior_art_combinations?: PriorArtCombination[];
}

// Claim Status with optional full text extraction
export interface ClaimStatus {
  claim_number: string;
  status: string;
  dependency_type: string;
  parent_claim?: string;
  claim_text?: string;
  claim_preamble?: string;
  claim_body?: string;
}

// Objection with normalized type
export interface Objection {
  objected_item: string;
  objection_type?: string;
  reason: string;
  corrective_action?: string;
  page_number?: string;
}

// Examiner Statement
export interface ExaminerStatement {
  statement_type: string;
  content: string;
  page_number?: string;
}

// Deadline Tier
export interface DeadlineTier {
  deadline_date: string;
  months_from_mailing: number;
  months_extension: number;
  extension_fee_micro: number;
  extension_fee_small: number;
  extension_fee_large: number;
  is_past: boolean;
}

// Deadline Calculation
export interface DeadlineCalculation {
  mailing_date: string;
  shortened_statutory_period: number;
  statutory_deadline: string;
  maximum_deadline: string;
  tiers: DeadlineTier[];
  notes: string[];
  is_final_action: boolean;
}

// Office Action Header with complete field extraction
export interface OfficeActionHeader {
  application_number?: string;
  filing_date?: string;
  patent_office: string;
  office_action_date?: string;
  office_action_type?: string;
  examiner_name?: string;
  art_unit?: string;
  attorney_docket_number?: string;
  confirmation_number?: string;
  response_deadline?: string;
  first_named_inventor?: string;
  applicant_name?: string;
  title_of_invention?: string;
  customer_number?: string;
  examiner_phone?: string;
  examiner_email?: string;
  examiner_type?: string;
  foreign_priority?: ForeignPriorityInfo[];
  parent_applications?: ParentApplicationInfo[];
}

// Complete Office Action Data
export interface OfficeActionData {
  header: OfficeActionHeader;
  claims_status: ClaimStatus[];
  rejections: Rejection[];
  objections: Objection[];
  other_statements: ExaminerStatement[];
  prosecution_history_summary?: string;
  all_references?: PriorArtReference[];
  reference_links?: RejectionReferenceLink[];
  deadline_calculation?: DeadlineCalculation;
}

// Job Status
export interface JobStatus {
  status: string;
  progress_percentage: number;
  error_details?: string;
}


// ============================================================================
// PATENT APPLICATION TYPES
// ============================================================================

export interface CorrespondenceAddress {
  name?: string;
  name2?: string;
  address1?: string;
  address2?: string;
  city?: string;
  state?: string;
  country?: string;
  postcode?: string;
  phone?: string;
  fax?: string;
  email?: string;
  customer_number?: string;
}

export interface ApplicationMetadata {
  title?: string;
  application_number?: string;
  entity_status?: string;
  total_drawing_sheets?: number;
  inventors: Inventor[];
  applicants: Applicant[];
  correspondence_address?: CorrespondenceAddress;
  application_type?: string;
  suggested_figure?: string;
}

export interface Inventor {
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  suffix?: string;
  prefix?: string;
  name?: string;
  street_address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  citizenship?: string;
}

export interface Applicant {
  name?: string;
  org_name?: string;
  is_organization?: boolean;
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  prefix?: string;
  suffix?: string;
  authority?: string;
  street_address?: string;
  address1?: string;
  address2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  postcode?: string;
  country?: string;
  phone?: string;
  fax?: string;
  email?: string;
}

export interface AttorneyAgentInfo {
  name?: string;
  registration_number?: string;
  phone_number?: string;
  email_address?: string;
  firm_name?: string;
  address?: string;
  is_attorney?: boolean;
}

export interface ClassificationInfo {
  suggested_art_unit?: string;
  uspc_classification?: string;
  ipc_classification?: string;
  cpc_classification?: string;
}

export interface CorrespondenceInfo {
  firm_name?: string;
  attorney_name?: string;
  customer_number?: string;
  email_address?: string;
  street_address?: string;
  address_line_2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  phone_number?: string;
  fax_number?: string;
}

export interface DomesticPriorityClaim {
  parent_application_number?: string;
  filing_date?: string;
  application_type?: string;
  relationship_type?: string;
  status?: string;
}

export interface ForeignPriorityClaim {
  country_code?: string;
  application_number?: string;
  filing_date?: string;
  certified_copy_status?: string;
  certified_copy_filed?: boolean;
}


// ============================================================================
// APPLICATION HISTORY TYPES
// ============================================================================

export interface QualityMetrics {
  completeness_score: number;
  accuracy_score: number;
  confidence_score: number;
  consistency_score: number;
  overall_quality_score: number;
  required_fields_populated: number;
  total_required_fields: number;
  optional_fields_populated: number;
  total_optional_fields: number;
  validation_errors: number;
  validation_warnings: number;
}

export interface ExtractionMetadata {
  extraction_method: string;
  document_type: string;
  processing_time: number;
  llm_tokens_used?: number;
  fallback_level_used?: string;
  manual_review_required: boolean;
  extraction_notes: string[];
}

export interface EnhancedInventor {
  given_name?: string;
  middle_name?: string;
  family_name?: string;
  full_name?: string;
  street_address?: string;
  address_line_2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  citizenship?: string;
  sequence_number?: number;
  completeness: string;
  confidence_score: number;
}

export interface EnhancedApplicant {
  is_assignee: boolean;
  organization_name?: string;
  individual_given_name?: string;
  individual_family_name?: string;
  street_address?: string;
  address_line_2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  customer_number?: string;
  email_address?: string;
  phone_number?: string;
  relationship_to_inventors: string;
  legal_entity_type?: string;
  completeness: string;
  confidence_score: number;
}

export interface PriorityClaimInfo {
  application_number: string;
  filing_date: string;
  country?: string;
  continuity_type?: string;
  confidence_score: number;
}

export interface ApplicationHistoryItem {
  _id: string;
  title?: string;
  application_number?: string;
  filing_date?: string;
  entity_status?: string;
  attorney_docket_number?: string;
  confirmation_number?: string;
  application_type?: string;
  inventors: EnhancedInventor[];
  applicants: EnhancedApplicant[];
  correspondence_info?: CorrespondenceInfo;
  attorney_agent_info?: AttorneyAgentInfo;
  domestic_priority_claims: PriorityClaimInfo[];
  foreign_priority_claims: PriorityClaimInfo[];
  classification_info?: ClassificationInfo;
  quality_metrics: QualityMetrics;
  extraction_metadata: ExtractionMetadata;
  manual_review_required: boolean;
  extraction_warnings: string[];
  recommendations: string[];
  created_by: string;
  created_at: string;
  workflow_status: string;
}

// Office Action History Item for history list
export interface OfficeActionHistoryItem {
  _id: string;
  document_type: 'office_action';
  filename?: string;
  created_at?: string;
  processed_status?: string;
  // Header info
  application_number?: string;
  title_of_invention?: string;
  office_action_type?: string;
  office_action_date?: string;
  examiner_name?: string;
  art_unit?: string;
  first_named_inventor?: string;
  // Summary stats
  total_claims: number;
  total_rejections: number;
  rejection_counts: Record<string, number>;
  // Deadline info
  deadline_calculation?: DeadlineCalculation;
}

// Combined history item type for the history page
export type HistoryItem =
  | (ApplicationHistoryItem & { record_type: 'application' })
  | (OfficeActionHistoryItem & { record_type: 'office_action' });
