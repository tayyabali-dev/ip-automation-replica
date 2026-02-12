# Quality Assurance Prompt Integration Plan

## Overview
This document outlines how to integrate the Data Quality Assurance prompt template into the enhanced extraction system to provide automated error correction capabilities.

## Integration Architecture

### 1. Enhanced Extraction Service Integration

#### Add QA Prompt Class
Add the following class to `backend/app/services/enhanced_extraction_service.py`:

```python
class QualityAssurancePrompts:
    """
    Prompts for quality assurance and error correction
    """
    
    def create_qa_correction_prompt(
        self,
        document_text: str,
        invalid_json_output: str,
        error_message: str
    ) -> str:
        """
        Create QA correction prompt for fixing extraction errors
        """
        return f"""
**Role:**
You are a Data Quality Assurance Expert.

**Task:**
You previously attempted to extract patent data into JSON, but the result failed automated validation. You must fix the JSON based on the specific error provided.

**Context:**
1. **Original Text:**
{document_text}

2. **The Invalid/Incomplete JSON you generated:**
{invalid_json_output}

3. **The Validation Error/Missing Data Issue:**
{error_message}

**Instructions:**
1. Analyze the Error Message.
2. Re-read the Original Text specifically looking for the missing or incorrect data.
3. Fix the JSON.
   - If the error says data is missing, SEARCH HARDER in the text to find it.
   - If the error is about format (like dates), correct the format.
4. Output ONLY the corrected, complete, valid JSON object inside a markdown code block. Do not provide explanations.

**Corrected JSON:**
"""
```

#### Add QA Correction Method
Add this method to the `EnhancedExtractionService` class:

```python
async def quality_assurance_correction(
    self,
    document_text: str,
    invalid_json: Dict[str, Any],
    error_message: str
) -> Dict[str, Any]:
    """
    Apply quality assurance correction using the QA prompt
    """
    try:
        qa_prompt = self.qa_prompts.create_qa_correction_prompt(
            document_text=document_text,
            invalid_json_output=json.dumps(invalid_json, indent=2),
            error_message=error_message
        )
        
        corrected_response = await self.llm_service.generate_structured_content(
            prompt=qa_prompt,
            retries=2
        )
        
        return corrected_response
        
    except Exception as e:
        logger.error(f"QA correction failed: {e}")
        raise DataProcessingError(f"Quality assurance correction failed: {str(e)}")
```

#### Update Constructor
Update the `EnhancedExtractionService.__init__` method:

```python
def __init__(self, llm_service: LLMService = None):
    self.llm_service = llm_service or LLMService()
    self.evidence_gathering_prompts = EvidenceGatheringPrompts()
    self.json_generation_prompts = JSONGenerationPrompts()
    self.qa_prompts = QualityAssurancePrompts()  # Add this line
```

### 2. Validation Service Integration

#### Add QA Trigger Method
Add this method to `backend/app/services/validation_service.py`:

```python
def should_trigger_qa_correction(
    self,
    validation_results: ValidationResults,
    quality_metrics: QualityMetrics
) -> Tuple[bool, str]:
    """
    Determine if QA correction should be triggered and return error message
    """
    critical_errors = []
    
    # Check for missing required fields
    if quality_metrics.required_fields_populated < quality_metrics.total_required_fields:
        missing_count = quality_metrics.total_required_fields - quality_metrics.required_fields_populated
        critical_errors.append(f"{missing_count} required fields are missing")
    
    # Check for validation errors
    if quality_metrics.validation_errors > 0:
        critical_errors.append(f"{quality_metrics.validation_errors} validation errors found")
    
    # Check for low quality scores
    if quality_metrics.overall_quality_score < 0.7:
        critical_errors.append(f"Overall quality score too low: {quality_metrics.overall_quality_score:.2f}")
    
    # Check specific field validation failures
    for field, result in validation_results.field_validations.items():
        if not result.is_valid and field in ['title', 'inventors', 'applicants']:
            critical_errors.append(f"Critical field '{field}' validation failed: {', '.join(result.issues)}")
    
    if critical_errors:
        error_message = "; ".join(critical_errors)
        return True, error_message
    
    return False, ""
```

### 3. Enhanced Extraction Pipeline Update

#### Update Main Extraction Method
Modify the `extract_with_two_step_process` method to include QA correction:

```python
async def extract_with_two_step_process(
    self,
    file_path: str,
    file_content: Optional[bytes] = None,
    document_type: str = "unknown",
    progress_callback: Optional[callable] = None
) -> EnhancedExtractionResult:
    """
    Main entry point for two-step extraction process with QA correction
    """
    start_time = datetime.utcnow()
    
    try:
        # Steps 1-3: Evidence gathering, JSON generation, validation (existing code)
        # ... existing implementation ...
        
        # Step 4: Quality Assurance Check
        validation_service = ValidationService()
        should_correct, error_message = validation_service.should_trigger_qa_correction(
            validated_result.validation_results,
            validated_result.quality_metrics
        )
        
        if should_correct:
            if progress_callback:
                await progress_callback(95, "Applying quality assurance correction...")
            
            # Extract original document text for QA
            original_text = await self._get_document_text(file_path, file_content)
            
            # Apply QA correction
            corrected_json = await self.quality_assurance_correction(
                document_text=original_text,
                invalid_json=validated_result.model_dump(),
                error_message=error_message
            )
            
            # Re-process corrected JSON
            corrected_result = await self._convert_to_extraction_result(
                corrected_json, validated_result.document_evidence
            )
            
            # Re-validate corrected result
            final_result = await self._validate_and_enhance_result(
                corrected_result, validated_result.document_evidence
            )
            
            # Mark as QA corrected
            final_result.extraction_metadata.qa_corrected = True
            final_result.extraction_metadata.original_error = error_message
            
            validated_result = final_result
        
        # Final processing
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        validated_result.extraction_metadata.processing_time = processing_time
        
        if progress_callback:
            await progress_callback(100, "Extraction completed successfully")
        
        return validated_result
        
    except Exception as e:
        logger.error(f"Enhanced extraction failed: {e}", exc_info=True)
        raise DataProcessingError(f"Enhanced extraction failed: {str(e)}")
```

### 4. Model Updates

#### Update ExtractionMetadata
Add QA correction tracking to `backend/app/models/enhanced_extraction.py`:

```python
class ExtractionMetadata(BaseModel):
    extraction_method: ExtractionMethod
    document_type: str
    processing_time: float = 0.0
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    qa_corrected: bool = False  # Add this field
    original_error: Optional[str] = None  # Add this field
    correction_attempts: int = 0  # Add this field
```

### 5. Error Handling Enhancement

#### Add QA-Specific Errors
Add to `backend/app/models/enhanced_extraction.py`:

```python
class QualityAssuranceError(ExtractionError):
    """Raised when quality assurance correction fails"""
    pass

class MaxCorrectionAttemptsError(ExtractionError):
    """Raised when maximum QA correction attempts exceeded"""
    pass
```

### 6. Testing Integration

#### Add QA Tests
Create tests in `backend/app/tests/test_enhanced_extraction.py`:

```python
async def test_qa_correction_missing_inventor():
    """Test QA correction for missing inventor data"""
    # Test implementation

async def test_qa_correction_invalid_date():
    """Test QA correction for invalid date format"""
    # Test implementation

async def test_qa_correction_max_attempts():
    """Test QA correction maximum attempts limit"""
    # Test implementation
```

## Implementation Steps

1. **Phase 1**: Add QualityAssurancePrompts class to enhanced_extraction_service.py
2. **Phase 2**: Add QA correction method to EnhancedExtractionService
3. **Phase 3**: Update ValidationService with QA trigger logic
4. **Phase 4**: Integrate QA correction into main extraction pipeline
5. **Phase 5**: Update data models with QA tracking fields
6. **Phase 6**: Add comprehensive QA testing
7. **Phase 7**: Update documentation and examples

## Benefits

1. **Automated Error Recovery**: System can fix common extraction errors automatically
2. **Improved Accuracy**: Targeted correction based on specific validation failures
3. **Reduced Manual Intervention**: Fewer cases requiring human review
4. **Quality Assurance**: Systematic approach to ensuring data quality
5. **Audit Trail**: Complete tracking of corrections and attempts

## Configuration Options

```python
class QAConfig:
    max_correction_attempts: int = 2
    quality_threshold: float = 0.7
    enable_qa_correction: bool = True
    critical_fields: List[str] = ["title", "inventors", "applicants"]
```

This integration plan ensures the QA prompt template becomes a seamless part of the enhanced extraction system, providing automated error correction and improved data quality.