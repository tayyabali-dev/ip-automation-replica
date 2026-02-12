from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from app.models.enhanced_extraction import EnhancedExtractionResult
from app.services.enhanced_extraction_service import EnhancedExtractionService
from app.services.validation_service import ValidationService
from app.services.ads_generator import ADSGenerator
from app.models.user import UserResponse
from app.api.deps import get_current_user
from app.db.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
import shutil
import uuid
import logging
import bson
import io
from typing import Dict, Any, List
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze-enhanced", response_model=EnhancedExtractionResult)
async def analyze_application_enhanced(file: UploadFile = File(...)):
    """
    Analyze an uploaded PDF file using the enhanced extraction system.
    Extracts comprehensive ADS information including all USPTO Form PTO/SB/14 fields.
    """
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    temp_file_path = f"temp_{uuid.uuid4()}.pdf"
    
    try:
        logger.info(f"Starting enhanced analysis for file: {file.filename}")

        # Save uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Initialize enhanced extraction service
        extraction_service = EnhancedExtractionService()
        validation_service = ValidationService()
        
        # Perform enhanced extraction
        try:
            # Step 1: Extract data using enhanced service
            extraction_result = await extraction_service.extract_with_two_step_process(temp_file_path)
            
            # Step 2: Validate extracted data
            validated_result = await validation_service.validate_extraction_result(extraction_result)
            
            logger.info(f"Enhanced analysis complete for {file.filename}")
            logger.info(f"Quality Score: {validated_result.quality_metrics.overall_quality_score:.2f}")
            logger.info(f"Manual Review Required: {validated_result.manual_review_required}")
            
            if validated_result.inventors:
                logger.info(f"Found {len(validated_result.inventors)} inventors")
            if validated_result.applicants:
                logger.info(f"Found {len(validated_result.applicants)} applicants")
            if validated_result.correspondence_info:
                logger.info("Found correspondence information")
            if validated_result.attorney_agent_info:
                logger.info("Found attorney/agent information")
            if validated_result.domestic_priority_claims:
                logger.info(f"Found {len(validated_result.domestic_priority_claims)} domestic priority claims")
            if validated_result.foreign_priority_claims:
                logger.info(f"Found {len(validated_result.foreign_priority_claims)} foreign priority claims")
                
            return validated_result
            
        except HTTPException as he:
            # Re-raise HTTP exceptions directly
            raise he
        except Exception as e:
            logger.error(f"Enhanced extraction failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to perform enhanced extraction: {str(e)}"
            )
            
    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.post("/generate-enhanced-ads")
async def generate_enhanced_ads(data: EnhancedExtractionResult):
    """
    Generate an ADS PDF from enhanced extraction result with all new fields populated.
    """
    try:
        # Initialize ADS generator
        ads_generator = ADSGenerator()
        
        # Generate ADS PDF with enhanced data
        pdf_stream = ads_generator.generate_ads_pdf(data)
        
        # Create filename
        filename = f"Enhanced_ADS_{data.application_number.replace('/', '-') if data.application_number else 'Draft'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        logger.error(f"Enhanced ADS generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate enhanced ADS: {str(e)}"
        )

@router.post("/validate-extraction")
async def validate_extraction_data(data: EnhancedExtractionResult):
    """
    Validate extraction result data and return validation details.
    """
    try:
        validation_service = ValidationService()
        
        # Perform validation
        validated_result = await validation_service.validate_extraction_result(data)
        
        # Return validation summary
        return {
            "validation_summary": {
                "overall_quality_score": validated_result.quality_metrics.overall_quality_score,
                "completeness_score": validated_result.quality_metrics.completeness_score,
                "accuracy_score": validated_result.quality_metrics.accuracy_score,
                "confidence_score": validated_result.quality_metrics.confidence_score,
                "consistency_score": validated_result.quality_metrics.consistency_score,
                "manual_review_required": validated_result.manual_review_required,
                "field_validations_count": len(validated_result.field_validations),
                "cross_field_validations_count": len(validated_result.cross_field_validations),
                "validation_errors": validated_result.quality_metrics.validation_errors,
                "validation_warnings": validated_result.quality_metrics.validation_warnings
            },
            "field_validations": [
                {
                    "field_name": fv.field_name,
                    "is_valid": fv.validation_result.is_valid,
                    "errors": fv.validation_result.errors,
                    "warnings": fv.validation_result.warnings,
                    "confidence_score": fv.validation_result.confidence_score
                }
                for fv in validated_result.field_validations
                if not fv.validation_result.is_valid or fv.validation_result.warnings
            ],
            "cross_field_validations": [
                {
                    "validation_type": cfv.validation_type,
                    "is_consistent": cfv.is_consistent,
                    "issues": cfv.issues,
                    "recommendations": cfv.recommendations,
                    "confidence_impact": cfv.confidence_impact
                }
                for cfv in validated_result.cross_field_validations
                if not cfv.is_consistent
            ],
            "recommendations": validated_result.recommendations,
            "extraction_warnings": validated_result.extraction_warnings
        }
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate extraction data: {str(e)}"
        )

@router.post("/save-enhanced-application", status_code=status.HTTP_201_CREATED)
async def save_enhanced_application(
    data: EnhancedExtractionResult,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Save enhanced extraction result as a new application record.
    """
    try:
        # Deduplication: Check if same application was saved in the last 60 seconds
        from datetime import timedelta
        dedup_window = datetime.utcnow() - timedelta(seconds=60)

        existing = await db.enhanced_applications.find_one({
            "created_by": current_user.id,
            "title": data.title,
            "application_number": data.application_number,
            "created_at": {"$gte": dedup_window.isoformat()}
        })

        if existing:
            logger.info(f"Duplicate save prevented for application: {data.title}")
            return {
                "application_id": str(existing["_id"]),
                "message": "Application already saved (duplicate prevented)",
                "quality_score": data.quality_metrics.overall_quality_score,
                "manual_review_required": data.manual_review_required
            }

        # Create application document - use model_dump() with proper serialization
        app_doc = data.model_dump(mode='json')  # Use JSON mode for proper serialization

        # Add metadata fields
        app_doc.update({
            "created_by": current_user.id,
            "created_at": datetime.utcnow(),
            "workflow_status": "extracted"
        })
        
        # Convert datetime objects to strings for BSON compatibility
        def convert_for_bson(obj):
            """Recursively convert objects to BSON-compatible types"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_for_bson(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_bson(item) for item in obj]
            else:
                return obj
        
        # Apply BSON conversion
        app_doc = convert_for_bson(app_doc)
        
        # Calculate BSON size
        try:
            bson_size = len(bson.BSON.encode(app_doc))
            if bson_size > 16 * 1024 * 1024:  # 16MB
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Application record size ({bson_size} bytes) exceeds the 16MB limit."
                )
        except Exception as bson_error:
            logger.error(f"BSON encoding failed: {bson_error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data serialization failed: {str(bson_error)}"
            )
        
        # Insert into database
        new_app = await db.enhanced_applications.insert_one(app_doc)
        
        return {
            "application_id": str(new_app.inserted_id),
            "message": "Enhanced application saved successfully",
            "quality_score": data.quality_metrics.overall_quality_score,
            "manual_review_required": data.manual_review_required
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions directly
        raise
    except Exception as e:
        logger.error(f"Failed to save enhanced application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save enhanced application"
        )

@router.get("/enhanced-applications", response_model=List[Dict[str, Any]])
async def get_enhanced_applications(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
    skip: int = 0,
    limit: int = 20
):
    """
    Get list of enhanced applications for the current user.
    """
    try:
        cursor = db.enhanced_applications.find(
            {"created_by": current_user.id}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        applications = []
        async for app in cursor:
            app["_id"] = str(app["_id"])
            applications.append(app)
        
        return applications
        
    except Exception as e:
        logger.error(f"Failed to retrieve enhanced applications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve enhanced applications"
        )

@router.get("/enhanced-applications/{application_id}", response_model=Dict[str, Any])
async def get_enhanced_application(
    application_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get a specific enhanced application by ID.
    """
    try:
        from bson import ObjectId
        
        app = await db.enhanced_applications.find_one({
            "_id": ObjectId(application_id),
            "created_by": current_user.id
        })
        
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enhanced application not found"
            )
        
        app["_id"] = str(app["_id"])
        return app
        
    except Exception as e:
        logger.error(f"Failed to retrieve enhanced application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve enhanced application"
        )

@router.post("/enhanced-applications/{application_id}/generate-ads")
async def generate_ads_from_saved_application(
    application_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Generate ADS PDF from a saved enhanced application.
    """
    try:
        from bson import ObjectId
        
        # Get the saved application
        app = await db.enhanced_applications.find_one({
            "_id": ObjectId(application_id),
            "created_by": current_user.id
        })
        
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enhanced application not found"
            )
        
        # Remove MongoDB-specific fields
        app_data = {k: v for k, v in app.items() if k not in ['_id', 'created_by', 'created_at', 'workflow_status']}
        
        # Convert back to EnhancedExtractionResult format
        extraction_result = EnhancedExtractionResult(**app_data)
        
        # Convert to PatentApplicationMetadata
        from app.models.patent_application import PatentApplicationMetadata, Inventor, Applicant
        
        # Convert inventors
        patent_inventors = []
        for inv in extraction_result.inventors:
            patent_inventor = Inventor(
                first_name=inv.given_name,
                middle_name=inv.middle_name,
                last_name=inv.family_name,
                name=inv.full_name,
                street_address=inv.street_address,
                city=inv.city,
                state=inv.state,
                zip_code=inv.postal_code,
                country=inv.country,
                citizenship=inv.citizenship,
                extraction_confidence=inv.confidence_score
            )
            patent_inventors.append(patent_inventor)
        
        # Convert applicants
        patent_applicants = []
        for app_item in extraction_result.applicants:
            patent_applicant = Applicant(
                name=app_item.organization_name or f"{app_item.individual_given_name or ''} {app_item.individual_family_name or ''}".strip(),
                org_name=app_item.organization_name,
                is_organization=bool(app_item.organization_name),
                first_name=app_item.individual_given_name,
                last_name=app_item.individual_family_name,
                street_address=app_item.street_address,
                city=app_item.city,
                state=app_item.state,
                zip_code=app_item.postal_code,
                country=app_item.country,
                phone=app_item.phone_number,
                email=app_item.email_address
            )
            patent_applicants.append(patent_applicant)
        
        patent_metadata = PatentApplicationMetadata(
            title=extraction_result.title,
            application_number=extraction_result.application_number,
            filing_date=extraction_result.filing_date,
            entity_status=extraction_result.entity_status,
            total_drawing_sheets=extraction_result.total_drawing_sheets,
            inventors=patent_inventors,
            applicants=patent_applicants,
            extraction_confidence=extraction_result.quality_metrics.overall_quality_score
        )
        
        # Generate ADS PDF
        ads_generator = ADSGenerator()
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            ads_generator.generate_ads_pdf(patent_metadata, temp_path)
            
            with open(temp_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
            
            pdf_stream = io.BytesIO(pdf_content)
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        # Create filename
        filename = f"Enhanced_ADS_{extraction_result.application_number.replace('/', '-') if extraction_result.application_number else 'Draft'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate ADS from saved application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate ADS: {str(e)}"
        )