#!/usr/bin/env python3
"""
Test script to directly test the data conversion from saved format to EnhancedExtractionResult.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import json
from app.models.enhanced_extraction import EnhancedExtractionResult, ExtractionMethod, DataCompleteness

def test_data_conversion():
    """Test converting saved data to EnhancedExtractionResult."""
    
    print("🔍 Testing Data Conversion")
    print("=" * 40)
    
    # Load the clean data
    try:
        with open('clean_app_data_20260206_023028.json', 'r') as f:
            app_data = json.load(f)
        print("✅ Loaded saved application data")
    except FileNotFoundError:
        print("❌ Clean data file not found. Run debug script first.")
        return
    
    print(f"\n📋 Data keys: {list(app_data.keys())}")
    
    # Test direct conversion first
    print("\n1. Testing direct conversion...")
    try:
        result = EnhancedExtractionResult(**app_data)
        print("✅ Direct conversion successful!")
        return result
    except Exception as e:
        print(f"❌ Direct conversion failed: {type(e).__name__}: {e}")
    
    # Test with enum conversion
    print("\n2. Testing with enum conversion...")
    try:
        def convert_enums(data):
            """Convert string enum values back to enum objects"""
            if isinstance(data, dict):
                result = {}
                for key, value in data.items():
                    if key == 'extraction_method' and isinstance(value, str):
                        try:
                            result[key] = ExtractionMethod(value)
                        except ValueError:
                            result[key] = value
                    elif key == 'completeness' and isinstance(value, str):
                        try:
                            result[key] = DataCompleteness(value)
                        except ValueError:
                            result[key] = value
                    else:
                        result[key] = convert_enums(value)
                return result
            elif isinstance(data, list):
                return [convert_enums(item) for item in data]
            else:
                return data
        
        converted_data = convert_enums(app_data)
        result = EnhancedExtractionResult(**converted_data)
        print("✅ Enum conversion successful!")
        return result
    except Exception as e:
        print(f"❌ Enum conversion failed: {type(e).__name__}: {e}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
    
    # Test field by field to identify the problematic field
    print("\n3. Testing field by field...")
    required_fields = {
        'quality_metrics': app_data.get('quality_metrics'),
        'extraction_metadata': app_data.get('extraction_metadata'),
        'inventors': app_data.get('inventors', []),
        'applicants': app_data.get('applicants', []),
        'field_validations': app_data.get('field_validations', []),
        'cross_field_validations': app_data.get('cross_field_validations', []),
        'domestic_priority_claims': app_data.get('domestic_priority_claims', []),
        'foreign_priority_claims': app_data.get('foreign_priority_claims', []),
        'extraction_warnings': app_data.get('extraction_warnings', []),
        'recommendations': app_data.get('recommendations', [])
    }
    
    for field_name, field_value in required_fields.items():
        try:
            test_data = {field_name: field_value}
            # Add minimal required fields
            if field_name != 'quality_metrics':
                test_data['quality_metrics'] = app_data['quality_metrics']
            if field_name != 'extraction_metadata':
                test_data['extraction_metadata'] = app_data['extraction_metadata']
            if field_name != 'inventors':
                test_data['inventors'] = app_data['inventors']
            
            EnhancedExtractionResult(**test_data)
            print(f"✅ {field_name}: OK")
        except Exception as e:
            print(f"❌ {field_name}: {type(e).__name__}: {e}")
    
    return None

if __name__ == "__main__":
    result = test_data_conversion()
    if result:
        print(f"\n🎉 Conversion successful! Application: {result.title or 'Untitled'}")
    else:
        print(f"\n💥 Conversion failed. Check the errors above.")