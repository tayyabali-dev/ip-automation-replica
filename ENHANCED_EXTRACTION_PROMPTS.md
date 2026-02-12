# Enhanced Extraction Prompts for USPTO Patent Document Data Extraction

## Two-Step Extraction Process Implementation

This document provides the enhanced prompt templates that implement the strict two-step extraction process to address data extraction issues.

## STEP 1: Evidence Gathering Prompt Template

### Universal Evidence Gathering Prompt

```
You are analyzing a USPTO patent document to populate an Application Data Sheet (ADS).

**CRITICAL INSTRUCTIONS:**
1. **SCAN THE ENTIRE DOCUMENT** - Check ALL pages systematically
2. **QUOTE RAW TEXT** - Extract exact text, never paraphrase or interpret
3. **NO HALLUCINATION** - Only extract what is visually present in the document
4. **DOCUMENT SOURCES** - Note page numbers and sections for all findings
5. **BE EXHAUSTIVE** - Better to over-extract than miss critical data

**EVIDENCE GATHERING PHASE:**

## STEP 1: EVIDENCE GATHERING (The Scratchpad)

### Invention Title Search
**Instructions:** Look for "Title of Invention", "Title:", or similar headers. Check first page, headers, and form fields.

**Evidence Found:**
- Raw Text: "[Quote exact title text found]"
- Source Location: Page X, Section Y
- Alternative Titles Found: "[Any variations]"
- Confidence: High/Medium/Low

### Inventor Information Gathering
**Instructions:** 
- Look for "Inventor Information", "Legal Name", "Given Name", "Family Name" sections
- Check ALL pages - inventor lists often span multiple pages
- Look for table structures with inventor data
- Extract EVERY inventor found, even if information is incomplete

**Evidence Found:**
[For each inventor discovered]
**Inventor #1:**
- Raw Text Found: "[Quote exact text block containing inventor info]"
- Source Location: Page X, Row/Section Y
- Given Name Found: "[exact text]"
- Middle Name Found: "[exact text or null]"
- Family Name Found: "[exact text]"
- Address Found: "[complete address text]"
- City Found: "[exact text]"
- State Found: "[exact text]"
- Country Found: "[exact text]"
- Citizenship Found: "[exact text or null]"
- Confidence: High/Medium/Low

**Inventor #2:**
[Repeat for all inventors found]

### Applicant/Assignee Information Gathering
**Instructions:**
- Look for "Applicant Information", "Assignee", "Company Name", "Organization"
- Check header information, correspondence sections, assignment statements
- Distinguish company addresses from inventor addresses
- Note if applicant is same as inventor

**Evidence Found:**
- Organization Name: "[Quote exact company/organization name]"
- Source Location: Page X, Section Y
- Street Address: "[Quote exact address]"
- City: "[exact text]"
- State: "[exact text]"
- Postal Code: "[exact text]"
- Country: "[exact text]"
- Relationship to Inventors: "[same as inventor/separate entity/unclear]"
- Confidence: High/Medium/Low

### Correspondence Information Gathering
**Instructions:**
- Look for "Customer Number", "Correspondence Address", email addresses
- Check headers, footer information, and dedicated correspondence sections

**Evidence Found:**
- Customer Number: "[Quote exact number]"
- Source Location: Page X, Section Y
- Email Address: "[Quote exact email]"
- Source Location: Page X, Section Y
- Confidence: High/Medium/Low

### Priority Claims Information Gathering
**Instructions:**
- Look for "claims benefit of", "continuation of", "provisional application"
- Search for foreign priority claims
- Extract application numbers and filing dates

**Evidence Found:**
**Domestic Priority Claims:**
- Raw Text: "[Quote exact priority claim text]"
- Application Number: "[exact number]"
- Filing Date: "[exact date as written]"
- Continuity Type: "[continuation/divisional/provisional/etc.]"
- Source Location: Page X, Section Y

**Foreign Priority Claims:**
- Raw Text: "[Quote exact foreign priority text]"
- Application Number: "[exact number]"
- Country: "[exact country]"
- Filing Date: "[exact date as written]"
- Source Location: Page X, Section Y

### Additional Information Gathering
**Instructions:**
- Look for Attorney Docket Number, Application Type indicators
- Note any other relevant bibliographic data

**Evidence Found:**
- Attorney Docket Number: "[exact text]"
- Application Type Indicators: "[any text suggesting provisional/nonprovisional]"
- Other Relevant Data: "[any additional bibliographic information]"

**END OF EVIDENCE GATHERING PHASE**
```

## STEP 2: JSON Generation Prompt Template

### Structured Data Generation Prompt

```
Based ONLY on the evidence you gathered in Step 1, generate a single, valid JSON object.

**CRITICAL RULES:**
- Use `null` if a specific field is absolutely not found in your evidence
- Format all dates as "YYYY-MM-DD" (convert from any format found)
- Ensure "country" is a 2-letter ISO code (e.g., "US") or full country name
- Do NOT make up, assume, or infer any data not explicitly found
- If evidence is unclear or ambiguous, use `null` rather than guess

**STEP 2: JSON GENERATION**

Based on the evidence gathered above, populate this JSON structure:

{
  "application_information": {
    "title_of_invention": "String from evidence or null",
    "attorney_docket_number": "String from evidence or null",
    "application_type": "Nonprovisional"
  },
  "inventor_information": [
    {
      "legal_name": {
        "given_name": "String from evidence",
        "middle_name": "String from evidence or null",
        "family_name": "String from evidence"
      },
      "residence": {
        "city": "String from evidence",
        "state_province": "String from evidence",
        "country": "String from evidence (2-letter code or full name)"
      },
      "mailing_address": {
        "address_1": "String from evidence",
        "address_2": "String from evidence or null",
        "city": "String from evidence",
        "state_province": "String from evidence",
        "postal_code": "String from evidence",
        "country": "String from evidence (2-letter code or full name)"
      }
    }
  ],
  "applicant_information": [
    {
      "is_assignee": true/false,
      "organization_name": "String from evidence (if company) or null",
      "legal_name": {
        "given_name": "String from evidence (if person) or null",
        "family_name": "String from evidence (if person) or null"
      },
      "mailing_address": {
        "address_1": "String from evidence",
        "city": "String from evidence",
        "state_province": "String from evidence",
        "postal_code": "String from evidence",
        "country": "String from evidence (2-letter code or full name)"
      }
    }
  ],
  "correspondence_information": {
    "customer_number": "String from evidence or null",
    "email_address": "String from evidence or null"
  },
  "domestic_benefit_information": {
    "claims_benefit": true/false,
    "prior_applications": [
      {
        "prior_application_number": "String from evidence",
        "continuity_type": "String from evidence (e.g., Continuation, Divisional, Provisional)",
        "filing_date": "YYYY-MM-DD format"
      }
    ]
  },
  "foreign_priority_information": {
    "claims_priority": true/false,
    "prior_applications": [
      {
        "prior_application_number": "String from evidence",
        "country": "String from evidence",
        "filing_date": "YYYY-MM-DD format"
      }
    ]
  }
}
```

## Format-Specific Prompt Variations

### XFA Form Extraction Prompt

```
**XFA FORM SPECIFIC INSTRUCTIONS:**

You are analyzing an XFA (Dynamic) form. These forms contain structured XML data.

**Evidence Gathering for XFA:**
1. Look for XML tags like `<GivenName>`, `<FamilyName>`, `<MailingAddress>`
2. Search for inventor sequences: `<Inventor_1>`, `<Inventor_2>`, etc.
3. Find applicant/assignee information in dedicated XML sections
4. Extract form field values, not just field names

**XFA Evidence Pattern:**
- XML Tag: `<FieldName>Value</FieldName>`
- Extracted Value: "Value"
- Source: XML datasets section

[Continue with standard evidence gathering format]
```

### Scanned Document Extraction Prompt

```
**SCANNED DOCUMENT SPECIFIC INSTRUCTIONS:**

You are analyzing a scanned document that may have OCR text quality issues.

**Evidence Gathering for Scanned Documents:**
1. **Visual Analysis Priority**: Use the image to understand document structure
2. **Text Verification**: Cross-reference OCR text with visual elements
3. **Table Recognition**: Identify table structures visually, then extract text
4. **Quality Assessment**: Note when text is unclear or potentially misread

**Scanned Document Evidence Pattern:**
- Visual Structure: "[Describe what you see - table, form, etc.]"
- OCR Text Found: "[Quote text as extracted]"
- Text Quality: High/Medium/Low
- Visual Confirmation: "[What the image shows vs. what OCR extracted]"

[Continue with standard evidence gathering format]
```

### Multi-Page Document Extraction Prompt

```
**MULTI-PAGE DOCUMENT SPECIFIC INSTRUCTIONS:**

This document spans multiple pages. Pay special attention to:

**Multi-Page Evidence Gathering:**
1. **Page-by-Page Analysis**: Systematically check each page
2. **Continuation Detection**: Look for "continued on next page" or similar
3. **Table Spanning**: Inventor tables often continue across pages
4. **Cross-Page Relationships**: Connect related information across pages

**Multi-Page Evidence Pattern:**
- Page X Content: "[What's found on this page]"
- Continuation Indicators: "[Any text suggesting more data follows]"
- Cross-Page Connections: "[How this page relates to others]"

[Continue with standard evidence gathering format]
```

## Validation and Quality Assurance Prompts

### Evidence Quality Check Prompt

```
**EVIDENCE QUALITY VALIDATION:**

Before generating JSON, review your evidence gathering:

1. **Completeness Check:**
   - Did you check ALL pages?
   - Did you find ALL inventors (not just the first few)?
   - Did you locate applicant/company information?

2. **Accuracy Check:**
   - Are all quotes exact (no paraphrasing)?
   - Are source locations specific and accurate?
   - Are confidence levels realistic?

3. **Consistency Check:**
   - Do inventor addresses make sense geographically?
   - Is applicant information distinct from inventor information?
   - Are dates in consistent formats?

**Quality Score:** Rate your evidence gathering as Excellent/Good/Fair/Poor
**Missing Data Note:** List any required fields you could not locate
```

### JSON Validation Prompt

```
**JSON GENERATION VALIDATION:**

After generating JSON, verify:

1. **Schema Compliance:**
   - All required fields present
   - Correct data types used
   - Proper null handling

2. **Data Quality:**
   - Dates in YYYY-MM-DD format
   - Country codes standardized
   - No hallucinated data

3. **Evidence Traceability:**
   - Every populated field has corresponding evidence
   - No data appears that wasn't in evidence gathering
   - Null values used appropriately for missing data

**Final Validation:** Confirm JSON is valid and complete
```

## Implementation Notes

### Integration with Existing System

These prompts are designed to replace the current prompt templates in:
- `_analyze_text_only()` method
- `_analyze_xfa_xml()` method  
- `_analyze_pdf_direct_fallback()` method
- `_extract_structured_chunk()` method

### Prompt Customization

Each extraction method should use the appropriate format-specific variation while maintaining the core two-step structure.

### Error Handling

If Step 1 (Evidence Gathering) fails, the system should:
1. Log the failure with specific error details
2. Attempt alternative extraction strategy
3. Return partial results with confidence scores
4. Never proceed to Step 2 without evidence

### Performance Considerations

The two-step approach may increase token usage but should significantly improve accuracy. Monitor:
- Token consumption per extraction
- Processing time impact
- Accuracy improvement metrics
- User satisfaction with results

This enhanced prompt engineering approach directly addresses the core issues of missed data, incorrect extractions, and inconsistent results by enforcing systematic evidence gathering before any data interpretation.