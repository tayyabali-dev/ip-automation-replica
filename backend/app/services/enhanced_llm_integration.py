"""
Integration module for enhanced extraction system with existing LLM service.
Provides backward compatibility while enabling enhanced features.
"""

import logging
from typing import Optional, Callable, Awaitable, Dict, Any
from datetime import datetime

from app.services.llm import LLMService
from app.services.enhanced_extraction_service import EnhancedExtractionService
from app.services.validation_service import ValidationService
from app.models.enhanced_extraction import (
    EnhancedExtractionResult, ExtractionMethod, ExtractionMetadata
)
from app.models.patent_application import PatentApplicationMetadata

logger = logging.getLogger(__name__)

class EnhancedLLMService(LLMService):
    """
    Enhanced LLM service that extends the existing LLMService with 
    two-step extraction capabilities while maintaining backward compatibility.
    """
    
    def __init__(self):
        super().__init__()
        self.enhanced_extraction_service = EnhancedExtractionService(llm_service=self)
        self.validation_service = ValidationService()
        self.use_enhanced_extraction = True  # Flag to enable/disable enhanced extraction
    
    async def analyze_cover_sheet_enhanced(
        self,
        file_path: str,
        file_content: Optional[bytes] = None,
        progress_callback: Optional[Callable[[int, str], Awaitable[None]]] = None,
        use_validation: bool = True
    ) -> EnhancedExtractionResult:
        """
        Enhanced cover sheet analysis using two-step extraction process.
        
        Args:
            file_path: Path to the document
            file_content: Optional raw bytes of the document
            progress_callback: Optional progress callback function
            use_validation: Whether to perform validation (default: True)
            
        Returns:
            EnhancedExtractionResult with comprehensive data and quality metrics
        """
        try:
            logger.info(f"Starting enhanced extraction for: {file_path}")
            
            # Perform two-step extraction
            result = await self.enhanced_extraction_service.extract_with_two_step_process(
                file_path=file_path,
                file_content=file_content,
                document_type="patent_application",
                progress_callback=progress_callback
            )
            
            # Perform validation if requested
            if use_validation:
                if progress_callback:
                    await progress_callback(95, "Validating extracted data...")
                
                result = await self.validation_service.validate_extraction_result(result)
            
            logger.info(f"Enhanced extraction completed. Quality score: {result.quality_metrics.overall_quality_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced extraction failed: {e}", exc_info=True)
            raise
    
    async def analyze_cover_sheet(
        self,
        file_path: str,
        file_content: Optional[bytes] = None,
        progress_callback: Optional[Callable[[int, str], Awaitable[None]]] = None
    ) -> PatentApplicationMetadata:
        """
        Backward compatible cover sheet analysis.
        Uses enhanced extraction if enabled, otherwise falls back to original method.
        """
        if self.use_enhanced_extraction:
            try:
                # Use enhanced extraction
                enhanced_result = await self.analyze_cover_sheet_enhanced(
                    file_path, file_content, progress_callback
                )
                
                # Convert to legacy format for backward compatibility
                return self._convert_to_legacy_format(enhanced_result)
                
            except Exception as e:
                logger.warning(f"Enhanced extraction failed, falling back to legacy: {e}")
                # Fall back to original method
                return await super().analyze_cover_sheet(file_path, file_content, progress_callback)
        else:
            # Use original method
            return await super().analyze_cover_sheet(file_path, file_content, progress_callback)
    
    def _convert_to_legacy_format(self, enhanced_result: EnhancedExtractionResult) -> PatentApplicationMetadata:
        """
        Convert enhanced extraction result to legacy PatentApplicationMetadata format.
        Now supports multiple applicants by converting all applicants to the new frontend format.
        """
        from app.models.patent_application import Inventor, Applicant
        
        # Convert inventors
        legacy_inventors = []
        for enhanced_inventor in enhanced_result.inventors:
            legacy_inventor = Inventor(
                first_name=enhanced_inventor.given_name,
                middle_name=enhanced_inventor.middle_name,
                last_name=enhanced_inventor.family_name,
                name=enhanced_inventor.full_name,
                street_address=enhanced_inventor.street_address,
                city=enhanced_inventor.city,
                state=enhanced_inventor.state,
                zip_code=enhanced_inventor.postal_code,
                country=enhanced_inventor.country,
                citizenship=enhanced_inventor.citizenship,
                extraction_confidence=enhanced_inventor.confidence_score
            )
            legacy_inventors.append(legacy_inventor)
        
        # Convert all applicants (not just the first one)
        legacy_applicants = []
        for enhanced_applicant in enhanced_result.applicants:
            legacy_applicant = Applicant(
                name=enhanced_applicant.organization_name or
                     f"{enhanced_applicant.individual_given_name or ''} {enhanced_applicant.individual_family_name or ''}".strip(),
                street_address=enhanced_applicant.street_address,
                city=enhanced_applicant.city,
                state=enhanced_applicant.state,
                zip_code=enhanced_applicant.postal_code,
                country=enhanced_applicant.country
            )
            legacy_applicants.append(legacy_applicant)
        
        # Create legacy metadata with multiple applicants support
        legacy_metadata = PatentApplicationMetadata(
            title=enhanced_result.title,
            application_number=enhanced_result.application_number,
            filing_date=enhanced_result.filing_date,
            entity_status=enhanced_result.entity_status,
            inventors=legacy_inventors,
            applicant=legacy_applicants[0] if legacy_applicants else None,  # Keep backward compatibility
            applicants=legacy_applicants,  # New field for multiple applicants
            total_drawing_sheets=enhanced_result.total_drawing_sheets,
            extraction_confidence=enhanced_result.quality_metrics.overall_quality_score,
            debug_reasoning=f"Enhanced extraction - Quality: {enhanced_result.quality_metrics.overall_quality_score:.2f}, Applicants: {len(legacy_applicants)}"
        )
        
        return legacy_metadata
    
    async def get_extraction_quality_report(
        self,
        file_path: str,
        file_content: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Get detailed quality report for extraction.
        """
        try:
            enhanced_result = await self.analyze_cover_sheet_enhanced(
                file_path, file_content, use_validation=True
            )
            
            return {
                "overall_quality_score": enhanced_result.quality_metrics.overall_quality_score,
                "completeness_score": enhanced_result.quality_metrics.completeness_score,
                "accuracy_score": enhanced_result.quality_metrics.accuracy_score,
                "confidence_score": enhanced_result.quality_metrics.confidence_score,
                "consistency_score": enhanced_result.quality_metrics.consistency_score,
                "required_fields_populated": enhanced_result.quality_metrics.required_fields_populated,
                "total_required_fields": enhanced_result.quality_metrics.total_required_fields,
                "validation_errors": enhanced_result.quality_metrics.validation_errors,
                "validation_warnings": enhanced_result.quality_metrics.validation_warnings,
                "manual_review_required": enhanced_result.manual_review_required,
                "recommendations": enhanced_result.recommendations,
                "extraction_warnings": enhanced_result.extraction_warnings,
                "processing_time": enhanced_result.extraction_metadata.processing_time,
                "extraction_method": enhanced_result.extraction_metadata.extraction_method.value
            }
            
        except Exception as e:
            logger.error(f"Quality report generation failed: {e}")
            return {
                "error": str(e),
                "overall_quality_score": 0.0,
                "manual_review_required": True
            }
    
    def enable_enhanced_extraction(self, enabled: bool = True):
        """Enable or disable enhanced extraction."""
        self.use_enhanced_extraction = enabled
        logger.info(f"Enhanced extraction {'enabled' if enabled else 'disabled'}")
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get statistics about extraction performance."""
        # This could be expanded to track statistics over time
        return {
            "enhanced_extraction_enabled": self.use_enhanced_extraction,
            "extraction_service_available": self.enhanced_extraction_service is not None,
            "validation_service_available": self.validation_service is not None
        }


class ExtractionResultConverter:
    """
    Utility class for converting between different extraction result formats.
    """
    
    @staticmethod
    def enhanced_to_legacy(enhanced_result: EnhancedExtractionResult) -> PatentApplicationMetadata:
        """Convert enhanced result to legacy format."""
        service = EnhancedLLMService()
        return service._convert_to_legacy_format(enhanced_result)
    
    @staticmethod
    def legacy_to_enhanced(legacy_result: PatentApplicationMetadata) -> EnhancedExtractionResult:
        """Convert legacy result to enhanced format (best effort)."""
        from app.models.enhanced_extraction import (
            EnhancedInventor, EnhancedApplicant, QualityMetrics, 
            ExtractionMetadata, DataCompleteness
        )
        
        # Convert inventors
        enhanced_inventors = []
        for legacy_inventor in legacy_result.inventors:
            enhanced_inventor = EnhancedInventor(
                given_name=legacy_inventor.first_name,
                middle_name=legacy_inventor.middle_name,
                family_name=legacy_inventor.last_name,
                full_name=legacy_inventor.name,
                street_address=legacy_inventor.street_address,
                city=legacy_inventor.city,
                state=legacy_inventor.state,
                postal_code=legacy_inventor.zip_code,
                country=legacy_inventor.country,
                citizenship=legacy_inventor.citizenship,
                completeness=DataCompleteness.COMPLETE if all([
                    legacy_inventor.first_name, legacy_inventor.last_name,
                    legacy_inventor.city, legacy_inventor.state, legacy_inventor.country
                ]) else DataCompleteness.INCOMPLETE,
                confidence_score=legacy_inventor.extraction_confidence or 0.5
            )
            enhanced_inventors.append(enhanced_inventor)
        
        # Convert applicant
        enhanced_applicants = []
        if legacy_result.applicant:
            enhanced_applicant = EnhancedApplicant(
                organization_name=legacy_result.applicant.name,
                street_address=legacy_result.applicant.street_address,
                city=legacy_result.applicant.city,
                state=legacy_result.applicant.state,
                postal_code=legacy_result.applicant.zip_code,
                country=legacy_result.applicant.country,
                completeness=DataCompleteness.COMPLETE if all([
                    legacy_result.applicant.name, legacy_result.applicant.city,
                    legacy_result.applicant.state, legacy_result.applicant.country
                ]) else DataCompleteness.INCOMPLETE,
                confidence_score=0.5  # Default confidence
            )
            enhanced_applicants.append(enhanced_applicant)
        
        # Create quality metrics (estimated)
        quality_metrics = QualityMetrics(
            completeness_score=legacy_result.extraction_confidence or 0.5,
            accuracy_score=legacy_result.extraction_confidence or 0.5,
            confidence_score=legacy_result.extraction_confidence or 0.5,
            consistency_score=0.8,  # Assume reasonable consistency
            overall_quality_score=legacy_result.extraction_confidence or 0.5,
            required_fields_populated=2 if legacy_result.title and legacy_result.inventors else 1,
            total_required_fields=2,
            optional_fields_populated=sum([
                1 if legacy_result.application_number else 0,
                1 if legacy_result.filing_date else 0,
                1 if legacy_result.entity_status else 0,
                1 if legacy_result.applicant else 0
            ]),
            total_optional_fields=4,
            validation_errors=0,
            validation_warnings=0
        )
        
        # Create extraction metadata
        extraction_metadata = ExtractionMetadata(
            extraction_method=ExtractionMethod.TEXT_EXTRACTION,  # Assume text extraction
            document_type="patent_application",
            processing_time=0.0  # Unknown
        )
        
        # Create enhanced result
        enhanced_result = EnhancedExtractionResult(
            title=legacy_result.title,
            application_number=legacy_result.application_number,
            filing_date=legacy_result.filing_date,
            entity_status=legacy_result.entity_status,
            inventors=enhanced_inventors,
            applicants=enhanced_applicants,
            quality_metrics=quality_metrics,
            extraction_metadata=extraction_metadata,
            manual_review_required=False,
            extraction_warnings=[],
            recommendations=[]
        )
        
        return enhanced_result


# Create enhanced LLM service instance for use throughout the application
enhanced_llm_service = EnhancedLLMService()