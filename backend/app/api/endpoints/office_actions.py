from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Query
from fastapi.responses import Response
from typing import List, Optional
from datetime import datetime, date
from app.api.deps import get_current_user
from app.models.user import UserResponse
from app.models.job import JobType, JobStatus
from app.models.office_action import OfficeActionExtractedData, DeadlineCalculation
from app.services.jobs import job_service
from app.services.storage import storage_service
from app.services.report_generator import report_generator
from app.services.deadline_calculator import deadline_calculator
from app.services.response_shell_generator import response_shell_generator, FirmInfo
from app.db.mongodb import get_database
from app.models.document import DocumentInDB, ProcessedStatus
from bson import ObjectId
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/history", response_model=List[dict])
async def get_office_action_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get list of processed Office Actions for the current user.
    Returns pre-computed history summary data for fast display.
    """
    db = await get_database()

    # Query documents that are office actions with extraction data
    cursor = db.documents.find({
        "user_id": str(current_user.id),
        "document_type": "office_action",
        "extraction_data": {"$exists": True, "$ne": None}
    }).sort("created_at", -1).skip(skip).limit(limit)

    documents = await cursor.to_list(length=limit)

    history_items = []
    for doc in documents:
        extraction_data = doc.get("extraction_data", {})

        # Use pre-computed history summary if available (new documents)
        history_summary = extraction_data.get("_history_summary")

        if history_summary:
            # Fast path: use pre-computed summary
            history_items.append({
                "_id": str(doc["_id"]),
                "document_type": "office_action",
                "filename": doc.get("filename"),
                "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
                "processed_status": doc.get("processed_status"),
                **history_summary,
                "deadline_calculation": extraction_data.get("deadline_calculation")
            })
        else:
            # Fallback for older documents without pre-computed summary
            header = extraction_data.get("header", {})
            rejections = extraction_data.get("rejections", [])
            claims_status = extraction_data.get("claims_status", [])

            rejection_counts = {}
            for rej in rejections:
                rej_type = rej.get("rejection_type_normalized") or rej.get("rejection_type", "Unknown")
                rejection_counts[rej_type] = rejection_counts.get(rej_type, 0) + 1

            history_items.append({
                "_id": str(doc["_id"]),
                "document_type": "office_action",
                "filename": doc.get("filename"),
                "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
                "processed_status": doc.get("processed_status"),
                "application_number": header.get("application_number"),
                "title_of_invention": header.get("title_of_invention"),
                "office_action_type": header.get("office_action_type"),
                "office_action_date": header.get("office_action_date"),
                "examiner_name": header.get("examiner_name"),
                "art_unit": header.get("art_unit"),
                "first_named_inventor": header.get("first_named_inventor"),
                "total_claims": len(claims_status),
                "total_rejections": len(rejections),
                "rejection_counts": rejection_counts,
                "deadline_calculation": extraction_data.get("deadline_calculation")
            })

    return history_items


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_office_action(
    file: UploadFile = File(...),
    extract_claim_text: bool = Query(
        False,
        description="If true, attempts to extract full claim text from the Office Action. Increases processing time."
    ),
    current_user: UserResponse = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """
    Upload an Office Action PDF for analysis.
    Starts an async extraction job.

    Args:
        file: The Office Action PDF file
        extract_claim_text: If true, extract full claim text from the document
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # 1. Upload to Storage
    file_content = await file.read()
    filename = f"{uuid.uuid4()}_{file.filename}"
    storage_key = storage_service.upload_file(file_content, filename, file.content_type)

    # 2. Create Document Record
    db = await get_database()
    doc_in_db = DocumentInDB(
        user_id=str(current_user.id),
        filename=file.filename,
        storage_key=storage_key,
        document_type="office_action",
        file_size=len(file_content),
        mime_type=file.content_type,
        processed_status=ProcessedStatus.PENDING,
        created_at=datetime.utcnow(),
        metadata={"extract_claim_text": extract_claim_text}  # Store the flag
    )
    logger.info(f"Creating document with user_id: {str(current_user.id)}, extract_claim_text: {extract_claim_text}")
    result = await db.documents.insert_one(doc_in_db.model_dump(by_alias=True))
    document_id = str(result.inserted_id)

    # 3. Create Processing Job
    job_id = await job_service.create_job(
        user_id=str(current_user.id),
        job_type=JobType.OFFICE_ACTION_ANALYSIS,
        input_refs=[document_id]
    )

    # 4. Trigger Worker (lazy import to avoid startup hang)
    try:
        from app.worker import process_document_extraction_task
        process_document_extraction_task.delay(job_id, document_id, storage_key, extract_claim_text)
    except Exception as task_error:
        logger.error(f"Failed to schedule Celery task: {task_error}")
        logger.warning("Celery task scheduling failed, job created but not scheduled")

    return {"job_id": job_id, "document_id": document_id}


@router.get("/{document_id}", response_model=OfficeActionExtractedData)
async def get_office_action_data(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve extracted Office Action data for a document.
    """
    db = await get_database()

    # Debug: Check if document exists at all
    doc_exists = await db.documents.find_one({"_id": ObjectId(document_id)})
    logger.info(f"Document exists check: {doc_exists is not None}")
    if doc_exists:
        logger.info(f"Document user_id: {doc_exists.get('user_id')} (type: {type(doc_exists.get('user_id'))})")
        logger.info(f"Current user_id: {current_user.id} (type: {type(current_user.id)})")
        logger.info(f"Document status: {doc_exists.get('processed_status')}")
        logger.info(f"Has extraction_data: {bool(doc_exists.get('extraction_data'))}")

        # Check if user_id matches in any format
        doc_user_id = doc_exists.get('user_id')
        current_user_str = str(current_user.id)
        current_user_obj = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id

        logger.info(f"User ID comparison:")
        logger.info(f"  doc_user_id == current_user_str: {doc_user_id == current_user_str}")
        logger.info(f"  doc_user_id == current_user_obj: {doc_user_id == current_user_obj}")
        logger.info(f"  str(doc_user_id) == current_user_str: {str(doc_user_id) == current_user_str}")

    # Try multiple query approaches
    queries_to_try = [
        {"_id": ObjectId(document_id), "user_id": str(current_user.id)},
        {"_id": ObjectId(document_id), "user_id": ObjectId(current_user.id)},
        {"_id": ObjectId(document_id)}  # No user filter for debugging
    ]

    document = None
    for i, query in enumerate(queries_to_try):
        logger.info(f"Trying query {i+1}: {query}")
        document = await db.documents.find_one(query)
        if document:
            logger.info(f"Query {i+1} succeeded!")
            break
        else:
            logger.info(f"Query {i+1} failed")

    # If no document found with user filtering, check if it exists without user filter for debugging
    if not document:
        # Final attempt: check if document exists at all (for debugging)
        any_document = await db.documents.find_one({"_id": ObjectId(document_id)})
        if any_document:
            logger.error(f"Document exists but user access failed. Doc user_id: {any_document.get('user_id')}, Current user: {current_user.id}")
            # Try to fix user_id type mismatch on the fly
            if str(any_document.get('user_id')) == str(current_user.id):
                logger.info("User ID mismatch detected - using document anyway")
                document = any_document
            else:
                raise HTTPException(status_code=403, detail="Access denied to this document")
        else:
            raise HTTPException(status_code=404, detail="Document not found")

    # Check if extraction data exists (more important than status)
    extraction_data = document.get("extraction_data")
    if not extraction_data:
        # Check if processing is still in progress
        status = document.get("processed_status")
        if status in [ProcessedStatus.PENDING, ProcessedStatus.PROCESSING]:
            raise HTTPException(status_code=400, detail=f"Document processing is not complete. Status: {status}")
        else:
            raise HTTPException(status_code=404, detail="No extraction data found")

    return OfficeActionExtractedData(**extraction_data)


@router.put("/{document_id}", response_model=OfficeActionExtractedData)
async def update_office_action_data(
    document_id: str,
    data: OfficeActionExtractedData,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update the extracted data manually.
    """
    db = await get_database()
    result = await db.documents.update_one(
        {"_id": ObjectId(document_id), "user_id": str(current_user.id)},
        {"$set": {"extraction_data": data.model_dump(by_alias=True)}}
    )

    if result.modified_count == 0:
        # Check if exists
        doc = await db.documents.find_one({"_id": ObjectId(document_id), "user_id": str(current_user.id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

    return data


@router.get("/{document_id}/report")
async def generate_report(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Generate and download the Word report.
    """
    db = await get_database()
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": str(current_user.id)
    })

    if not document or not document.get("extraction_data"):
        raise HTTPException(status_code=404, detail="Document or data not found")

    try:
        # Generate Report
        report_stream = report_generator.generate_office_action_report(document["extraction_data"])

        # Return as downloadable file
        headers = {
            'Content-Disposition': f'attachment; filename="Office_Action_Report_{document["filename"]}.docx"'
        }
        return Response(
            content=report_stream.getvalue(),
            headers=headers,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")


@router.get("/{document_id}/response-shell")
async def generate_response_shell(
    document_id: str,
    firm_name: Optional[str] = Query(None, description="Firm name for signature block"),
    attorney_name: Optional[str] = Query(None, description="Attorney name for signature block"),
    attorney_reg_number: Optional[str] = Query(None, description="USPTO registration number"),
    firm_address: Optional[str] = Query(None, description="Firm address"),
    firm_phone: Optional[str] = Query(None, description="Firm phone number"),
    firm_email: Optional[str] = Query(None, description="Firm email"),
    include_claim_amendments: bool = Query(True, description="Include claims amendment section"),
    include_specification_amendments: bool = Query(False, description="Include specification amendment section"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Generate a USPTO Response Shell document (DOCX) with placeholders.

    This generates a formal USPTO response template that includes:
    - Header block with application information
    - Claims amendment section (with status markers)
    - Remarks section with rejection-specific response templates
    - Conclusion and signature block

    Pass firm/attorney information as query parameters to populate the signature block.
    """
    db = await get_database()
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": str(current_user.id)
    })

    if not document or not document.get("extraction_data"):
        raise HTTPException(status_code=404, detail="Document or data not found")

    try:
        # Create FirmInfo from parameters
        firm_info = FirmInfo(
            firm_name=firm_name,
            attorney_name=attorney_name,
            attorney_reg_number=attorney_reg_number,
            firm_address=firm_address,
            firm_phone=firm_phone,
            firm_email=firm_email
        )

        # Parse extracted data
        oa_data = OfficeActionExtractedData(**document["extraction_data"])

        # Generate Response Shell
        response_stream = response_shell_generator.generate_response_shell(
            data=oa_data,
            firm_info=firm_info,
            include_claim_amendments=include_claim_amendments,
            include_specification_amendments=include_specification_amendments
        )

        # Return as downloadable file
        original_filename = document.get("filename", "document").replace(".pdf", "")
        headers = {
            'Content-Disposition': f'attachment; filename="Response_Shell_{original_filename}.docx"'
        }
        return Response(
            content=response_stream.getvalue(),
            headers=headers,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        logger.error(f"Response shell generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate response shell: {str(e)}")


@router.post("/{document_id}/calculate-deadlines", response_model=DeadlineCalculation)
async def calculate_deadlines(
    document_id: str,
    mailing_date: Optional[str] = Query(
        None,
        description="Override the mailing date (ISO format: YYYY-MM-DD). If not provided, uses the extracted date."
    ),
    shortened_period: int = Query(
        3,
        ge=1,
        le=6,
        description="Shortened statutory period in months (default 3)"
    ),
    is_final_action: bool = Query(
        False,
        description="Whether this is a Final Office Action"
    ),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Calculate or recalculate response deadlines with extension fees.

    Returns deadline tiers from the statutory deadline (no extension) through
    the maximum 6-month deadline, with extension fees for micro, small, and
    large entities at each tier.

    Deadlines are adjusted for weekends and US federal holidays.
    """
    db = await get_database()
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": str(current_user.id)
    })

    if not document or not document.get("extraction_data"):
        raise HTTPException(status_code=404, detail="Document or data not found")

    extraction_data = document["extraction_data"]

    # Determine mailing date
    if mailing_date:
        date_to_use = mailing_date
    else:
        # Try to get from extracted data
        header = extraction_data.get("header", {})
        date_to_use = header.get("office_action_date")

        if not date_to_use:
            raise HTTPException(
                status_code=400,
                detail="No mailing date found in extracted data. Please provide a mailing_date parameter."
            )

    # Determine if this is a final action from extracted data if not specified
    if not is_final_action:
        header = extraction_data.get("header", {})
        oa_type = header.get("office_action_type", "").lower()
        is_final_action = "final" in oa_type

    try:
        # Calculate deadlines
        deadline_calc = deadline_calculator.calculate_from_string(
            mailing_date_str=date_to_use,
            shortened_period_months=shortened_period,
            is_final_action=is_final_action
        )

        # Update the document with calculated deadlines
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"extraction_data.deadline_calculation": deadline_calc.model_dump()}}
        )

        return deadline_calc

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Deadline calculation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate deadlines: {str(e)}")


@router.get("/{document_id}/deadlines", response_model=DeadlineCalculation)
async def get_deadlines(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get the calculated deadlines for a document.

    Returns the previously calculated deadline data. Use POST /calculate-deadlines
    to calculate or recalculate.
    """
    db = await get_database()
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": str(current_user.id)
    })

    if not document or not document.get("extraction_data"):
        raise HTTPException(status_code=404, detail="Document or data not found")

    extraction_data = document["extraction_data"]
    deadline_calc = extraction_data.get("deadline_calculation")

    if not deadline_calc:
        raise HTTPException(
            status_code=404,
            detail="No deadline calculation found. Use POST /calculate-deadlines to calculate."
        )

    return DeadlineCalculation(**deadline_calc)
