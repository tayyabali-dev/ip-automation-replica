from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from app.models.patent_application import PatentApplicationMetadata, Inventor, PatentApplicationCreate, PatentApplicationResponse, PatentApplicationInDB
from app.models.validation import ADSGenerationResponse, ValidationReport, ValidationSummary
from app.services.llm import llm_service
from app.services.ads_generator import ADSGenerator
from app.services.ads_validator import ADSValidator, ValidationConfig
from app.services.xfa_mapper import XFAMapper
from app.services.pdf_injector import PDFInjector
from app.services.csv_handler import parse_inventors_csv
from app.services.storage import storage_service
from app.services.file_validators import validate_upload, FileValidationError
from app.models.user import UserResponse
from app.api.deps import get_current_user
from app.db.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
import shutil
import uuid
import logging
import bson
from datetime import datetime
from typing import Dict, Any, List

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=PatentApplicationMetadata)
async def analyze_application(file: UploadFile = File(...)):
    """
    Analyze an uploaded PDF file to extract patent application metadata.
    """
    content = await file.read()

    try:
        validation = validate_upload(content, file.filename, file.content_type)
    except FileValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )

    for warning in validation.get("warnings", []):
        logger.warning(f"Analyze warning: {warning}")

    file_type = validation["file_type"]

    # Preserve extension for temp file
    file_ext = file.filename.rsplit('.', 1)[-1] if file.filename else file_type
    temp_file_path = f"temp_{uuid.uuid4()}.{file_ext}"
    
    try:
        logger.info(f"Received file for analysis: {file.filename} (Type: {file.content_type})")

        # Save uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            buffer.write(content)
            
        # Analyze PDF directly with LLM (Native Vision/Multimodal Support)
        try:
            # We pass the file path directly. The LLM service handles uploading to Gemini.
            metadata = await llm_service.analyze_cover_sheet(temp_file_path)
            
            # Log the result before returning
            logger.info(f"Analysis complete for {file.filename}")
            if metadata.inventors:
                logger.info(f"Found {len(metadata.inventors)} inventors: {[inv.name for inv in metadata.inventors]}")
            else:
                logger.warning("No inventors found in the analysis result.")
                
            return metadata
        except HTTPException as he:
            # Re-raise HTTP exceptions (like 503 from LLM service) directly
            raise he
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to analyze PDF content: {str(e)}"
            )
            
    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.post("/parse-csv", response_model=List[Inventor])
async def parse_csv(file: UploadFile = File(...)):
    """
    Parse an uploaded CSV file to extract inventor data.
    """
    # Validate file extension
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    try:
        content = await file.read()
        inventors = parse_inventors_csv(content)
        return inventors
    except Exception as e:
        logger.error(f"CSV parsing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV: {str(e)}"
        )

@router.post("/import-csv", status_code=status.HTTP_201_CREATED)
async def import_csv(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Import a CSV file, create a new application record, and return the application_id.
    """
    # 1. Parse CSV
    # Validate file extension
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    try:
        content = await file.read()
        inventors = parse_inventors_csv(content)
    except Exception as e:
        logger.error(f"CSV parsing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV: {str(e)}"
        )

    # 2. Create Application Record
    try:
        # Create a basic application with the imported inventors
        app_in = PatentApplicationCreate(
            title="Imported via CSV", # Placeholder
            inventors=inventors,
            workflow_status="uploaded" # Using string to avoid enum import issues if tricky
        )
        
        app_db = PatentApplicationInDB(
            **app_in.model_dump(),
            created_by=current_user.id
        )
        
        doc = app_db.model_dump(by_alias=True)
        
        # Insert
        new_app = await db.patent_applications.insert_one(doc)
        
        return {
            "application_id": str(new_app.inserted_id),
            "message": f"Successfully imported {len(inventors)} inventors."
        }
        
    except Exception as e:
        logger.error(f"Failed to create application from CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application record"
        )

@router.post("/", response_model=PatentApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_in: PatentApplicationCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new patent application record.
    Validates that the record size does not exceed MongoDB 16MB limit.
    """
    # Create DB model
    app_db = PatentApplicationInDB(
        **application_in.model_dump(),
        created_by=current_user.id
    )
    
    # Calculate BSON size
    doc = app_db.model_dump(by_alias=True)
    try:
        bson_size = len(bson.BSON.encode(doc))
        if bson_size > 16 * 1024 * 1024: # 16MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Application record size ({bson_size} bytes) exceeds the 16MB limit."
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"BSON encoding failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to validate application record size"
        )

    try:
        new_app = await db.patent_applications.insert_one(doc)
        application_id = new_app.inserted_id
        
        # ── Merge figures PDF page count into total_drawing_sheets ─────
        # Check if any linked document is a figures PDF with a page count
        if application_in.source_document_ids:
            from bson import ObjectId
            for doc_id in application_in.source_document_ids:
                doc = await db.documents.find_one({"_id": ObjectId(doc_id)})
                if doc:
                    extraction_data = doc.get("extraction_data", {})
                    if extraction_data and extraction_data.get("is_figures_pdf"):
                        page_count = extraction_data.get("figures_page_count", 0)
                        if page_count > 0:
                            # Update the application's total_drawing_sheets
                            await db.patent_applications.update_one(
                                {"_id": application_id},
                                {"$set": {"total_drawing_sheets": page_count}}
                            )
                            logger.info(
                                f"Application {application_id}: "
                                f"total_drawing_sheets set to {page_count} "
                                f"from figures PDF"
                            )
                            break
        # ──────────────────────────────────────────────────────────────
        
        created_app = await db.patent_applications.find_one({"_id": application_id})
        return PatentApplicationResponse(**created_app)
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application"
        )

@router.post("/generate-ads", response_model=ADSGenerationResponse)
async def generate_ads_with_validation(data: PatentApplicationMetadata):
    """
    Generate an ADS PDF from the provided metadata with comprehensive validation.
    
    This endpoint implements a hybrid validation approach:
    - CRITICAL ERRORS: Block PDF generation and return error response
    - WARNINGS: Generate PDF but include validation warnings in response
    - INFO: Generate PDF with informational messages about normalizations
    
    Returns:
        ADSGenerationResponse: Complete response including PDF and validation report
    """
    start_time = datetime.utcnow()
    
    try:
        # ══════════════════════════════════════════════════════════════════════
        # CRITICAL VALIDATION: Check inventor count matches original extraction
        # ══════════════════════════════════════════════════════════════════════
        
        # Check if we have original inventor count from extraction
        if data.original_inventor_count is not None and data.original_inventor_count > 0:
            submitted_inventor_count = len(data.inventors) if data.inventors else 0
            
            if submitted_inventor_count != data.original_inventor_count:
                logger.warning(
                    f"Inventor count mismatch: original={data.original_inventor_count}, "
                    f"submitted={submitted_inventor_count}"
                )
                
                # Determine if inventors were added or removed
                if submitted_inventor_count > data.original_inventor_count:
                    action = "added"
                    difference = submitted_inventor_count - data.original_inventor_count
                    action_detail = f"{difference} inventor(s) have been added"
                else:
                    action = "removed"
                    difference = data.original_inventor_count - submitted_inventor_count
                    action_detail = f"{difference} inventor(s) have been removed"
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "inventor_count_changed",
                        "message": (
                            f"Cannot generate ADS: Inventor count has changed from "
                            f"{data.original_inventor_count} to {submitted_inventor_count}. "
                            f"{action_detail}. Re-extraction from the source document is required."
                        ),
                        "original_count": data.original_inventor_count,
                        "submitted_count": submitted_inventor_count,
                        "action": action,
                        "difference": difference,
                    }
                )
        
        # ══════════════════════════════════════════════════════════════════════
        # Continue with normal PDF generation if validation passes...
        # ══════════════════════════════════════════════════════════════════════
        
        # Initialize services
        mapper = XFAMapper()
        validator = ADSValidator(ValidationConfig(
            enable_auto_correction=True,
            strict_country_validation=True,
            normalize_names=True
        ))
        
        # Step 1: Generate XFA XML from metadata
        logger.info(f"Generating XFA XML for application: {data.title}")
        xfa_xml = mapper.map_metadata_to_xml(data)
        
        # Step 2: Validate the generated XML against source metadata
        logger.info("Performing data integrity validation")
        validation_result = validator.validate_ads_output(xfa_xml, data)
        
        # Step 3: Check if generation should be blocked
        if validation_result.generation_blocked:
            logger.error(f"ADS generation blocked due to {len(validation_result.blocking_errors)} critical errors")
            
            return ADSGenerationResponse(
                success=False,
                pdf_generated=False,
                validation_report=validation_result.validation_report,
                generation_blocked=True,
                blocking_errors=validation_result.blocking_errors,
                message=f"PDF generation blocked due to {len(validation_result.blocking_errors)} critical validation errors"
            )
        
        # Step 4: Generate PDF (validation passed or only warnings)
        template_path = _get_template_path()
        
        if not os.path.exists(template_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="XFA template not found"
            )
        
        # Inject XML into PDF
        injector = PDFInjector()
        pdf_stream = injector.inject_xml(template_path, xfa_xml)
        
        # Calculate PDF size
        pdf_stream.seek(0, 2)  # Seek to end
        pdf_size = pdf_stream.tell()
        pdf_stream.seek(0)  # Reset to beginning
        
        # Generate filename
        app_num = data.application_number.replace('/', '-') if data.application_number else 'Draft'
        filename = f"ADS_Filled_{app_num}.pdf"
        
        # Step 5: Log validation results
        report = validation_result.validation_report
        if report.summary.warnings_count > 0:
            logger.warning(f"ADS generated with {report.summary.warnings_count} validation warnings")
        
        if report.summary.auto_corrections_count > 0:
            logger.info(f"Applied {report.summary.auto_corrections_count} automatic corrections")
        
        # Step 6: Return streaming response with validation metadata
        def generate_pdf_with_headers():
            """Generator that yields PDF data with validation headers"""
            # Yield PDF content
            while True:
                chunk = pdf_stream.read(8192)  # 8KB chunks
                if not chunk:
                    break
                yield chunk
        
        return StreamingResponse(
            generate_pdf_with_headers(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Validation-Score": str(report.summary.validation_score),
                "X-Validation-Warnings": str(report.summary.warnings_count),
                "X-Validation-Errors": str(report.summary.errors_count),
                "X-Processing-Time": str(report.processing_time_ms)
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like our inventor count validation) directly
        raise
    except Exception as e:
        logger.error(f"ADS generation failed: {e}", exc_info=True)
        
        # Return error response with validation context
        error_report = ValidationReport(
            is_valid=False,
            summary=ValidationSummary(validation_score=0.0),
            mismatches=[],
            processing_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
            xfa_xml_size=0
        )
        
        return ADSGenerationResponse(
            success=False,
            pdf_generated=False,
            validation_report=error_report,
            generation_blocked=True,
            blocking_errors=[],
            message=f"ADS generation failed: {str(e)}"
        )

@router.post("/validate-ads", response_model=ValidationReport)
async def validate_ads_only(data: PatentApplicationMetadata):
    """
    Validate ADS data without generating PDF.
    Useful for pre-validation before actual generation.
    """
    try:
        mapper = XFAMapper()
        validator = ADSValidator()
        
        # Generate XFA XML
        xfa_xml = mapper.map_metadata_to_xml(data)
        
        # Validate only
        validation_result = validator.validate_ads_output(xfa_xml, data)
        
        return validation_result.validation_report
        
    except Exception as e:
        logger.error(f"ADS validation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )

def _get_template_path() -> str:
    """Get the path to the XFA ADS template"""
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "templates",
        "xfa_ads_template.pdf"
    )
    
    # Fallback to external path if internal template not found
    if not os.path.exists(template_path):
        template_path = os.path.join("..", "Client attachments", "Original ADS from USPTO Website.pdf")
    
    return template_path