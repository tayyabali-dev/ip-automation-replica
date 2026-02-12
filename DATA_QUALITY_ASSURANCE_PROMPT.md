# Data Quality Assurance Prompt Template

## Purpose
This prompt template is used when the initial extraction fails validation and needs correction. It provides a systematic approach to fix JSON output based on specific validation errors.

## Prompt Template

```
**Role:**
You are a Data Quality Assurance Expert.

**Task:**
You previously attempted to extract patent data into JSON, but the result failed automated validation. You must fix the JSON based on the specific error provided.

**Context:**
1. **Original Text:**
{{document_text}}

2. **The Invalid/Incomplete JSON you generated:**
{{invalid_json_output}}

3. **The Validation Error/Missing Data Issue:**
{{error_message}}
*(System Note: Pass the specific error here, e.g., "Inventor list is empty" or "Field 'title_of_invention' is missing")*

**Instructions:**
1. Analyze the Error Message.
2. Re-read the Original Text specifically looking for the missing or incorrect data.
3. Fix the JSON.
   - If the error says data is missing, SEARCH HARDER in the text to find it.
   - If the error is about format (like dates), correct the format.
4. Output ONLY the corrected, complete, valid JSON object inside a markdown code block. Do not provide explanations.

**Corrected JSON:**
```

## Integration Points

### 1. Enhanced Extraction Service
This prompt should be used in the `EnhancedExtractionService` when:
- Initial extraction fails validation
- Quality metrics fall below threshold
- Specific field validation errors occur

### 2. Validation Service Integration
The `ValidationService` should trigger this prompt when:
- Required fields are missing
- Field format validation fails
- Cross-field consistency checks fail

### 3. Error Handling Workflow
```
Initial Extraction → Validation → If Failed → QA Prompt → Re-validation → Success/Escalation
```

## Common Error Types to Handle

### Missing Data Errors
- "Inventor list is empty"
- "Field 'title_of_invention' is missing"
- "Applicant information not found"
- "Correspondence details missing"

### Format Errors
- "Date format invalid - expected YYYY-MM-DD"
- "Country code invalid - expected 2-letter ISO code"
- "Email format invalid"
- "State code not recognized"

### Consistency Errors
- "Inventor name mismatch between given_name/family_name and full_name"
- "Address inconsistency between residence and mailing address"
- "Applicant address doesn't match any inventor address"

## Implementation Example

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
```

## Benefits

1. **Targeted Error Correction**: Focuses specifically on the identified issue
2. **Systematic Approach**: Follows a structured process for error analysis
3. **Improved Accuracy**: Forces re-examination of source text for missing data
4. **Format Standardization**: Ensures consistent output format
5. **Automated Recovery**: Enables automatic correction without manual intervention

## Usage in Enhanced Extraction Pipeline

This QA prompt is the final safety net in the enhanced extraction system:

1. **Step 1**: Evidence Gathering (prevents most errors)
2. **Step 2**: JSON Generation (structured output)
3. **Step 3**: Validation (identifies remaining issues)
4. **Step 4**: QA Correction (fixes identified issues)
5. **Step 5**: Final Validation (confirms correction)

This ensures maximum data extraction accuracy and completeness.