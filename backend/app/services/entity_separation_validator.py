"""
Entity separation validator to prevent applicant/inventor cross-contamination
"""

import re
import logging
from typing import Dict, List, Optional, Any
from app.models.enhanced_extraction import (
    EnhancedInventor, EnhancedApplicant, ValidationResult, 
    CrossFieldValidationResult, DataCompleteness
)

logger = logging.getLogger(__name__)

class EntitySeparationValidator:
    """Comprehensive validation to prevent inventor/applicant data confusion"""
    
    def __init__(self):
        self.corporate_indicators = [
            "inc", "incorporated", "llc", "corp", "corporation", "ltd", "limited",
            "company", "co", "enterprises", "group", "holdings", "technologies",
            "systems", "solutions", "industries", "international", "global"
        ]
        
        self.business_address_indicators = [
            "suite", "ste", "floor", "fl", "building", "bldg", "plaza", "center",
            "office", "tower", "complex", "park", "campus", "headquarters", "hq"
        ]
        
        self.individual_name_patterns = [
            r"^[A-Z][a-z]+ [A-Z][a-z]+$",  # First Last
            r"^[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+$",  # First M. Last
            r"^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+$"  # First Middle Last
        ]
    
    def validate_inventor_purity(self, inventor: EnhancedInventor) -> ValidationResult:
        """Ensure inventor contains only individual person data"""
        errors = []
        warnings = []
        
        # Check for corporate indicators in name fields
        name_fields = [
            ("given_name", inventor.given_name),
            ("family_name", inventor.family_name),
            ("full_name", inventor.full_name)
        ]
        
        for field_name, value in name_fields:
            if value:
                for indicator in self.corporate_indicators:
                    if indicator.lower() in value.lower():
                        errors.append(
                            f"Corporate indicator '{indicator}' found in inventor {field_name}: '{value}'"
                        )
        
        # Check for business address indicators
        if inventor.street_address:
            for indicator in self.business_address_indicators:
                if indicator.lower() in inventor.street_address.lower():
                    warnings.append(
                        f"Business address indicator '{indicator}' in inventor address: '{inventor.street_address}'"
                    )
        
        # Validate name patterns (should look like individual names)
        if inventor.full_name:
            is_individual_pattern = any(
                re.match(pattern, inventor.full_name.strip()) 
                for pattern in self.individual_name_patterns
            )
            if not is_individual_pattern:
                warnings.append(
                    f"Inventor full_name doesn't match individual name patterns: '{inventor.full_name}'"
                )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            confidence_score=1.0 - (len(errors) * 0.5) - (len(warnings) * 0.1)
        )
    
    def validate_applicant_completeness(self, applicant: EnhancedApplicant) -> ValidationResult:
        """Ensure applicant data is complete and properly structured"""
        errors = []
        warnings = []
        
        # Check entity type consistency
        has_org_name = bool(applicant.organization_name)
        has_individual_name = bool(applicant.individual_given_name or applicant.individual_family_name)
        
        if not has_org_name and not has_individual_name:
            errors.append("Applicant must have either organization name or individual names")
        
        if has_org_name and has_individual_name:
            warnings.append("Applicant has both organization and individual names - verify entity type")
        
        # Validate organization name format
        if applicant.organization_name:
            org_name = applicant.organization_name.lower()
            has_legal_suffix = any(
                suffix in org_name for suffix in ["inc", "llc", "corp", "ltd", "company"]
            )
            if not has_legal_suffix:
                warnings.append(
                    f"Organization name may be missing legal suffix: '{applicant.organization_name}'"
                )
        
        # Check address completeness
        required_address_fields = ["street_address", "city", "state", "country"]
        missing_fields = []
        for field in required_address_fields:
            if not getattr(applicant, field):
                missing_fields.append(field)
        
        if missing_fields:
            errors.append(f"Missing required applicant address fields: {missing_fields}")
        
        # Validate business address format
        if applicant.street_address:
            has_business_indicators = any(
                indicator.lower() in applicant.street_address.lower()
                for indicator in self.business_address_indicators
            )
            if not has_business_indicators and applicant.organization_name:
                warnings.append(
                    "Corporate applicant address may not be a business address"
                )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            confidence_score=1.0 - (len(errors) * 0.5) - (len(warnings) * 0.1)
        )
    
    def detect_cross_contamination(
        self, 
        inventors: List[EnhancedInventor], 
        applicants: List[EnhancedApplicant]
    ) -> CrossFieldValidationResult:
        """Detect if applicant data has been assigned to inventors or vice versa"""
        issues = []
        recommendations = []
        
        # Check if any inventor data looks like applicant data
        for i, inventor in enumerate(inventors):
            # Check for corporate names in inventor fields
            if inventor.given_name:
                for indicator in self.corporate_indicators:
                    if indicator.lower() in inventor.given_name.lower():
                        issues.append(
                            f"Inventor {i} given_name contains corporate indicator: '{inventor.given_name}'"
                        )
                        recommendations.append(
                            f"Move corporate name from inventor {i} to applicant organization_name"
                        )
            
            # Check for business addresses in inventor fields
            if inventor.street_address:
                business_score = sum(
                    1 for indicator in self.business_address_indicators
                    if indicator.lower() in inventor.street_address.lower()
                )
                if business_score >= 2:  # Multiple business indicators
                    issues.append(
                        f"Inventor {i} address appears to be business address: '{inventor.street_address}'"
                    )
                    recommendations.append(
                        f"Move business address from inventor {i} to applicant address"
                    )
        
        # Check if applicant data is missing when it should be present
        if not applicants and inventors:
            # Look for signs that inventors might actually be applicants
            potential_applicant_inventors = []
            for i, inventor in enumerate(inventors):
                if inventor.given_name:
                    corporate_score = sum(
                        1 for indicator in self.corporate_indicators
                        if indicator.lower() in inventor.given_name.lower()
                    )
                    if corporate_score > 0:
                        potential_applicant_inventors.append(i)
            
            if potential_applicant_inventors:
                issues.append(
                    f"No applicants found, but inventors {potential_applicant_inventors} contain corporate indicators"
                )
                recommendations.append(
                    "Review document for applicant/company information that may have been misclassified as inventors"
                )
        
        return CrossFieldValidationResult(
            validation_type="entity_separation",
            fields_involved=["inventors", "applicants"],
            is_consistent=len(issues) == 0,
            issues=issues,
            recommendations=recommendations,
            confidence_impact=-0.2 * len(issues)
        )
    
    def auto_fix_cross_contamination(
        self, 
        inventors: List[EnhancedInventor], 
        applicants: List[EnhancedApplicant]
    ) -> Dict[str, Any]:
        """Attempt to automatically fix cross-contamination issues"""
        
        fixes_applied = []
        inventors_to_remove = []
        applicants_to_add = []
        
        # Check inventors for corporate data
        for i, inventor in enumerate(inventors):
            corporate_issues = self._detect_corporate_data_in_inventor(inventor)
            
            if corporate_issues['has_corporate_name']:
                # Extract corporate name and create applicant
                org_name = self._extract_corporate_name(inventor)
                if org_name:
                    new_applicant = EnhancedApplicant(
                        organization_name=org_name,
                        street_address=inventor.street_address,
                        city=inventor.city,
                        state=inventor.state,
                        postal_code=inventor.postal_code,
                        country=inventor.country,
                        completeness=DataCompleteness.PARTIAL_NAME,
                        confidence_score=0.7  # Lower confidence due to correction
                    )
                    applicants_to_add.append(new_applicant)
                    inventors_to_remove.append(i)
                    fixes_applied.append(
                        f"Moved corporate name '{org_name}' from inventor {i} to new applicant"
                    )
        
        return {
            'fixes_applied': fixes_applied,
            'inventors_to_remove': inventors_to_remove,
            'applicants_to_add': applicants_to_add
        }
    
    def _detect_corporate_data_in_inventor(self, inventor: EnhancedInventor) -> Dict[str, bool]:
        """Detect if inventor contains corporate data"""
        
        issues = {
            'has_corporate_name': False,
            'has_business_address': False,
            'corporate_indicators_found': [],
            'business_indicators_found': []
        }
        
        # Check name fields for corporate indicators
        name_fields = [inventor.given_name, inventor.family_name, inventor.full_name]
        for name_field in name_fields:
            if name_field:
                for indicator in self.corporate_indicators:
                    if indicator.lower() in name_field.lower():
                        issues['has_corporate_name'] = True
                        issues['corporate_indicators_found'].append(indicator)
        
        # Check address for business indicators
        if inventor.street_address:
            for indicator in self.business_address_indicators:
                if indicator.lower() in inventor.street_address.lower():
                    issues['has_business_address'] = True
                    issues['business_indicators_found'].append(indicator)
        
        return issues
    
    def _extract_corporate_name(self, inventor: EnhancedInventor) -> Optional[str]:
        """Extract corporate name from inventor data"""
        
        # Priority order: full_name, given_name, family_name
        name_candidates = [
            inventor.full_name,
            inventor.given_name,
            inventor.family_name
        ]
        
        for name in name_candidates:
            if name:
                for indicator in self.corporate_indicators:
                    if indicator.lower() in name.lower():
                        return name.strip()
        
        return None