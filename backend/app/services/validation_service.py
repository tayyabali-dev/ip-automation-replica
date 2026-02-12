"""
Validation service for enhanced extraction results.
Implements comprehensive field validation, cross-field validation, and quality scoring.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
from dataclasses import dataclass

from app.models.enhanced_extraction import (
    EnhancedExtractionResult, EnhancedInventor, EnhancedApplicant,
    ValidationResult, FieldValidationResult, CrossFieldValidationResult,
    QualityMetrics, ConfidenceLevel, DataCompleteness
)
from app.services.entity_separation_validator import EntitySeparationValidator

logger = logging.getLogger(__name__)

@dataclass
class ValidationConfig:
    """Configuration for validation rules"""
    min_name_length: int = 1
    max_name_length: int = 100
    min_address_length: int = 5
    max_address_length: int = 200
    required_inventor_fields: List[str] = None
    required_applicant_fields: List[str] = None
    
    def __post_init__(self):
        if self.required_inventor_fields is None:
            self.required_inventor_fields = ["given_name", "family_name", "city", "state", "country"]
        if self.required_applicant_fields is None:
            self.required_applicant_fields = ["street_address", "city", "state", "country"]

class FieldValidator:
    """Validates individual fields"""
    
    def __init__(self, config: ValidationConfig = None):
        self.config = config or ValidationConfig()
        self.us_states = self._load_us_states()
        self.countries = self._load_countries()
    
    def validate_name(self, name: str, field_name: str) -> ValidationResult:
        """Validate name fields (given_name, family_name, etc.)"""
        errors = []
        warnings = []
        normalized_value = name
        
        if not name or not name.strip():
            errors.append(f"{field_name} is required")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                normalized_value=None,
                confidence_score=0.0
            )
        
        # Normalize name
        normalized_value = name.strip().title()
        
        # Length validation
        if len(normalized_value) < self.config.min_name_length:
            errors.append(f"{field_name} is too short (minimum {self.config.min_name_length} characters)")
        elif len(normalized_value) > self.config.max_name_length:
            errors.append(f"{field_name} is too long (maximum {self.config.max_name_length} characters)")
        
        # Character validation
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", normalized_value):
            warnings.append(f"{field_name} contains unusual characters")
        
        # Common issues
        if normalized_value.isupper():
            warnings.append(f"{field_name} is all uppercase - normalized to title case")
        
        confidence_score = 1.0 - (len(warnings) * 0.1) - (len(errors) * 0.5)
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            normalized_value=normalized_value,
            confidence_score=confidence_score
        )
    
    def validate_address(self, address: str, field_name: str) -> ValidationResult:
        """Validate address fields"""
        errors = []
        warnings = []
        normalized_value = address
        
        if not address or not address.strip():
            errors.append(f"{field_name} is required")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                normalized_value=None,
                confidence_score=0.0
            )
        
        # Normalize address
        normalized_value = address.strip()
        
        # Length validation
        if len(normalized_value) < self.config.min_address_length:
            errors.append(f"{field_name} is too short (minimum {self.config.min_address_length} characters)")
        elif len(normalized_value) > self.config.max_address_length:
            errors.append(f"{field_name} is too long (maximum {self.config.max_address_length} characters)")
        
        # Basic format validation
        if not re.search(r'\d', normalized_value) and field_name == "street_address":
            warnings.append("Street address typically contains numbers")
        
        confidence_score = 1.0 - (len(warnings) * 0.1) - (len(errors) * 0.5)
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            normalized_value=normalized_value,
            confidence_score=confidence_score
        )
    
    def validate_state(self, state: str, country: str = "US") -> ValidationResult:
        """Validate state/province field"""
        errors = []
        warnings = []
        normalized_value = state
        
        if not state or not state.strip():
            errors.append("State/province is required")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                normalized_value=None,
                confidence_score=0.0
            )
        
        normalized_value = state.strip().upper()
        
        # US state validation
        if country.upper() in ["US", "USA", "UNITED STATES"]:
            if normalized_value not in self.us_states:
                # Try to find close match
                close_match = self._find_close_state_match(normalized_value)
                if close_match:
                    warnings.append(f"State '{state}' normalized to '{close_match}'")
                    normalized_value = close_match
                else:
                    errors.append(f"'{state}' is not a valid US state")
        
        confidence_score = 1.0 - (len(warnings) * 0.1) - (len(errors) * 0.5)
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            normalized_value=normalized_value,
            confidence_score=confidence_score
        )
    
    def validate_country(self, country: str) -> ValidationResult:
        """Validate country field"""
        errors = []
        warnings = []
        normalized_value = country
        
        if not country or not country.strip():
            errors.append("Country is required")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                normalized_value=None,
                confidence_score=0.0
            )
        
        normalized_value = country.strip()
        
        # Normalize common country formats
        country_upper = normalized_value.upper()
        if country_upper in ["USA", "UNITED STATES", "UNITED STATES OF AMERICA"]:
            normalized_value = "US"
        elif country_upper in self.countries:
            normalized_value = country_upper
        elif len(normalized_value) == 2:
            normalized_value = normalized_value.upper()
        else:
            # Try to find in full country names
            found = False
            for code, name in self.countries.items():
                if name.upper() == country_upper:
                    normalized_value = code
                    found = True
                    break
            
            if not found:
                warnings.append(f"Country '{country}' not recognized - keeping as provided")
        
        confidence_score = 1.0 - (len(warnings) * 0.1) - (len(errors) * 0.5)
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            normalized_value=normalized_value,
            confidence_score=confidence_score
        )
    
    def validate_date(self, date_str: str) -> ValidationResult:
        """Validate date format and convert to YYYY-MM-DD"""
        errors = []
        warnings = []
        normalized_value = date_str
        
        if not date_str or not date_str.strip():
            return ValidationResult(
                is_valid=True,  # Date is optional
                errors=errors,
                normalized_value=None,
                confidence_score=1.0
            )
        
        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d",      # 2023-12-31
            "%m/%d/%Y",      # 12/31/2023
            "%m-%d-%Y",      # 12-31-2023
            "%d/%m/%Y",      # 31/12/2023
            "%B %d, %Y",     # December 31, 2023
            "%b %d, %Y",     # Dec 31, 2023
            "%Y%m%d",        # 20231231
        ]
        
        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt).date()
                break
            except ValueError:
                continue
        
        if parsed_date is None:
            errors.append(f"Could not parse date '{date_str}'")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                normalized_value=None,
                confidence_score=0.0
            )
        
        # Validate date range
        current_date = date.today()
        if parsed_date > current_date:
            warnings.append(f"Date '{date_str}' is in the future")
        elif parsed_date.year < 1900:
            warnings.append(f"Date '{date_str}' is very old")
        
        # Normalize to YYYY-MM-DD format
        normalized_value = parsed_date.strftime("%Y-%m-%d")
        
        confidence_score = 1.0 - (len(warnings) * 0.1) - (len(errors) * 0.5)
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            normalized_value=normalized_value,
            confidence_score=confidence_score
        )
    
    def validate_email(self, email: str) -> ValidationResult:
        """Validate email address format"""
        errors = []
        warnings = []
        normalized_value = email
        
        if not email or not email.strip():
            return ValidationResult(
                is_valid=True,  # Email is optional
                errors=errors,
                normalized_value=None,
                confidence_score=1.0
            )
        
        normalized_value = email.strip().lower()
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, normalized_value):
            errors.append(f"'{email}' is not a valid email format")
        
        confidence_score = 1.0 - (len(warnings) * 0.1) - (len(errors) * 0.5)
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            normalized_value=normalized_value,
            confidence_score=confidence_score
        )
    
    def _load_us_states(self) -> set:
        """Load US state codes"""
        return {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
            'DC'  # District of Columbia
        }
    
    def _load_countries(self) -> Dict[str, str]:
        """Load country codes and names"""
        return {
            'US': 'United States',
            'CA': 'Canada',
            'GB': 'United Kingdom',
            'DE': 'Germany',
            'FR': 'France',
            'JP': 'Japan',
            'CN': 'China',
            'IN': 'India',
            'AU': 'Australia',
            'BR': 'Brazil',
            # Add more as needed
        }
    
    def _find_close_state_match(self, state: str) -> Optional[str]:
        """Find close match for state name"""
        state_names = {
            'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR',
            'CALIFORNIA': 'CA', 'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE',
            'FLORIDA': 'FL', 'GEORGIA': 'GA', 'HAWAII': 'HI', 'IDAHO': 'ID',
            'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS',
            'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
            'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS',
            'MISSOURI': 'MO', 'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV',
            'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 'NEW YORK': 'NY',
            'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK',
            'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
            'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT',
            'VERMONT': 'VT', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV',
            'WISCONSIN': 'WI', 'WYOMING': 'WY'
        }
        
        return state_names.get(state.upper())


class CrossFieldValidator:
    """Validates relationships between fields"""
    
    def __init__(self):
        self.field_validator = FieldValidator()
    
    def validate_inventor_consistency(self, inventor: EnhancedInventor) -> CrossFieldValidationResult:
        """Validate consistency within inventor data"""
        issues = []
        recommendations = []
        confidence_impact = 0.0
        
        # Check name consistency
        if inventor.full_name and inventor.given_name and inventor.family_name:
            expected_full = f"{inventor.given_name} {inventor.family_name}"
            if inventor.middle_name:
                expected_full = f"{inventor.given_name} {inventor.middle_name} {inventor.family_name}"
            
            if inventor.full_name.lower() != expected_full.lower():
                issues.append(f"Full name '{inventor.full_name}' doesn't match component names")
                confidence_impact -= 0.1
        
        # Check address consistency
        if inventor.state and inventor.country:
            if inventor.country.upper() in ["US", "USA"] and inventor.state not in self.field_validator.us_states:
                issues.append(f"State '{inventor.state}' not valid for country '{inventor.country}'")
                confidence_impact -= 0.2
        
        # Check completeness
        required_fields = ["given_name", "family_name", "city", "state", "country"]
        missing_fields = [field for field in required_fields if not getattr(inventor, field)]
        if missing_fields:
            recommendations.append(f"Missing required fields: {', '.join(missing_fields)}")
            confidence_impact -= len(missing_fields) * 0.1
        
        return CrossFieldValidationResult(
            validation_type="inventor_consistency",
            fields_involved=["given_name", "family_name", "full_name", "state", "country"],
            is_consistent=len(issues) == 0,
            issues=issues,
            recommendations=recommendations,
            confidence_impact=confidence_impact
        )
    
    def validate_applicant_consistency(self, applicant: EnhancedApplicant) -> CrossFieldValidationResult:
        """Validate consistency within applicant data"""
        issues = []
        recommendations = []
        confidence_impact = 0.0
        
        # Check entity type consistency
        if applicant.organization_name and (applicant.individual_given_name or applicant.individual_family_name):
            issues.append("Applicant has both organization and individual names")
            confidence_impact -= 0.2
        
        if not applicant.organization_name and not (applicant.individual_given_name and applicant.individual_family_name):
            issues.append("Applicant must have either organization name or individual names")
            confidence_impact -= 0.3
        
        # Check address consistency
        if applicant.state and applicant.country:
            if applicant.country.upper() in ["US", "USA"] and applicant.state not in self.field_validator.us_states:
                issues.append(f"State '{applicant.state}' not valid for country '{applicant.country}'")
                confidence_impact -= 0.2
        
        return CrossFieldValidationResult(
            validation_type="applicant_consistency",
            fields_involved=["organization_name", "individual_given_name", "individual_family_name", "state", "country"],
            is_consistent=len(issues) == 0,
            issues=issues,
            recommendations=recommendations,
            confidence_impact=confidence_impact
        )


class ValidationService:
    """Main validation service coordinating all validation activities"""
    
    def __init__(self, config: ValidationConfig = None):
        self.config = config or ValidationConfig()
        self.field_validator = FieldValidator(self.config)
        self.cross_validator = CrossFieldValidator()
        self.entity_separator = EntitySeparationValidator()
    
    async def validate_extraction_result(
        self,
        result: EnhancedExtractionResult
    ) -> EnhancedExtractionResult:
        """Perform comprehensive validation on extraction result"""
        
        try:
            # Step 1: Field-level validation
            await self._validate_all_fields(result)
            
            # Step 2: Entity separation validation
            await self._validate_entity_separation(result)
            
            # Step 3: Cross-field validation
            await self._validate_cross_field_relationships(result)
            
            # Step 4: Calculate quality metrics
            result.quality_metrics = self._calculate_quality_metrics(result)
            
            # Step 5: Determine if manual review is required
            result.manual_review_required = self._requires_manual_review(result)
            
            # Step 6: Generate recommendations
            result.recommendations = self._generate_recommendations(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            # Return result with validation error flag
            result.extraction_warnings.append(f"Validation failed: {str(e)}")
            result.manual_review_required = True
            return result
    
    async def _validate_all_fields(self, result: EnhancedExtractionResult):
        """Validate all individual fields"""
        
        # Validate core application fields
        if result.title:
            validation = self.field_validator.validate_name(result.title, "title")
            result.field_validations.append(FieldValidationResult(
                field_name="title",
                original_value=result.title,
                validation_result=validation
            ))
            if validation.normalized_value:
                result.title = validation.normalized_value
        
        if result.filing_date:
            validation = self.field_validator.validate_date(result.filing_date)
            result.field_validations.append(FieldValidationResult(
                field_name="filing_date",
                original_value=result.filing_date,
                validation_result=validation
            ))
            if validation.normalized_value:
                result.filing_date = validation.normalized_value
        
        # Validate inventors
        for i, inventor in enumerate(result.inventors):
            await self._validate_inventor_fields(inventor, i, result)
        
        # Validate applicants
        for i, applicant in enumerate(result.applicants):
            await self._validate_applicant_fields(applicant, i, result)
    
    async def _validate_inventor_fields(
        self,
        inventor: EnhancedInventor,
        index: int,
        result: EnhancedExtractionResult
    ):
        """Validate all fields for a single inventor"""
        
        prefix = f"inventor_{index}"
        
        # Validate names
        if inventor.given_name:
            validation = self.field_validator.validate_name(inventor.given_name, f"{prefix}_given_name")
            result.field_validations.append(FieldValidationResult(
                field_name=f"{prefix}_given_name",
                original_value=inventor.given_name,
                validation_result=validation
            ))
            if validation.normalized_value:
                inventor.given_name = validation.normalized_value
        
        if inventor.family_name:
            validation = self.field_validator.validate_name(inventor.family_name, f"{prefix}_family_name")
            result.field_validations.append(FieldValidationResult(
                field_name=f"{prefix}_family_name",
                original_value=inventor.family_name,
                validation_result=validation
            ))
            if validation.normalized_value:
                inventor.family_name = validation.normalized_value
        
        # Validate addresses
        if inventor.street_address:
            validation = self.field_validator.validate_address(inventor.street_address, f"{prefix}_street_address")
            result.field_validations.append(FieldValidationResult(
                field_name=f"{prefix}_street_address",
                original_value=inventor.street_address,
                validation_result=validation
            ))
            if validation.normalized_value:
                inventor.street_address = validation.normalized_value
        
        if inventor.city:
            validation = self.field_validator.validate_name(inventor.city, f"{prefix}_city")
            result.field_validations.append(FieldValidationResult(
                field_name=f"{prefix}_city",
                original_value=inventor.city,
                validation_result=validation
            ))
            if validation.normalized_value:
                inventor.city = validation.normalized_value
        
        if inventor.state:
            validation = self.field_validator.validate_state(inventor.state, inventor.country or "US")
            result.field_validations.append(FieldValidationResult(
                field_name=f"{prefix}_state",
                original_value=inventor.state,
                validation_result=validation
            ))
            if validation.normalized_value:
                inventor.state = validation.normalized_value
        
        if inventor.country:
            validation = self.field_validator.validate_country(inventor.country)
            result.field_validations.append(FieldValidationResult(
                field_name=f"{prefix}_country",
                original_value=inventor.country,
                validation_result=validation
            ))
            if validation.normalized_value:
                inventor.country = validation.normalized_value
    
    async def _validate_applicant_fields(
        self,
        applicant: EnhancedApplicant,
        index: int,
        result: EnhancedExtractionResult
    ):
        """Validate all fields for a single applicant"""
        
        prefix = f"applicant_{index}"
        
        # Validate organization name
        if applicant.organization_name:
            validation = self.field_validator.validate_name(applicant.organization_name, f"{prefix}_organization_name")
            result.field_validations.append(FieldValidationResult(
                field_name=f"{prefix}_organization_name",
                original_value=applicant.organization_name,
                validation_result=validation
            ))
            if validation.normalized_value:
                applicant.organization_name = validation.normalized_value
        
        # Validate email
        if applicant.email_address:
            validation = self.field_validator.validate_email(applicant.email_address)
            result.field_validations.append(FieldValidationResult(
                field_name=f"{prefix}_email_address",
                original_value=applicant.email_address,
                validation_result=validation
            ))
            if validation.normalized_value:
                applicant.email_address = validation.normalized_value
    
    async def _validate_entity_separation(self, result: EnhancedExtractionResult):
        """Validate entity separation between inventors and applicants"""
        
        try:
            # Validate inventor purity (no corporate data in inventor fields)
            for i, inventor in enumerate(result.inventors):
                validation_result = self.entity_separator.validate_inventor_purity(inventor)
                
                if not validation_result.is_valid:
                    # Add cross-field validation result for tracking
                    result.cross_field_validations.append(CrossFieldValidationResult(
                        validation_type="entity_separation_inventor",
                        fields_involved=[f"inventor_{i}_given_name", f"inventor_{i}_family_name",
                                       f"inventor_{i}_street_address", f"inventor_{i}_city"],
                        is_consistent=False,
                        issues=validation_result.errors,
                        recommendations=validation_result.warnings,
                        confidence_impact=-0.3
                    ))
                    
                    # Add to extraction warnings
                    result.extraction_warnings.extend([
                        f"Inventor {i+1}: {error}" for error in validation_result.errors
                    ])
                    
                    # Apply auto-fixes if available
                    if hasattr(validation_result, 'auto_fix_suggestions') and validation_result.auto_fix_suggestions:
                        for suggestion in validation_result.auto_fix_suggestions:
                            result.extraction_warnings.append(f"Auto-fix suggestion for Inventor {i+1}: {suggestion}")
            
            # Validate applicant completeness
            for i, applicant in enumerate(result.applicants):
                validation_result = self.entity_separator.validate_applicant_completeness(applicant)
                
                if not validation_result.is_valid:
                    # Add cross-field validation result for tracking
                    result.cross_field_validations.append(CrossFieldValidationResult(
                        validation_type="entity_separation_applicant",
                        fields_involved=[f"applicant_{i}_organization_name", f"applicant_{i}_individual_given_name",
                                       f"applicant_{i}_street_address", f"applicant_{i}_city"],
                        is_consistent=False,
                        issues=validation_result.errors,
                        recommendations=validation_result.warnings,
                        confidence_impact=-0.2
                    ))
                    
                    # Add to extraction warnings
                    result.extraction_warnings.extend([
                        f"Applicant {i+1}: {error}" for error in validation_result.errors
                    ])
            
            # Detect cross-contamination between inventors and applicants
            contamination_result = self.entity_separator.detect_cross_contamination(result.inventors, result.applicants)
            
            # Add the contamination result to cross-field validations
            result.cross_field_validations.append(contamination_result)
            
            # If contamination is detected (not consistent), add warnings and mark for review
            if not contamination_result.is_consistent:
                # Add to extraction warnings
                result.extraction_warnings.extend([
                    f"Cross-contamination: {issue}" for issue in contamination_result.issues
                ])
                
                # Add recommendations
                result.extraction_warnings.extend([
                    f"Recommendation: {rec}" for rec in contamination_result.recommendations
                ])
                
                # Mark for manual review due to contamination
                result.manual_review_required = True
                
        except Exception as e:
            logger.error(f"Entity separation validation failed: {e}", exc_info=True)
            result.extraction_warnings.append(f"Entity separation validation error: {str(e)}")
            result.manual_review_required = True
    
    async def _validate_cross_field_relationships(self, result: EnhancedExtractionResult):
        """Validate relationships between fields"""
        
        # Validate each inventor's internal consistency
        for i, inventor in enumerate(result.inventors):
            validation = self.cross_validator.validate_inventor_consistency(inventor)
            result.cross_field_validations.append(validation)
        
        # Validate each applicant's internal consistency
        for i, applicant in enumerate(result.applicants):
            validation = self.cross_validator.validate_applicant_consistency(applicant)
            result.cross_field_validations.append(validation)
    
    def _calculate_quality_metrics(self, result: EnhancedExtractionResult) -> QualityMetrics:
        """Calculate comprehensive quality metrics"""
        
        # Count required and optional fields
        required_populated = 0
        total_required = 2  # title, inventors
        optional_populated = 0
        total_optional = 4  # application_number, filing_date, entity_status, applicants
        
        # Check core fields
        if result.title:
            required_populated += 1
        if result.inventors:
            required_populated += 1
        
        if result.application_number:
            optional_populated += 1
        if result.filing_date:
            optional_populated += 1
        if result.entity_status:
            optional_populated += 1
        if result.applicants:
            optional_populated += 1
        
        # Calculate scores
        completeness_score = required_populated / total_required if total_required > 0 else 1.0
        
        # Accuracy score based on validation results
        if result.field_validations:
            valid_fields = sum(1 for v in result.field_validations if v.validation_result.is_valid)
            accuracy_score = valid_fields / len(result.field_validations)
        else:
            accuracy_score = 0.8  # Default when no validations
        
        # Confidence score from individual field confidence
        confidence_scores = []
        for inventor in result.inventors:
            confidence_scores.append(inventor.confidence_score)
        for applicant in result.applicants:
            confidence_scores.append(applicant.confidence_score)
        confidence_score = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        # Consistency score from cross-field validations
        if result.cross_field_validations:
            consistent_validations = sum(1 for v in result.cross_field_validations if v.is_consistent)
            consistency_score = consistent_validations / len(result.cross_field_validations)
        else:
            consistency_score = 0.8  # Default when no cross-validations
        
        # Overall quality score (weighted average)
        overall_score = (
            completeness_score * 0.3 +
            accuracy_score * 0.3 +
            confidence_score * 0.2 +
            consistency_score * 0.2
        )
        
        # Count validation issues
        validation_errors = sum(1 for v in result.field_validations if not v.validation_result.is_valid)
        validation_warnings = sum(len(v.validation_result.warnings) for v in result.field_validations)
        
        return QualityMetrics(
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            confidence_score=confidence_score,
            consistency_score=consistency_score,
            overall_quality_score=overall_score,
            required_fields_populated=required_populated,
            total_required_fields=total_required,
            optional_fields_populated=optional_populated,
            total_optional_fields=total_optional,
            validation_errors=validation_errors,
            validation_warnings=validation_warnings
        )
    
    def _requires_manual_review(self, result: EnhancedExtractionResult) -> bool:
        """Determine if manual review is required"""
        
        # Check for validation errors
        if any(not v.validation_result.is_valid for v in result.field_validations):
            return True
        
        # Check for cross-field validation issues
        if any(not v.is_consistent for v in result.cross_field_validations):
            return True
        
        # Check overall quality score
        if result.quality_metrics.overall_quality_score < 0.7:
            return True
        
        # Check for missing required fields
        if not result.title or not result.inventors:
            return True
        
        return False
    
    def _generate_recommendations(self, result: EnhancedExtractionResult) -> List[str]:
        """Generate recommendations for improving data quality"""
        recommendations = []
        
        # Check for missing required fields
        if not result.title:
            recommendations.append("Title of invention is missing - this is required for USPTO submission")
        
        if not result.inventors:
            recommendations.append("No inventors found - at least one inventor is required")
        
        # Check inventor completeness
        incomplete_inventors = [
            i for i, inv in enumerate(result.inventors)
            if inv.completeness in [DataCompleteness.INCOMPLETE, DataCompleteness.PARTIAL_NAME, DataCompleteness.PARTIAL_ADDRESS]
        ]
        if incomplete_inventors:
            recommendations.append(f"Inventors {incomplete_inventors} have incomplete information")
        
        # Check for missing applicant information
        if not result.applicants:
            recommendations.append("No applicant information found - consider if inventors are also applicants")
        
        # Check for validation warnings
        warning_count = sum(len(v.validation_result.warnings) for v in result.field_validations)
        if warning_count > 5:
            recommendations.append(f"Multiple validation warnings ({warning_count}) - review data quality")
        
        # Check quality score
        if result.quality_metrics.overall_quality_score < 0.8:
            recommendations.append("Overall quality score is low - consider manual review")
        
        return recommendations
