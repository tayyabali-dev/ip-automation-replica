from datetime import datetime
import datetime as dt_module
from typing import Optional, Dict, Any
from app.db.mongodb import get_database
from app.models.job import JobStatus, JobType, ProcessingJobInDB, ProcessingJobCreate, ProcessingJobResponse
from app.models.document import ProcessedStatus
from app.services.file_validators import (
    validate_before_extraction,
    validate_pdf_not_encrypted,
    FileValidationError,
)
from bson import ObjectId
import logging
import os
import uuid
import time
import io

# Support both PyPDF2 and pypdf (newer name for the same library)
try:
    from PyPDF2 import PdfReader
except ImportError:
    from pypdf import PdfReader

# For content-based PDF analysis
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


def count_pdf_pages(file_content: bytes) -> int:
    """
    Count pages in a PDF file. Used to determine Total Drawing Sheets
    from the actual figures PDF instead of relying on LLM estimation.

    Returns page count, or 0 if file can't be read.
    """
    try:
        reader = PdfReader(io.BytesIO(file_content))
        count = len(reader.pages)
        return count
    except Exception as e:
        # Log the actual error so it's not invisible
        logger.error(f"count_pdf_pages failed: {type(e).__name__}: {e}")
        return 0


def is_figures_pdf(file_content: bytes, filename: str = "") -> bool:
    """
    Detect if a PDF is a figures/drawings file based on CONTENT and FILENAME.
    
    Figures PDFs characteristics:
    - Mostly images/diagrams with sparse text labels
    - Low text-per-page ratio (even with labels, much less than cover sheets)
    - May have "figure", "drawing", "fig" in filename
    
    Cover sheets characteristics:
    - Dense paragraphs of text (title, abstract, claims, inventor info)
    - High text-per-page ratio
    
    Args:
        file_content: Raw PDF bytes
        filename: Original filename (used as secondary signal)
    
    Returns:
        True if PDF appears to be figures (should count pages, skip LLM)
        False if PDF has substantial text (should extract with LLM)
    """
    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
        page_count = len(doc)
        
        if page_count == 0:
            doc.close()
            return False
        
        total_text = ""
        for page in doc:
            total_text += page.get_text()
        
        doc.close()
        
        # Clean the text (remove excessive whitespace)
        cleaned_text = " ".join(total_text.split())
        text_length = len(cleaned_text)
        
        # Calculate text per page ratio
        text_per_page = text_length / page_count
        
        logger.info(
            f"PDF text analysis: {text_length} chars total, "
            f"{page_count} pages, {text_per_page:.0f} chars/page"
        )
        
        # ══════════════════════════════════════════════════════════════════════
        # DETECTION LOGIC (multiple signals)
        # ══════════════════════════════════════════════════════════════════════
        
        # Signal 1: Filename contains figure-related keywords
        filename_lower = filename.lower()
        has_figure_keyword = any(keyword in filename_lower for keyword in [
            'figure', 'figures', 'drawing', 'drawings', 'diagram', 'diagrams',
            'fig_', 'figs_', 'fig-', 'figs-', 'dwg', 'sheet'
        ])
        
        # Signal 2: Very low text per page (typical figures have < 200 chars/page of labels)
        # Cover sheets typically have 1000+ chars/page
        low_text_per_page = text_per_page < 300
        
        # Signal 3: Total text is low even with multiple pages
        # A 14-page figures PDF might have ~2000 chars total (labels)
        # A 14-page cover sheet would have ~14000+ chars
        low_total_text = text_length < (page_count * 400)
        
        # Signal 4: Check for figure-like patterns in text
        # Figures often have: "Figure 1", "FIG. 2", numbers as labels
        text_lower = cleaned_text.lower()
        figure_pattern_count = (
            text_lower.count('figure ') + 
            text_lower.count('fig.') + 
            text_lower.count('fig ')
        )
        has_many_figure_refs = figure_pattern_count >= (page_count * 0.5)  # At least 0.5 per page
        
        # Decision logic:
        # - If filename suggests figures AND text is sparse → figures PDF
        # - If text per page is very low → figures PDF
        # - If has many "Figure X" references and low text density → figures PDF
        
        is_figures = False
        reason = ""
        
        if has_figure_keyword and (low_text_per_page or low_total_text):
            is_figures = True
            reason = f"filename contains figure keyword and sparse text ({text_per_page:.0f} chars/page)"
        elif text_per_page < 150:
            # Very sparse text - almost certainly figures
            is_figures = True
            reason = f"very sparse text ({text_per_page:.0f} chars/page)"
        elif low_text_per_page and has_many_figure_refs:
            is_figures = True
            reason = f"low text density ({text_per_page:.0f} chars/page) with {figure_pattern_count} figure references"
        elif low_text_per_page and low_total_text and page_count >= 3:
            # Multiple pages with consistently low text
            is_figures = True
            reason = f"multi-page PDF with sparse text ({text_per_page:.0f} chars/page, {text_length} total)"
        
        if is_figures:
            logger.info(f"✓ Detected as FIGURES PDF: {reason}")
        else:
            logger.info(
                f"✗ Detected as TEXT PDF: {text_per_page:.0f} chars/page "
                f"(threshold: 300), proceeding with LLM extraction"
            )
        
        return is_figures
        
    except Exception as e:
        # If we can't read the PDF, check filename as fallback
        logger.warning(f"Could not analyze PDF content: {e}")
        
        # Filename-only fallback
        if filename:
            filename_lower = filename.lower()
            if any(kw in filename_lower for kw in ['figure', 'drawing', 'diagram', 'fig_', 'dwg']):
                logger.info(f"Using filename fallback: detected as figures PDF")
                return True
        
        return False


class JobService:
    async def create_job(self, user_id: str, job_type: JobType, input_refs: list[str]) -> str:
        db = await get_database()
        job_in = ProcessingJobCreate(
            user_id=user_id,
            job_type=job_type,
            input_references=input_refs,
            status=JobStatus.PENDING
        )
        job_db = ProcessingJobInDB(**job_in.model_dump())
        result = await db.processing_jobs.insert_one(job_db.model_dump(by_alias=True))
        logger.info(f"Created job {result.inserted_id} for user {user_id} with type {job_type}")
        return str(result.inserted_id)

    async def update_job_status(self, job_id: str, status: JobStatus, progress: int = 0, error: Optional[str] = None):
        db = await get_database()
        update_data = {
            "status": status,
            "progress_percentage": progress,
            "updated_at": datetime.utcnow()
        }
        if status == JobStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
        if error:
            update_data["error_details"] = error
            logger.error(f"Job {job_id} failed: {error}")
            
        await db.processing_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": update_data}
        )
        logger.info(f"Updated job {job_id} status to {status} (Progress: {progress}%)")

    async def get_job(self, job_id: str) -> Optional[ProcessingJobResponse]:
        db = await get_database()
        job = await db.processing_jobs.find_one({"_id": ObjectId(job_id)})
        if job:
            return ProcessingJobResponse(**job)
        return None

    async def cleanup_old_jobs(self, days: int = 7):
        """
        Cleanup jobs older than specified days.
        """
        try:
            db = await get_database()
            cutoff_date = datetime.utcnow() - dt_module.timedelta(days=days)
            
            result = await db.processing_jobs.delete_many({
                "updated_at": {"$lt": cutoff_date},
                "status": {"$in": [JobStatus.COMPLETED, JobStatus.FAILED]}
            })
            
            if result.deleted_count > 0:
                logger.info(f"Cleaned up {result.deleted_count} old jobs (older than {days} days)")
        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {e}")

    async def process_document_extraction(
        self,
        job_id: str,
        document_id: str,
        storage_key: str,
        extract_claim_text: bool = False
    ):
        """
        Background task to process document extraction.
        Handles both ADS Extraction and Office Action Analysis based on job type.

        Args:
            job_id: The job ID for tracking
            document_id: The document ID in MongoDB
            storage_key: The storage key for the file
            extract_claim_text: If true, extract full claim text (Office Action only)
        """
        # Delayed imports to avoid circular dependencies
        from app.services.storage import storage_service
        from app.services.llm import llm_service
        from app.services.audit import audit_service
        from app.core.config import settings
        
        logger.info(f"Starting extraction for Job {job_id} (Doc: {document_id})")
        db = await get_database()
        
        # Get user_id for logging (could be passed in, or fetched from job)
        job = await db.processing_jobs.find_one({"_id": ObjectId(job_id)})
        user_id = str(job["user_id"]) if job else "system"
        job_type = job.get("job_type", JobType.ADS_EXTRACTION)

        job_start_time = time.time()
        
        try:
            # 1. Update Job Status to PROCESSING
            logger.info(f"Setting Job {job_id} to PROCESSING (10%)")
            await self.update_job_status(job_id, JobStatus.PROCESSING, progress=10)
            await db.documents.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": {"processed_status": ProcessedStatus.PROCESSING}}
            )
            
            # 2. Download file from Storage (To Memory)
            logger.info(f"Downloading file {storage_key} to memory...")
            file_content = storage_service.download_as_bytes(storage_key)
            logger.info(f"Download complete ({len(file_content)} bytes). Setting progress to 30%")
            
            await self.update_job_status(job_id, JobStatus.PROCESSING, progress=30)

            # ── Detect file type from storage key ────────────────────────
            file_ext = storage_key.rsplit('.', 1)[-1].lower() if '.' in storage_key else 'pdf'
            file_type = "docx" if file_ext == "docx" else "pdf"
            # ─────────────────────────────────────────────────────────────

            # ── P0 + P1: Pre-extraction validation ───────────────────────
            try:
                # Office Actions are typically 15-30+ pages and contain critical
                # rejection data (§103, examiner contact) in the BACK HALF.
                # Truncating to 10 pages causes missing §103 rejections,
                # missing prior art references, and missing examiner phone.
                if job_type == JobType.OFFICE_ACTION_ANALYSIS:
                    oa_max_pages = 50  # Office Actions need full document
                else:
                    oa_max_pages = 10  # ADS cover sheets are short

                pre_check = validate_before_extraction(
                    file_content=file_content,
                    file_type=file_type,
                    max_pages=oa_max_pages,
                )
            except FileValidationError as e:
                logger.error(f"Validation failed for document {document_id}: {e.message}")
                # Update job status to failed with user-friendly message
                await self.update_job_status(job_id, JobStatus.FAILED, error=e.message)
                await db.documents.update_one(
                    {"_id": ObjectId(document_id)},
                    {"$set": {"processed_status": ProcessedStatus.FAILED}}
                )
                return

            # Use possibly-truncated content
            processing_content = pre_check["content"]
            extraction_strategy = pre_check["extraction_strategy"]

            for warning in pre_check["warnings"]:
                logger.warning(f"Document {document_id}: {warning}")

            # ── P1: Log if document was truncated ────────────────────────
            if pre_check["was_truncated"]:
                logger.info(
                    f"Document {document_id} truncated from "
                    f"{pre_check['page_count']} pages to 10 for analysis"
                )
            # ─────────────────────────────────────────────────────────────

            # ══════════════════════════════════════════════════════════════
            # Check if THIS document is a figures PDF (content + filename)
            # Only applies to ADS extraction - Office Actions should always be analyzed
            # ══════════════════════════════════════════════════════════════

            doc_record = await db.documents.find_one({"_id": ObjectId(document_id)})
            doc_filename = doc_record.get("filename", "") if doc_record else ""

            # Only check for figures if it's a PDF AND it's ADS extraction (not Office Actions)
            if file_ext == 'pdf' and job_type != JobType.OFFICE_ACTION_ANALYSIS and is_figures_pdf(file_content, filename=doc_filename):
                page_count = count_pdf_pages(file_content)
                logger.info(
                    f"✓ Figures PDF confirmed: {doc_filename} "
                    f"({page_count} pages) - skipping LLM extraction"
                )
                if page_count > 0:
                    # Store page count in extraction_data on THIS document
                    metadata_dump = {
                        "is_figures_pdf": True,
                        "figures_page_count": page_count,
                        "total_drawing_sheets": page_count,
                        "filename": doc_filename,
                        # Include empty fields so frontend doesn't break
                        "title": None,
                        "inventors": [],
                        "applicants": [],
                        "application_number": None,
                        "entity_status": None,
                    }

                    # Save and skip LLM extraction (figures PDFs have no metadata)
                    await db.documents.update_one(
                        {"_id": ObjectId(document_id)},
                        {
                            "$set": {
                                "processed_status": ProcessedStatus.COMPLETED,
                                "extraction_data": metadata_dump,
                            }
                        }
                    )
                    # Update job status to complete
                    await self.update_job_status(job_id, JobStatus.COMPLETED, progress=100)
                    logger.info(
                        f"Figures PDF processed: {page_count} pages stored as total_drawing_sheets. "
                        f"LLM extraction skipped."
                    )
                    return  # ← EXIT EARLY, no LLM call needed
            else:
                if file_ext == 'pdf':
                    logger.info(
                        f"✗ Not a figures PDF ({doc_filename}), "
                        f"proceeding with LLM extraction"
                    )

            # ── Not a figures PDF — proceed with normal LLM extraction ─────
            # 3. Perform Extraction
            logger.info("Calling LLM Service...")
            start_time = datetime.utcnow()
            
            # Define progress callback
            async def report_progress(progress: int, message: str):
                await self.update_job_status(job_id, JobStatus.PROCESSING, progress=progress)
                logger.info(f"Job {job_id} progress: {progress}% - {message}")

            # Pass downloaded bytes directly to analyze_cover_sheet/office_action to avoid disk I/O
            if job_type == JobType.OFFICE_ACTION_ANALYSIS:
                logger.info(f"Executing Office Action Analysis for Job {job_id} (extract_claim_text={extract_claim_text})")
                extraction_result = await llm_service.analyze_office_action(
                    file_path=storage_key,
                    file_content=processing_content,
                    progress_callback=report_progress,
                    extract_claim_text=extract_claim_text
                )
                # Convert dict to model if needed, but llm_service returns dict for OA
                # We need to ensure it's JSON serializable for MongoDB
                metadata_dump = extraction_result

                # Pre-compute history summary for faster history queries
                header = extraction_result.get("header", {})
                rejections = extraction_result.get("rejections", [])
                claims_status = extraction_result.get("claims_status", [])

                # Count rejections by type
                rejection_counts = {}
                for rej in rejections:
                    rej_type = rej.get("rejection_type_normalized") or rej.get("rejection_type", "Unknown")
                    rejection_counts[rej_type] = rejection_counts.get(rej_type, 0) + 1

                history_summary = {
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
                }

                # Store history_summary separately for quick access
                metadata_dump["_history_summary"] = history_summary
            else:
                logger.info(f"Executing ADS Extraction for Job {job_id}")
                metadata = await llm_service.analyze_cover_sheet(
                    file_path=storage_key,
                    file_content=processing_content,
                    extraction_strategy=extraction_strategy,  # NEW parameter
                    progress_callback=report_progress
                )
                
                # LLM is unreliable for drawing sheet counts — only trust
                # the figures PDF page count (handled in the early-exit block above).
                # Force null so the user fills it in manually when no figures PDF exists.
                metadata.total_drawing_sheets = None
                
                metadata_dump = metadata.model_dump(by_alias=True)

            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Log LLM Usage
            await audit_service.log_event(
                user_id=user_id,
                event_type="llm_extraction",
                details={
                    "job_id": job_id,
                    "document_id": document_id,
                    "job_type": job_type,
                    "duration_ms": duration_ms,
                    "model": settings.GEMINI_MODEL
                }
            )

            await self.update_job_status(job_id, JobStatus.PROCESSING, progress=90)
            
            # 4. Save Results
            # Store full extraction data in the document
            logger.info("Saving extraction results...")
            await db.documents.update_one(
                {"_id": ObjectId(document_id)},
                {
                    "$set": {
                        "processed_status": ProcessedStatus.COMPLETED,
                        "extraction_data": metadata_dump
                    }
                }
            )
            
            # 5. Complete Job
            await self.update_job_status(job_id, JobStatus.COMPLETED, progress=100)
            logger.info(f"Job {job_id} completed successfully.")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            await self.update_job_status(job_id, JobStatus.FAILED, error=str(e))
            await db.documents.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": {"processed_status": ProcessedStatus.FAILED}}
            )
            
        finally:
            pass

job_service = JobService()