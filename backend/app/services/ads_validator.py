"""
ADS Data Integrity Validation Service

This service validates generated XFA XML against source metadata to ensure
data integrity in ADS PDF generation. It implements a hybrid validation approach:
- CRITICAL ERRORS: Block PDF generation
- WARNINGS: Allow PDF generation with clear warnings
- INFO: Informational messages about normalizations
"""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import hashlib
import re
from dataclasses import dataclass

from app.models.patent_application import PatentApplicationMetadata, Inventor, Applicant
from app.models.validation import (
    ValidationReport, ValidationSummary, FieldMismatch, ValidationSeverity,
    ValidationCategory, ExtractedXFAData, ExtractedInventor, ExtractedApplicant,
    ADSGenerationResponse, VALIDATION_RULES
)

logger = logging.getLogger(__name__)

@dataclass
class ValidationConfig:
    """Configuration for validation behavior"""
    enable_auto_correction: bool = True
    strict_country_validation: bool = True
    normalize_names: bool = True
    validate_address_format: bool = True
    max_processing_time_ms: int = 5000  # 5 second timeout

class XFAFieldExtractor:
    """Extracts structured data from XFA datasets XML"""
    
    def __init__(self):
        self.namespace = {'xfa': 'http://www.xfa.org/schema/xfa-data/1.0/'}
        
    def extract_fields_from_xml(self, xml_string: str) -> ExtractedXFAData:
        """
        Extract all fields from XFA datasets XML into structured format.
        
        Args:
            xml_string: Complete XFA datasets XML string
            
        Returns:
            ExtractedXFAData: Structured data extracted from XML
        """
        try:
            root = ET.fromstring(xml_string)
            extracted = ExtractedXFAData()
            
            # Extract application-level fields
            self._extract_application_fields(root, extracted)
            
            # Extract inventors
            self._extract_inventors(root, extracted)
            
            # Extract applicants
            self._extract_applicants(root, extracted)
            
            # Extract correspondence information
            self._extract_correspondence(root, extracted)
            
            logger.info(f"Successfully extracted {len(extracted.inventors)} inventors and {len(extracted.applicants)} applicants from XFA XML")
            return extracted
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse XFA XML: {e}")
            extracted = ExtractedXFAData()
            extracted.xml_structure_valid = False
            extracted.extraction_warnings.append(f"XML parsing failed: {str(e)}")
            return extracted
        except Exception as e:
            logger.error(f"Unexpected error during XFA extraction: {e}")
            extracted = ExtractedXFAData()
            extracted.xml_structure_valid = False
            extracted.extraction_warnings.append(f"Extraction error: {str(e)}")
            return extracted
    
    def _extract_application_fields(self, root: ET.Element, extracted: ExtractedXFAData):
        """Extract application-level fields from ROOT level and ContentArea2"""
        
        # FIXED: Title is now at ROOT level (outside ContentArea3)
        title_elem = root.find(".//us-request/invention-title")
        if title_elem is not None and title_elem.text:
            extracted.title = title_elem.text.strip()
        
        # FIXED: Attorney docket number is also at ROOT level
        docket_elem = root.find(".//us-request/attorney-docket-number")
        if docket_elem is not None and docket_elem.text:
            extracted.attorney_docket_number = docket_elem.text.strip()
        
        # Application type and entity status from ContentArea2
        app_type_elem = root.find(".//ContentArea2//application_type")
        if app_type_elem is not None and app_type_elem.text:
            extracted.application_type = app_type_elem.text.strip()
        
        # Entity status from chkSmallEntity
        entity_elem = root.find(".//ContentArea2//chkSmallEntity")
        if entity_elem is not None and entity_elem.text:
            entity_value = entity_elem.text.strip()
            entity_map = {"0": "undiscounted", "1": "small", "2": "micro"}
            extracted.entity_status = entity_map.get(entity_value, entity_value)
        
        # Drawing sheets and suggested figure
        sheets_elem = root.find(".//ContentArea2//us-total_number_of_drawing-sheets")
        if sheets_elem is not None and sheets_elem.text:
            extracted.total_drawing_sheets = sheets_elem.text.strip()
        
        figure_elem = root.find(".//ContentArea2//us-suggested_representative_figure")
        if figure_elem is not None and figure_elem.text:
            extracted.suggested_figure = figure_elem.text.strip()
    
    def _extract_inventors(self, root: ET.Element, extracted: ExtractedXFAData):
        """Extract all inventors from ContentArea1/sfApplicantInformation blocks"""
        
        inventor_blocks = root.findall(".//ContentArea1/sfApplicantInformation")
        
        for i, block in enumerate(inventor_blocks):
            inventor = ExtractedInventor(sequence=i + 1)
            
            # Extract name fields
            inventor.prefix = self._get_text(block, ".//sfApplicantName/prefix")
            inventor.first_name = self._get_text(block, ".//sfApplicantName/firstName")
            inventor.middle_name = self._get_text(block, ".//sfApplicantName/middleName")
            inventor.last_name = self._get_text(block, ".//sfApplicantName/lastName")
            inventor.suffix = self._get_text(block, ".//sfApplicantName/suffix")
            
            # Extract residency information
            residency_radio = self._get_text(block, ".//ResidencyRadio")
            inventor.residency_type = residency_radio
            
            if residency_radio == "us-residency":
                # US residence fields
                inventor.residence_city = self._get_text(block, ".//sfUSres/rsCityTxt")
                inventor.residence_state = self._get_text(block, ".//sfUSres/rsStTxt")
                inventor.residence_country = self._get_text(block, ".//sfUSres/rsCtryTxt")
            else:
                # Non-US residence fields
                inventor.residence_city = self._get_text(block, ".//sfNonUSRes/nonresCity")
                inventor.residence_country = self._get_text(block, ".//sfNonUSRes/nonresCtryList")
            
            # Extract citizenship
            inventor.citizenship = self._get_text(block, ".//sfCitz/CitizedDropDown")
            
            # Extract mailing address
            inventor.mail_address1 = self._get_text(block, ".//sfApplicantMail/address1")
            inventor.mail_address2 = self._get_text(block, ".//sfApplicantMail/address2")
            inventor.mail_city = self._get_text(block, ".//sfApplicantMail/city")
            inventor.mail_state = self._get_text(block, ".//sfApplicantMail/state")
            inventor.mail_postcode = self._get_text(block, ".//sfApplicantMail/postcode")
            inventor.mail_country = self._get_text(block, ".//sfApplicantMail/mailCountry")
            
            # Only add if we found meaningful data
            if inventor.first_name or inventor.last_name or inventor.residence_city:
                extracted.inventors.append(inventor)
    
    def _extract_applicants(self, root: ET.Element, extracted: ExtractedXFAData):
        """Extract all applicants from ContentArea2/sfAssigneeInformation blocks"""
        
        applicant_blocks = root.findall(".//ContentArea2/sfAssigneeInformation")
        
        for i, block in enumerate(applicant_blocks):
            applicant = ExtractedApplicant(sequence=i + 1)
            
            # Check if organization
            chk_org = self._get_text(block, ".//chkOrg")
            applicant.is_organization = chk_org == "1"
            
            if applicant.is_organization:
                # Organization name
                applicant.organization_name = self._get_text(block, ".//sforgName/orgName")
            else:
                # Individual name fields
                applicant.prefix = self._get_text(block, ".//sfApplicantName/prefix")
                applicant.first_name = self._get_text(block, ".//sfApplicantName/first-name")
                applicant.middle_name = self._get_text(block, ".//sfApplicantName/middle-name")
                applicant.last_name = self._get_text(block, ".//sfApplicantName/last-name")
                applicant.suffix = self._get_text(block, ".//sfApplicantName/suffix")
            
            # Authority type
            applicant.authority_type = self._get_text(block, ".//LegalRadio")
            
            # Address information
            applicant.address1 = self._get_text(block, ".//sfAssigneeAddress/address-1")
            applicant.address2 = self._get_text(block, ".//sfAssigneeAddress/address-2")
            applicant.city = self._get_text(block, ".//sfAssigneeAddress/city")
            applicant.state = self._get_text(block, ".//sfAssigneeAddress/state")
            applicant.postcode = self._get_text(block, ".//sfAssigneeAddress/postcode")
            applicant.country = self._get_text(block, ".//sfAssigneeAddress/txtCorrCtry")
            applicant.phone = self._get_text(block, ".//sfAssigneeAddress/phone")
            applicant.fax = self._get_text(block, ".//sfAssigneeAddress/fax")
            
            # Email
            applicant.email = self._get_text(block, ".//sfAssigneeEmail/email")
            
            # Only add if we found meaningful data
            if applicant.organization_name or applicant.first_name or applicant.last_name:
                extracted.applicants.append(applicant)
    
    def _extract_correspondence(self, root: ET.Element, extracted: ExtractedXFAData):
        """Extract correspondence information from ContentArea2"""
        
        # Customer number
        extracted.correspondence_customer_number = self._get_text(root, ".//sfCorrCustNo/customerNumber")
        
        # Address fields
        extracted.correspondence_name1 = self._get_text(root, ".//sfCorrAddress/Name1")
        extracted.correspondence_name2 = self._get_text(root, ".//sfCorrAddress/Name2")
        extracted.correspondence_address1 = self._get_text(root, ".//sfCorrAddress/address1")
        extracted.correspondence_address2 = self._get_text(root, ".//sfCorrAddress/address2")
        extracted.correspondence_city = self._get_text(root, ".//sfCorrAddress/city")
        extracted.correspondence_state = self._get_text(root, ".//sfCorrAddress/state")
        extracted.correspondence_country = self._get_text(root, ".//sfCorrAddress/corrCountry")
        extracted.correspondence_postcode = self._get_text(root, ".//sfCorrAddress/postcode")
        extracted.correspondence_phone = self._get_text(root, ".//sfCorrAddress/phone")
        extracted.correspondence_fax = self._get_text(root, ".//sfCorrAddress/fax")
        
        # Email
        extracted.correspondence_email = self._get_text(root, ".//sfemail/email")
    
    def _get_text(self, element: ET.Element, xpath: str) -> Optional[str]:
        """Safely extract text from XML element"""
        found = element.find(xpath)
        if found is not None and found.text:
            return found.text.strip()
        return None

class FieldComparator:
    """Compares fields between source metadata and extracted XFA data"""
    
    def __init__(self, config: ValidationConfig):
        self.config = config
        self.country_codes = self._load_country_codes()
        self.state_codes = self._load_state_codes()
    
    def compare_fields(
        self, 
        source: PatentApplicationMetadata, 
        extracted: ExtractedXFAData
    ) -> List[FieldMismatch]:
        """
        Compare all fields between source and extracted data.
        
        Returns:
            List[FieldMismatch]: All mismatches found
        """
        mismatches = []
        
        # Compare application-level fields
        mismatches.extend(self._compare_application_fields(source, extracted))
        
        # Compare inventors
        mismatches.extend(self._compare_inventors(source.inventors, extracted.inventors))
        
        # Compare applicants
        mismatches.extend(self._compare_applicants(source.applicants, extracted.applicants))
        
        # Compare correspondence
        if source.correspondence_address:
            mismatches.extend(self._compare_correspondence(source.correspondence_address, extracted))
        
        return mismatches
    
    def _compare_application_fields(
        self, 
        source: PatentApplicationMetadata, 
        extracted: ExtractedXFAData
    ) -> List[FieldMismatch]:
        """Compare application-level fields"""
        mismatches = []
        
        # Title comparison
        if source.title != extracted.title:
            severity = ValidationSeverity.ERROR if not extracted.title else ValidationSeverity.WARNING
            mismatches.append(FieldMismatch(
                field_path="title",
                expected_value=source.title,
                actual_value=extracted.title,
                severity=severity,
                description="Application title mismatch" if extracted.title else "Application title is missing",
                category=ValidationCategory.APPLICATION_INFO
            ))
        
        # Entity status comparison
        if source.entity_status:
            normalized_source = self._normalize_entity_status(source.entity_status)
            if normalized_source != extracted.entity_status:
                mismatches.append(FieldMismatch(
                    field_path="entity_status",
                    expected_value=source.entity_status,
                    actual_value=extracted.entity_status,
                    severity=ValidationSeverity.WARNING,
                    description="Entity status normalization applied",
                    category=ValidationCategory.APPLICATION_INFO,
                    auto_corrected=True,
                    correction_applied=f"Normalized '{source.entity_status}' to '{extracted.entity_status}'"
                ))
        
        return mismatches
    
    def _compare_inventors(
        self, 
        source_inventors: List[Inventor], 
        extracted_inventors: List[ExtractedInventor]
    ) -> List[FieldMismatch]:
        """Compare inventor arrays"""
        mismatches = []
        
        # Check count mismatch
        if len(source_inventors) != len(extracted_inventors):
            mismatches.append(FieldMismatch(
                field_path="inventors.count",
                expected_value=str(len(source_inventors)),
                actual_value=str(len(extracted_inventors)),
                severity=ValidationSeverity.ERROR,
                description=f"Inventor count mismatch: expected {len(source_inventors)}, found {len(extracted_inventors)}",
                category=ValidationCategory.INVENTOR_DATA
            ))
        
        # Compare each inventor
        for i, (source_inv, extracted_inv) in enumerate(zip(source_inventors, extracted_inventors)):
            mismatches.extend(self._compare_single_inventor(source_inv, extracted_inv, i))
        
        return mismatches
    
    def _compare_single_inventor(
        self,
        source: Inventor,
        extracted: ExtractedInventor,
        index: int
    ) -> List[FieldMismatch]:
        """Compare a single inventor's fields"""
        mismatches = []
        prefix = f"inventors[{index}]"
        
        # Name fields - critical for USPTO submission
        name_fields = [
            ("first_name", source.first_name, extracted.first_name, ValidationSeverity.ERROR),
            ("middle_name", source.middle_name, extracted.middle_name, ValidationSeverity.WARNING),
            ("last_name", source.last_name, extracted.last_name, ValidationSeverity.ERROR),
            ("prefix", source.prefix, extracted.prefix, ValidationSeverity.INFO),
            ("suffix", source.suffix, extracted.suffix, ValidationSeverity.INFO)
        ]
        
        for field_name, source_val, extracted_val, default_severity in name_fields:
            # Check for missing required fields first
            if field_name in ["first_name", "last_name"]:
                if not source_val or not source_val.strip():
                    mismatches.append(FieldMismatch(
                        field_path=f"{prefix}.{field_name}",
                        expected_value=source_val,
                        actual_value=extracted_val,
                        severity=ValidationSeverity.ERROR,
                        description=f"Inventor {index + 1} {field_name} is required but missing",
                        category=ValidationCategory.INVENTOR_DATA
                    ))
                    continue
                
                if not extracted_val or not extracted_val.strip():
                    mismatches.append(FieldMismatch(
                        field_path=f"{prefix}.{field_name}",
                        expected_value=source_val,
                        actual_value=extracted_val,
                        severity=ValidationSeverity.ERROR,
                        description=f"Inventor {index + 1} {field_name} missing in generated XML",
                        category=ValidationCategory.INVENTOR_DATA
                    ))
                    continue
            
            normalized_source = self._normalize_name(source_val)
            normalized_extracted = self._normalize_name(extracted_val)
            
            if normalized_source != normalized_extracted:
                # Check if it's just a case normalization
                if source_val and extracted_val and source_val.lower() == extracted_val.lower():
                    severity = ValidationSeverity.INFO
                    description = f"Inventor {index + 1} {field_name} case normalized"
                    auto_corrected = True
                    correction = f"Normalized case from '{source_val}' to '{extracted_val}'"
                else:
                    severity = default_severity
                    description = f"Inventor {index + 1} {field_name} mismatch"
                    auto_corrected = False
                    correction = None
                
                mismatches.append(FieldMismatch(
                    field_path=f"{prefix}.{field_name}",
                    expected_value=source_val,
                    actual_value=extracted_val,
                    severity=severity,
                    description=description,
                    category=ValidationCategory.INVENTOR_DATA,
                    auto_corrected=auto_corrected,
                    correction_applied=correction
                ))
        
        return mismatches
    
    def _compare_applicants(
        self, 
        source_applicants: List[Applicant], 
        extracted_applicants: List[ExtractedApplicant]
    ) -> List[FieldMismatch]:
        """Compare applicant arrays"""
        mismatches = []
        
        # Check count mismatch
        if len(source_applicants) != len(extracted_applicants):
            mismatches.append(FieldMismatch(
                field_path="applicants.count",
                expected_value=str(len(source_applicants)),
                actual_value=str(len(extracted_applicants)),
                severity=ValidationSeverity.WARNING,
                description=f"Applicant count mismatch: expected {len(source_applicants)}, found {len(extracted_applicants)}",
                category=ValidationCategory.APPLICANT_DATA
            ))
        
        # Compare each applicant
        for i, (source_app, extracted_app) in enumerate(zip(source_applicants, extracted_applicants)):
            mismatches.extend(self._compare_single_applicant(source_app, extracted_app, i))
        
        return mismatches
    
    def _compare_single_applicant(
        self, 
        source: Applicant, 
        extracted: ExtractedApplicant, 
        index: int
    ) -> List[FieldMismatch]:
        """Compare a single applicant's fields"""
        mismatches = []
        prefix = f"applicants[{index}]"
        
        # Organization name
        source_org_name = getattr(source, 'org_name', None) or getattr(source, 'name', None)
        if source_org_name != extracted.organization_name:
            mismatches.append(FieldMismatch(
                field_path=f"{prefix}.organization_name",
                expected_value=source_org_name,
                actual_value=extracted.organization_name,
                severity=ValidationSeverity.ERROR if not extracted.organization_name else ValidationSeverity.WARNING,
                description=f"Applicant {index + 1} organization name mismatch",
                category=ValidationCategory.APPLICANT_DATA
            ))
        
        return mismatches
    
    def _compare_correspondence(self, source, extracted: ExtractedXFAData) -> List[FieldMismatch]:
        """Compare correspondence address fields"""
        mismatches = []
        
        # Compare key correspondence fields
        corr_fields = [
            ("name", getattr(source, 'name', None), extracted.correspondence_name1),
            ("address1", getattr(source, 'address1', None), extracted.correspondence_address1),
            ("city", getattr(source, 'city', None), extracted.correspondence_city),
            ("email", getattr(source, 'email', None), extracted.correspondence_email)
        ]
        
        for field_name, source_val, extracted_val in corr_fields:
            if source_val != extracted_val:
                mismatches.append(FieldMismatch(
                    field_path=f"correspondence.{field_name}",
                    expected_value=source_val,
                    actual_value=extracted_val,
                    severity=ValidationSeverity.WARNING,
                    description=f"Correspondence {field_name} mismatch",
                    category=ValidationCategory.CORRESPONDENCE
                ))
        
        return mismatches
    
    def _normalize_name(self, name: Optional[str]) -> Optional[str]:
        """Normalize name for comparison"""
        if not name:
            return None
        if self.config.normalize_names:
            return name.strip().title()
        return name.strip()
    
    def _normalize_entity_status(self, status: str) -> str:
        """Normalize entity status"""
        status_lower = status.lower().strip()
        if status_lower in ["small", "small entity"]:
            return "small"
        elif status_lower in ["micro", "micro entity"]:
            return "micro"
        else:
            return "undiscounted"
    
    def _load_country_codes(self) -> Dict[str, str]:
        """Load country name to code mappings"""
        return {
            "united states": "US", "usa": "US", "united states of america": "US",
            "united kingdom": "GB", "uk": "GB", "great britain": "GB",
            "canada": "CA", "india": "IN", "china": "CN", "japan": "JP",
            "germany": "DE", "france": "FR", "australia": "AU", "brazil": "BR"
        }
    
    def _load_state_codes(self) -> Dict[str, str]:
        """Load state name to code mappings"""
        return {
            "CALIFORNIA": "CA", "TEXAS": "TX", "FLORIDA": "FL", "NEW YORK": "NY",
            "MASSACHUSETTS": "MA", "ILLINOIS": "IL", "PENNSYLVANIA": "PA"
        }

class ADSValidator:
    """Main ADS validation service"""
    
    def __init__(self, config: ValidationConfig = None):
        self.config = config or ValidationConfig()
        self.extractor = XFAFieldExtractor()
        self.comparator = FieldComparator(self.config)
    
    def validate_ads_output(
        self, 
        xfa_xml: str, 
        source_metadata: PatentApplicationMetadata
    ) -> ADSGenerationResponse:
        """
        Main validation function - validates generated XFA XML against source metadata.
        
        Args:
            xfa_xml: Generated XFA datasets XML string
            source_metadata: Original patent application metadata
            
        Returns:
            ADSGenerationResponse: Complete validation result with report
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting ADS validation for application: {source_metadata.title}")
            
            # Extract fields from XFA XML
            extracted_data = self.extractor.extract_fields_from_xml(xfa_xml)
            
            # Check if XML structure is valid
            if not extracted_data.xml_structure_valid:
                return self._create_error_response(
                    "Invalid XML structure",
                    extracted_data.extraction_warnings,
                    start_time,
                    len(xfa_xml)
                )
            
            # Compare fields
            mismatches = self.comparator.compare_fields(source_metadata, extracted_data)
            
            # Generate validation report
            report = self._generate_validation_report(mismatches, xfa_xml, start_time, source_metadata)
            
            # Determine if generation should be blocked
            blocking_errors = [m for m in mismatches if m.severity == ValidationSeverity.ERROR]
            generation_blocked = len(blocking_errors) > 0
            
            # Create success message
            if generation_blocked:
                message = f"PDF generation blocked due to {len(blocking_errors)} critical errors"
            elif report.summary.warnings_count > 0:
                message = f"PDF generated with {report.summary.warnings_count} warnings"
            else:
                message = "PDF generated successfully with no validation issues"
            
            logger.info(f"Validation completed: {message}")
            
            return ADSGenerationResponse(
                success=not generation_blocked,
                pdf_generated=not generation_blocked,
                validation_report=report,
                generation_blocked=generation_blocked,
                blocking_errors=blocking_errors,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            return self._create_error_response(
                f"Validation system error: {str(e)}",
                [],
                start_time,
                len(xfa_xml)
            )
    
    def _generate_validation_report(
        self, 
        mismatches: List[FieldMismatch], 
        xfa_xml: str, 
        start_time: datetime,
        source_metadata: PatentApplicationMetadata
    ) -> ValidationReport:
        """Generate comprehensive validation report"""
        
        # Calculate summary statistics
        errors = [m for m in mismatches if m.severity == ValidationSeverity.ERROR]
        warnings = [m for m in mismatches if m.severity == ValidationSeverity.WARNING]
        info = [m for m in mismatches if m.severity == ValidationSeverity.INFO]
        auto_corrected = [m for m in mismatches if m.auto_corrected]
        
        # Calculate validation score
        total_issues = len(errors) + len(warnings) + len(info)
        if total_issues == 0:
            validation_score = 1.0
        else:
            # Weight errors more heavily than warnings
            weighted_issues = len(errors) * 1.0 + len(warnings) * 0.5 + len(info) * 0.1
            validation_score = max(0.0, 1.0 - (weighted_issues / 20.0))  # Normalize to 0-1
        
        # Determine categories checked
        categories_checked = list(set([m.category for m in mismatches]))
        if not categories_checked:
            categories_checked = [ValidationCategory.STRUCTURAL]
        
        # Estimate total fields checked
        total_fields = (
            len(source_metadata.inventors) * 8 +  # 8 fields per inventor
            len(source_metadata.applicants) * 6 +  # 6 fields per applicant
            5  # Application-level fields
        )
        
        # Generate metadata hash for tracking
        metadata_str = f"{source_metadata.title}_{len(source_metadata.inventors)}_{len(source_metadata.applicants)}"
        metadata_hash = hashlib.md5(metadata_str.encode()).hexdigest()[:8]
        
        summary = ValidationSummary(
            total_fields_checked=total_fields,
            errors_count=len(errors),
            warnings_count=len(warnings),
            info_count=len(info),
            auto_corrections_count=len(auto_corrected),
            validation_score=validation_score,
            categories_checked=categories_checked
        )
        
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            summary=summary,
            mismatches=mismatches,
            processing_time_ms=processing_time,
            xfa_xml_size=len(xfa_xml),
            source_metadata_hash=metadata_hash
        )
    
    def _create_error_response(
        self, 
        error_message: str, 
        warnings: List[str], 
        start_time: datetime,
        xml_size: int
    ) -> ADSGenerationResponse:
        """Create error response for validation failures"""
        
        error_mismatch = FieldMismatch(
            field_path="validation.system",
            expected_value="success",
            actual_value="error",
            severity=ValidationSeverity.ERROR,
            description=error_message,
            category=ValidationCategory.STRUCTURAL
        )
        
        summary = ValidationSummary(
            total_fields_checked=0,
            errors_count=1,
            warnings_count=len(warnings),
            validation_score=0.0,
            categories_checked=[ValidationCategory.STRUCTURAL]
        )
        
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        error_report = ValidationReport(
            is_valid=False,
            summary=summary,
            mismatches=[error_mismatch],
            processing_time_ms=processing_time,
            xfa_xml_size=xml_size
        )
        
        return ADSGenerationResponse(
            success=False,
            pdf_generated=False,
            validation_report=error_report,
            generation_blocked=True,
            blocking_errors=[error_mismatch],
            message=error_message
        )