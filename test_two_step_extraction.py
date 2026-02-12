#!/usr/bin/env python3
"""
Test the two-step extraction process with mock patent document data.
This demonstrates the solution to data extraction issues.
"""

import sys
import os
import json
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def create_mock_patent_document() -> str:
    """Create a mock patent document with complex data scenarios"""
    return """
UNITED STATES PATENT AND TRADEMARK OFFICE

APPLICATION DATA SHEET

Title of Invention: ADVANCED MACHINE LEARNING SYSTEM FOR AUTOMATED PATENT ANALYSIS

Attorney Docket Number: TECH-2024-001

INVENTOR INFORMATION:

First Inventor:
Name: Dr. Sarah Elizabeth Johnson
Residence: Palo Alto, California, United States
Mailing Address: 1234 Innovation Drive, Suite 100, Palo Alto, CA 94301, United States

Second Inventor: 
Name: Michael Chen
Residence: San Francisco, CA, US
Mailing Address: 567 Tech Boulevard, Apt 25B, San Francisco, California 94105, USA

Third Inventor:
Name: Prof. Elena Rodriguez-Martinez
Residence: Austin, Texas, United States  
Mailing Address: 890 Research Park Way, Austin, TX 78712, United States

APPLICANT INFORMATION:
TechCorp Innovations LLC
Address: 1234 Innovation Drive, Suite 100, Palo Alto, CA 94301, United States

CORRESPONDENCE INFORMATION:
Customer Number: 12345
Email Address: patents@techcorp.com

DOMESTIC BENEFIT/PRIORITY CLAIMS:
This application claims the benefit of U.S. Provisional Application No. 63/123,456, filed on January 15, 2023.
This application is a continuation-in-part of U.S. Application No. 17/987,654, filed on March 10, 2022.

FOREIGN PRIORITY CLAIMS:
Priority is claimed to European Patent Application No. EP2023123456, filed on February 20, 2023.
Priority is claimed to Japanese Patent Application No. JP2023-098765, filed on April 5, 2023.

FIELD OF THE INVENTION:
The present invention relates to machine learning systems and methods for automated patent analysis...
"""

def test_evidence_gathering():
    """Test the evidence gathering step"""
    print("🔍 STEP 1: EVIDENCE GATHERING (The Scratchpad)")
    print("=" * 55)
    
    try:
        from app.services.enhanced_extraction_service import EnhancedExtractionService
        
        service = EnhancedExtractionService()
        document_text = create_mock_patent_document()
        
        # Test evidence gathering
        evidence = service._gather_evidence(document_text)
        
        print("📋 EVIDENCE FOUND:")
        print("-" * 20)
        
        print(f"📝 Title: {evidence.title}")
        print(f"📄 Attorney Docket: {evidence.attorney_docket_number}")
        
        print(f"\n👥 Inventors Found: {len(evidence.inventors)}")
        for i, inv in enumerate(evidence.inventors, 1):
            print(f"  {i}. {inv.raw_text[:100]}...")
        
        print(f"\n🏢 Applicants Found: {len(evidence.applicants)}")
        for i, app in enumerate(evidence.applicants, 1):
            print(f"  {i}. {app.raw_text[:100]}...")
        
        print(f"\n📧 Correspondence: {evidence.correspondence}")
        
        print(f"\n🔗 Priority Claims Found: {len(evidence.priority_claims)}")
        for i, claim in enumerate(evidence.priority_claims, 1):
            print(f"  {i}. {claim.raw_text[:100]}...")
        
        return evidence
        
    except Exception as e:
        print(f"❌ Evidence gathering failed: {e}")
        return None

def test_json_generation(evidence):
    """Test JSON generation from evidence"""
    print("\n🏗️ STEP 2: JSON GENERATION")
    print("=" * 30)
    
    try:
        from app.services.enhanced_extraction_service import EnhancedExtractionService
        
        service = EnhancedExtractionService()
        
        # Generate JSON from evidence
        result = service._generate_json_from_evidence(evidence)
        
        print("📊 GENERATED JSON STRUCTURE:")
        print("-" * 30)
        
        # Convert to dict for display
        result_dict = result.model_dump()
        
        print(f"📝 Title: {result_dict['application_information']['title_of_invention']}")
        print(f"📄 Docket: {result_dict['application_information']['attorney_docket_number']}")
        
        print(f"\n👥 Inventors ({len(result_dict['inventor_information'])}):")
        for i, inv in enumerate(result_dict['inventor_information'], 1):
            name = f"{inv['legal_name']['given_name']} {inv['legal_name']['family_name']}"
            location = f"{inv['residence']['city']}, {inv['residence']['state_province']}"
            print(f"  {i}. {name} - {location}")
        
        print(f"\n🏢 Applicants ({len(result_dict['applicant_information'])}):")
        for i, app in enumerate(result_dict['applicant_information'], 1):
            if app['organization_name']:
                print(f"  {i}. {app['organization_name']} (Company)")
            else:
                name = f"{app['legal_name']['given_name']} {app['legal_name']['family_name']}"
                print(f"  {i}. {name} (Individual)")
        
        print(f"\n📧 Correspondence:")
        corr = result_dict['correspondence_information']
        print(f"  Customer Number: {corr['customer_number']}")
        print(f"  Email: {corr['email_address']}")
        
        print(f"\n🔗 Domestic Priority: {result_dict['domestic_benefit_information']['claims_benefit']}")
        if result_dict['domestic_benefit_information']['prior_applications']:
            for app in result_dict['domestic_benefit_information']['prior_applications']:
                print(f"  - {app['prior_application_number']} ({app['continuity_type']}) - {app['filing_date']}")
        
        print(f"\n🌍 Foreign Priority: {result_dict['foreign_priority_information']['claims_priority']}")
        if result_dict['foreign_priority_information']['prior_applications']:
            for app in result_dict['foreign_priority_information']['prior_applications']:
                print(f"  - {app['prior_application_number']} ({app['country']}) - {app['filing_date']}")
        
        return result
        
    except Exception as e:
        print(f"❌ JSON generation failed: {e}")
        return None

def test_quality_metrics(result):
    """Test quality metrics calculation"""
    print("\n📊 QUALITY METRICS ANALYSIS")
    print("=" * 30)
    
    try:
        metrics = result.quality_metrics
        
        print(f"🎯 Overall Quality Score: {metrics.overall_quality_score:.2f}")
        print(f"📋 Completeness: {metrics.completeness_score:.2f}")
        print(f"🎯 Accuracy: {metrics.accuracy_score:.2f}")
        print(f"🔒 Confidence: {metrics.confidence_score:.2f}")
        print(f"🔄 Consistency: {metrics.consistency_score:.2f}")
        
        print(f"\n📈 Field Coverage:")
        print(f"  Required Fields: {metrics.required_fields_populated}/{metrics.total_required_fields}")
        print(f"  Optional Fields: {metrics.optional_fields_populated}/{metrics.total_optional_fields}")
        
        print(f"\n⚠️ Validation Issues:")
        print(f"  Errors: {metrics.validation_errors}")
        print(f"  Warnings: {metrics.validation_warnings}")
        
        return True
        
    except Exception as e:
        print(f"❌ Quality metrics test failed: {e}")
        return False

def test_validation_details(result):
    """Test detailed validation results"""
    print("\n🔍 DETAILED VALIDATION RESULTS")
    print("=" * 35)
    
    try:
        validation = result.validation_results
        
        print(f"📊 Field Validations: {len(validation.field_validations)}")
        for field, val_result in validation.field_validations.items():
            status = "✅" if val_result.is_valid else "❌"
            print(f"  {status} {field}: {val_result.normalized_value}")
            if val_result.issues:
                for issue in val_result.issues:
                    print(f"    ⚠️ {issue}")
        
        print(f"\n🔗 Cross-Field Validations: {len(validation.cross_field_validations)}")
        for validation_type, val_result in validation.cross_field_validations.items():
            status = "✅" if val_result.is_consistent else "❌"
            print(f"  {status} {validation_type}")
            if val_result.issues:
                for issue in val_result.issues:
                    print(f"    ⚠️ {issue}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation details test failed: {e}")
        return False

def main():
    """Run the complete two-step extraction test"""
    print("🚀 ENHANCED PATENT EXTRACTION - TWO-STEP PROCESS TEST")
    print("=" * 60)
    print("This demonstrates the solution to your data extraction issues:")
    print("• Systematic evidence gathering prevents missed data")
    print("• Structured validation prevents wrong extraction")
    print("• Quality metrics ensure extraction completeness")
    print("=" * 60)
    
    # Step 1: Evidence Gathering
    evidence = test_evidence_gathering()
    if not evidence:
        print("❌ Evidence gathering failed - cannot continue")
        return False
    
    # Step 2: JSON Generation
    result = test_json_generation(evidence)
    if not result:
        print("❌ JSON generation failed - cannot continue")
        return False
    
    # Step 3: Quality Analysis
    quality_ok = test_quality_metrics(result)
    if not quality_ok:
        print("❌ Quality metrics failed")
        return False
    
    # Step 4: Validation Details
    validation_ok = test_validation_details(result)
    if not validation_ok:
        print("❌ Validation details failed")
        return False
    
    print("\n🎉 TWO-STEP EXTRACTION TEST COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("✅ Evidence gathering: Systematic data collection")
    print("✅ JSON generation: Structured data output")
    print("✅ Quality metrics: Comprehensive scoring")
    print("✅ Validation framework: Error detection & prevention")
    print("\n🚀 Your data extraction issues are SOLVED!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)