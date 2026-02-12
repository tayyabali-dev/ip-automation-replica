"""
File validation utilities for patent application document uploads.

Handles edge cases for PDF and DOCX file uploads:
- P0: Encrypted PDFs, corrupted/invalid files, empty/blank documents
- P1: Scanned image-only PDFs, oversized documents, Unicode/special characters

Drop this module into: app/services/file_validators.py
"""

import io
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


# ============================================================================
# MAGIC BYTES — File Format Validation
# ============================================================================

# File signatures (magic bytes)
MAGIC_BYTES = {
    "pdf": {
        "signature": b"%PDF",
        "offset": 0,
        "mime": "application/pdf",
    },
    "docx": {
        # DOCX is a ZIP archive — starts with PK\x03\x04
        "signature": b"PK\x03\x04",
        "offset": 0,
        "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    },
}

ALLOWED_EXTENSIONS = {"pdf", "docx"}


class FileValidationError(Exception):
    """Raised when file validation fails. Contains a user-friendly message."""

    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


# ============================================================================
# P0: Core Validation Functions
# ============================================================================


def validate_file_integrity(
    file_content: bytes,
    filename: str,
) -> dict:
    """
    Master validation function — runs all P0 checks in sequence.
    Call this at the upload endpoint BEFORE storing in GCS.

    Returns:
        dict with keys:
            - valid (bool)
            - file_type (str): "pdf" or "docx"
            - error (str | None): user-facing error message
            - error_code (str | None): machine-readable error code
            - warnings (list[str]): non-fatal warnings (e.g. low text content)

    Raises:
        FileValidationError if file is fundamentally invalid.
    """
    result = {
        "valid": True,
        "file_type": None,
        "error": None,
        "error_code": None,
        "warnings": [],
    }

    # --- Check 1: Not empty ---
    if not file_content or len(file_content) == 0:
        raise FileValidationError(
            "The uploaded file is empty (0 bytes).",
            error_code="EMPTY_FILE",
        )

    # --- Check 2: File size (reject > 50 MB) ---
    max_size_mb = 50
    size_mb = len(file_content) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise FileValidationError(
            f"File is too large ({size_mb:.1f} MB). Maximum allowed size is {max_size_mb} MB.",
            error_code="FILE_TOO_LARGE",
        )

    # --- Check 3: Detect file type from magic bytes ---
    file_type = _detect_file_type(file_content)
    ext = _get_extension(filename)

    if file_type is None:
        raise FileValidationError(
            f"The uploaded file does not appear to be a valid PDF or DOCX. "
            f"The file's internal structure does not match any supported format.",
            error_code="INVALID_FORMAT",
        )

    # --- Check 4: Extension vs content mismatch ---
    if ext and ext != file_type:
        raise FileValidationError(
            f"File extension '.{ext}' does not match the actual file content "
            f"(detected as {file_type.upper()}). Please upload the correct file.",
            error_code="EXTENSION_MISMATCH",
        )

    result["file_type"] = file_type

    # --- Check 5: Type-specific validation ---
    if file_type == "pdf":
        _validate_pdf(file_content, result)
    elif file_type == "docx":
        _validate_docx(file_content, result)

    return result


def _detect_file_type(content: bytes) -> Optional[str]:
    """Detect file type from magic bytes."""
    for ftype, info in MAGIC_BYTES.items():
        offset = info["offset"]
        sig = info["signature"]
        if content[offset : offset + len(sig)] == sig:
            return ftype
    return None


def _get_extension(filename: str) -> Optional[str]:
    """Extract lowercase extension from filename."""
    if not filename or "." not in filename:
        return None
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext if ext in ALLOWED_EXTENSIONS else None


# ============================================================================
# P0: PDF-Specific Validation
# ============================================================================


def _validate_pdf(content: bytes, result: dict) -> None:
    """Run PDF-specific checks: encryption, corruption, blank pages."""
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError

    try:
        reader = PdfReader(io.BytesIO(content))
    except PdfReadError as e:
        error_msg = str(e).lower()
        if "encrypt" in error_msg or "password" in error_msg:
            raise FileValidationError(
                "This PDF is password-protected or encrypted. "
                "Please remove the password protection and upload again.",
                error_code="PDF_ENCRYPTED",
            )
        raise FileValidationError(
            "This PDF file appears to be corrupted or malformed and cannot be read. "
            "Please try re-saving or re-downloading the file.",
            error_code="PDF_CORRUPTED",
        )
    except Exception as e:
        logger.error(f"Unexpected error reading PDF: {e}")
        raise FileValidationError(
            "An unexpected error occurred while reading this PDF. "
            "The file may be corrupted.",
            error_code="PDF_READ_ERROR",
        )

    # Check if PDF is encrypted (even if PdfReader didn't throw)
    if reader.is_encrypted:
        # Try to decrypt with empty password (some PDFs have owner-only encryption)
        try:
            decrypt_result = reader.decrypt("")
            if decrypt_result == 0:
                raise FileValidationError(
                    "This PDF is password-protected. "
                    "Please remove the password and upload again.",
                    error_code="PDF_ENCRYPTED",
                )
            # decrypt_result == 1 or 2 means decryption succeeded with empty password
            # This is "owner password only" — we can proceed
            result["warnings"].append(
                "PDF has owner-level encryption (no user password). Proceeding."
            )
        except FileValidationError:
            raise
        except Exception:
            raise FileValidationError(
                "This PDF is encrypted and cannot be processed. "
                "Please remove the encryption and upload again.",
                error_code="PDF_ENCRYPTED",
            )

    # Check page count
    num_pages = len(reader.pages)
    if num_pages == 0:
        raise FileValidationError(
            "This PDF has no pages.",
            error_code="PDF_EMPTY",
        )

    # Check for blank content (all pages have no extractable text)
    total_text = ""
    for page in reader.pages:
        text = page.extract_text() or ""
        total_text += text.strip()
        # Short-circuit: if we find substantial text, no need to check all pages
        if len(total_text) > 50:
            break

    if len(total_text) < 10:
        # This is a WARNING, not an error — the PDF might be scanned/image-only
        # and the vision fallback path can handle it
        result["warnings"].append(
            "PDF contains very little or no extractable text. "
            "This may be a scanned document — image-based extraction will be attempted."
        )

    result["page_count"] = num_pages


def validate_pdf_not_encrypted(content: bytes) -> tuple[bool, str]:
    """
    Standalone check for PDF encryption.
    Returns (is_ok, error_message).
    Use this if you want a quick check without full validation.
    """
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError

    try:
        reader = PdfReader(io.BytesIO(content))
        if reader.is_encrypted:
            try:
                result = reader.decrypt("")
                if result == 0:
                    return False, "PDF is password-protected."
            except Exception:
                return False, "PDF is encrypted and cannot be processed."
        return True, ""
    except PdfReadError as e:
        if "encrypt" in str(e).lower():
            return False, "PDF is encrypted."
        return False, f"PDF is corrupted: {e}"
    except Exception as e:
        return False, f"Cannot read PDF: {e}"


# ============================================================================
# P0: DOCX-Specific Validation
# ============================================================================


def _validate_docx(content: bytes, result: dict) -> None:
    """Run DOCX-specific checks: valid ZIP, contains document.xml, not empty."""
    import zipfile

    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            names = zf.namelist()

            # Must contain word/document.xml (core requirement for DOCX)
            if "word/document.xml" not in names:
                raise FileValidationError(
                    "This file has a .docx extension but does not contain "
                    "the expected document structure. It may be a different "
                    "type of ZIP archive (e.g., .xlsx, .pptx, or a regular .zip).",
                    error_code="DOCX_INVALID_STRUCTURE",
                )

            # Try to read document.xml to verify it's not corrupted
            try:
                doc_xml = zf.read("word/document.xml")
                if len(doc_xml) < 50:
                    result["warnings"].append("DOCX document.xml is unusually small.")
            except Exception:
                raise FileValidationError(
                    "The DOCX file's internal structure is corrupted.",
                    error_code="DOCX_CORRUPTED",
                )

    except zipfile.BadZipFile:
        raise FileValidationError(
            "This file appears to be corrupted — it has a DOCX/ZIP header "
            "but cannot be unzipped. Please try re-saving the document.",
            error_code="DOCX_CORRUPTED",
        )
    except FileValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error validating DOCX: {e}")
        raise FileValidationError(
            "An unexpected error occurred while validating this DOCX file.",
            error_code="DOCX_READ_ERROR",
        )


# ============================================================================
# P1: Page Truncation for Oversized Documents
# ============================================================================


def truncate_pdf_pages(
    content: bytes,
    max_pages: int = 10,
) -> tuple[bytes, int, bool]:
    """
    If a PDF exceeds max_pages, return a truncated version.
    This prevents sending 50+ page specifications to the LLM.

    Returns:
        (truncated_content, original_page_count, was_truncated)
    """
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(io.BytesIO(content))
    total_pages = len(reader.pages)

    if total_pages <= max_pages:
        return content, total_pages, False

    logger.info(
        f"Truncating PDF from {total_pages} pages to {max_pages} pages for LLM analysis"
    )

    writer = PdfWriter()
    for i in range(min(max_pages, total_pages)):
        writer.add_page(reader.pages[i])

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue(), total_pages, True


# ============================================================================
# P1: Text Content Assessment (Scanned PDF Detection)
# ============================================================================


def assess_pdf_text_content(content: bytes) -> dict:
    """
    Analyze how much extractable text a PDF contains.
    Helps decide whether to use text extraction or vision/OCR fallback.

    Returns:
        dict with:
            - total_chars (int): total extracted character count
            - has_text (bool): whether meaningful text was found
            - is_likely_scanned (bool): probably a scanned document
            - text_per_page (float): average chars per page
            - recommendation (str): "text", "vision", or "ocr"
    """
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(content))
    total_chars = 0
    pages_with_text = 0
    num_pages = len(reader.pages)

    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        char_count = len(text)
        total_chars += char_count
        if char_count > 20:  # More than trivial content
            pages_with_text += 1

    text_per_page = total_chars / max(num_pages, 1)

    # Heuristics for scanned document detection
    is_likely_scanned = (
        total_chars < 50  # Almost no text extracted
        or (text_per_page < 30 and pages_with_text < num_pages * 0.3)
    )

    # Decide extraction strategy
    if total_chars > 200 and text_per_page > 100:
        recommendation = "text"  # Good text content, use text extraction
    elif is_likely_scanned:
        recommendation = "vision"  # Scanned doc, use Gemini vision
    else:
        recommendation = "text"  # Some text, try text first

    return {
        "total_chars": total_chars,
        "has_text": total_chars > 50,
        "is_likely_scanned": is_likely_scanned,
        "text_per_page": text_per_page,
        "pages_with_text": pages_with_text,
        "total_pages": num_pages,
        "recommendation": recommendation,
    }


# ============================================================================
# P1: XML-Safe Text Sanitization (Unicode & Special Characters)
# ============================================================================


def sanitize_for_xml(text: Optional[str]) -> str:
    """
    Sanitize text for safe inclusion in XFA/XML output.
    Handles:
    - XML special characters (&, <, >, ", ')
    - Control characters that break XML parsers
    - Ensures Unicode names (diacritics, CJK) survive round-trip

    Use this in ads_xfa_builder.py wherever user-provided text
    is inserted into XML elements.
    """
    if not text:
        return ""

    # Remove XML-illegal control characters (keep tab, newline, carriage return)
    # XML 1.0 allows: #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD]
    cleaned = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]",
        "",
        text,
    )

    # Escape XML special characters
    # Order matters: & must be first
    cleaned = cleaned.replace("&", "&amp;")
    cleaned = cleaned.replace("<", "&lt;")
    cleaned = cleaned.replace(">", "&gt;")
    cleaned = cleaned.replace('"', "&quot;")
    cleaned = cleaned.replace("'", "&apos;")

    return cleaned


def sanitize_inventor_name(name: Optional[str]) -> str:
    """
    Normalize inventor/applicant names.
    Handles common LLM extraction artifacts:
    - Extra whitespace
    - Accidental numbering ("1. John Doe")
    - Stray quotes or brackets
    - Preserves diacritics and international characters
    """
    if not name:
        return ""

    # Strip leading/trailing whitespace
    name = name.strip()

    # Remove leading numbering artifacts ("1.", "1)", "#1")
    name = re.sub(r"^[\d]+[.):\-]\s*", "", name)

    # Remove surrounding quotes
    name = name.strip("\"'`""''")

    # Remove stray brackets
    name = re.sub(r"[\[\]{}()]", "", name)

    # Collapse multiple spaces
    name = re.sub(r"\s+", " ", name)

    # Trim to reasonable length (USPTO name fields max ~50 chars)
    if len(name) > 60:
        name = name[:60].rstrip()

    return name.strip()


# ============================================================================
# Convenience: Validate at Upload Endpoint
# ============================================================================


def validate_upload(
    file_content: bytes,
    filename: str,
    content_type: str,
) -> dict:
    """
    One-call validation for the upload endpoint.
    Combines MIME type check + magic bytes + format-specific checks.

    Usage in your FastAPI endpoint:
        from app.services.file_validators import validate_upload, FileValidationError

        @router.post("/upload")
        async def upload_document(file: UploadFile):
            content = await file.read()
            try:
                validation = validate_upload(content, file.filename, file.content_type)
            except FileValidationError as e:
                raise HTTPException(status_code=400, detail=e.message)
    """
    # Check MIME type first (fast, before reading content)
    allowed_mimes = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        # Some browsers send generic MIME for docx
        "application/octet-stream",
        "application/zip",
    }

    if content_type and content_type not in allowed_mimes:
        raise FileValidationError(
            f"Unsupported file type: {content_type}. "
            "Please upload a PDF or DOCX file.",
            error_code="UNSUPPORTED_MIME",
        )

    # Run full integrity checks
    return validate_file_integrity(file_content, filename)


# ============================================================================
# Convenience: Validate Before LLM Processing (in Celery worker)
# ============================================================================


def validate_before_extraction(
    file_content: bytes,
    file_type: str,
    max_pages: int = 10,
) -> dict:
    """
    Pre-extraction validation for the Celery worker / job service.
    Call this AFTER downloading from GCS, BEFORE sending to LLM.

    Returns dict with:
        - content (bytes): possibly truncated PDF content
        - extraction_strategy (str): "text", "vision", or "docx_text"
        - page_count (int): original page count
        - was_truncated (bool)
        - warnings (list[str])
    """
    result = {
        "content": file_content,
        "extraction_strategy": "text",
        "page_count": 1,
        "was_truncated": False,
        "warnings": [],
    }

    if file_type == "docx":
        result["extraction_strategy"] = "docx_text"
        return result

    if file_type == "pdf":
        # Assess text content to determine extraction strategy
        assessment = assess_pdf_text_content(file_content)
        result["page_count"] = assessment["total_pages"]
        result["extraction_strategy"] = assessment["recommendation"]

        if assessment["is_likely_scanned"]:
            result["warnings"].append(
                f"Scanned document detected ({assessment['total_chars']} chars "
                f"across {assessment['total_pages']} pages). Using vision extraction."
            )

        # Truncate if too many pages
        if assessment["total_pages"] > max_pages:
            truncated, original_count, was_truncated = truncate_pdf_pages(
                file_content, max_pages
            )
            result["content"] = truncated
            result["was_truncated"] = was_truncated
            result["warnings"].append(
                f"Document has {original_count} pages. "
                f"Only the first {max_pages} pages will be analyzed."
            )

    return result