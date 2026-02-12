#!/usr/bin/env node
/**
 * Test script to verify frontend error message parsing
 * This simulates how the frontend parses the backend error response
 */

// Simulate the backend response that contains the inventor count error
const mockBackendResponse = {
    "success": false,
    "pdf_generated": false,
    "pdf_size_bytes": null,
    "filename": null,
    "validation_report": {
        "is_valid": false,
        "summary": {
            "total_fields_checked": 0,
            "errors_count": 0,
            "warnings_count": 0,
            "info_count": 0,
            "auto_corrections_count": 0,
            "validation_score": 0.0,
            "categories_checked": []
        },
        "mismatches": [],
        "processing_time_ms": 602,
        "checked_at": "2026-02-03T15:53:57.985552",
        "xfa_xml_size": 0,
        "source_metadata_hash": null
    },
    "generation_blocked": true,
    "blocking_errors": [],
    "message": "ADS generation failed: 400: {'error': 'inventor_count_changed', 'message': 'Cannot generate ADS: Inventor count has changed from 2 to 3. Adding or removing inventors requires re-extraction from the source document.', 'original_count': 2, 'submitted_count': 3}"
};

// Simulate the frontend error parsing logic
function parseErrorMessage(errorData) {
    if (errorData.success === false && errorData.generation_blocked) {
        const message = errorData.message || '';
        
        // Check for inventor count validation error
        if (message.includes('inventor_count_changed') || message.includes('Inventor count has changed')) {
            // Extract the actual error message from the nested structure
            let cleanMessage = 'Inventor count has changed. Adding or removing inventors requires re-extraction.';
            
            if (message.includes('ADS generation failed: 400:')) {
                try {
                    // Extract the JSON part after "ADS generation failed: 400: "
                    const errorPart = message.split('ADS generation failed: 400: ')[1];
                    // Replace single quotes with double quotes to make it valid JSON
                    const jsonString = errorPart.replace(/'/g, '"');
                    const errorObj = JSON.parse(jsonString);
                    cleanMessage = errorObj.message || cleanMessage;
                } catch (parseError) {
                    console.warn('Could not parse error message:', parseError);
                    // Fallback: try to extract from the raw message
                    if (message.includes('Inventor count has changed from')) {
                        const match = message.match(/Inventor count has changed from (\d+) to (\d+)/);
                        if (match) {
                            const [, originalCount, currentCount] = match;
                            cleanMessage = `Cannot generate ADS: Inventor count has changed from ${originalCount} to ${currentCount}. Adding or removing inventors requires re-extraction.`;
                        }
                    }
                }
            }
            
            return {
                type: 'critical',
                title: 'Cannot Generate ADS',
                message: cleanMessage,
            };
        } else {
            return {
                type: 'error',
                title: 'Generation Failed',
                message: errorData.message || 'Failed to generate ADS PDF.',
            };
        }
    } else {
        return {
            type: 'error',
            title: 'Generation Failed',
            message: 'An unexpected error occurred during PDF generation.',
        };
    }
}

// Test the parsing
console.log('🧪 Testing Frontend Error Message Parsing');
console.log('=' .repeat(50));

console.log('\n📥 Backend Response:');
console.log('Message:', mockBackendResponse.message);

console.log('\n🔄 Frontend Parsing Result:');
const result = parseErrorMessage(mockBackendResponse);

console.log('Type:', result.type);
console.log('Title:', result.title);
console.log('Message:', result.message);

console.log('\n✅ Expected Message:');
console.log('Cannot generate ADS: Inventor count has changed from 2 to 3. Adding or removing inventors requires re-extraction from the source document.');

console.log('\n🎯 Test Result:');
const expectedMessage = 'Cannot generate ADS: Inventor count has changed from 2 to 3. Adding or removing inventors requires re-extraction from the source document.';
if (result.message === expectedMessage) {
    console.log('✅ SUCCESS: Message parsing works correctly!');
} else {
    console.log('❌ FAILED: Message parsing needs adjustment');
    console.log('Expected:', expectedMessage);
    console.log('Got:     ', result.message);
}

console.log('\n' + '=' .repeat(50));