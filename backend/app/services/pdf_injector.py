import logging
import io
import pikepdf

logger = logging.getLogger(__name__)

class PDFInjector:
    """
    Service to inject XFA XML data into a PDF template using pikepdf.
    Operations are performed in-memory.
    
    Enhanced to work with the new ads_xfa_builder XML format that fixes
    all 6 critical bugs in ADS form generation.
    """

    @staticmethod
    def inject_xml(template_path: str, xml_data: str) -> io.BytesIO:
        """
        Injects the provided XML string into the XFA 'datasets' stream of the PDF template.
        
        Args:
            template_path: Path to the PDF template file.
            xml_data: The XFA XML string to inject (from ads_xfa_builder).
            
        Returns:
            io.BytesIO: The resulting PDF as a binary stream.
        """
        logger.info(f"Injecting enhanced XFA XML into PDF template: {template_path}")
        
        # Validate XML data
        if not xml_data or not xml_data.strip():
            raise ValueError("XML data is empty or None")
        
        # Log XML structure for debugging
        if logger.isEnabledFor(logging.DEBUG):
            xml_preview = xml_data[:500] + "..." if len(xml_data) > 500 else xml_data
            logger.debug(f"XML data preview: {xml_preview}")
        
        try:
            # Open the template PDF
            with pikepdf.Pdf.open(template_path) as pdf:
                # Ensure xml_data is bytes
                xml_bytes = xml_data.encode('utf-8')
                logger.debug(f"XML data size: {len(xml_bytes)} bytes")
                
                # 1. Try Standard API (pdf.Xfa)
                if hasattr(pdf, 'Xfa'):
                    try:
                        pdf.Xfa['datasets'] = xml_bytes
                        logger.info("Successfully injected XML using standard pdf.Xfa API")
                        return PDFInjector._save_to_buffer(pdf)
                    except Exception as e:
                        logger.warning(f"Standard pdf.Xfa assignment failed: {e}. Trying manual fallback.")
                
                # 2. Manual Injection Fallback (pdf.Root.AcroForm.XFA)
                try:
                    # Access AcroForm.XFA directly
                    acroform = None
                    if '/AcroForm' in pdf.Root:
                        acroform = pdf.Root['/AcroForm']
                    elif 'AcroForm' in pdf.Root:
                         acroform = pdf.Root['AcroForm']
                    else:
                         # Try attribute access just in case
                         try:
                             acroform = pdf.Root.AcroForm
                         except AttributeError:
                             raise ValueError("No /AcroForm in PDF Root.")

                    xfa_array = None
                    if '/XFA' in acroform:
                        xfa_array = acroform['/XFA']
                    elif 'XFA' in acroform:
                        xfa_array = acroform['XFA']
                    else:
                         try:
                             xfa_array = acroform.XFA
                         except AttributeError:
                            raise ValueError("No /XFA in AcroForm.")
                    
                    logger.debug(f"Found XFA array with {len(xfa_array)} elements")
                    
                    # Iterate through XFA array (key, value pairs)
                    injected = False
                    for i in range(0, len(xfa_array), 2):
                        key = xfa_array[i]
                        # key is usually a pikepdf.String, need to cast to str
                        key_str = str(key)
                        logger.debug(f"Processing XFA key: {key_str}")
                        
                        if key_str == "datasets":
                            # The next item is the stream to replace
                            new_stream = pikepdf.Stream(pdf, xml_bytes)
                            xfa_array[i+1] = new_stream
                            injected = True
                            logger.info("Successfully injected enhanced XFA datasets via manual AcroForm array method")
                            break
                    
                    if injected:
                         return PDFInjector._save_to_buffer(pdf)
                    else:
                        logger.warning("XFA found but 'datasets' key missing in manual scan.")
                        # Log all keys for debugging
                        all_keys = [str(xfa_array[i]) for i in range(0, len(xfa_array), 2)]
                        logger.debug(f"Available XFA keys: {all_keys}")
                        raise ValueError("XFA 'datasets' key not found.")
                        
                except Exception as e:
                    # Collect keys for debugging
                    root_keys = list(pdf.Root.keys())
                    logger.error(f"Manual XFA injection failed. Root keys: {root_keys}")
                    raise ValueError(f"Failed to inject XFA. Manual check failed: {e}. Root Keys: {root_keys}")

        except Exception as e:
            logger.error(f"Failed to inject enhanced XML into PDF: {e}")
            raise e

    @staticmethod
    def _save_to_buffer(pdf: pikepdf.Pdf) -> io.BytesIO:
        """
        Save the PDF to a BytesIO buffer.
        
        Args:
            pdf: The pikepdf.Pdf object to save
            
        Returns:
            io.BytesIO: Buffer containing the PDF data
        """
        output_buffer = io.BytesIO()
        pdf.save(output_buffer)
        output_buffer.seek(0)
        logger.debug(f"Saved PDF to buffer, size: {len(output_buffer.getvalue())} bytes")
        return output_buffer

    @staticmethod
    def validate_xml_structure(xml_data: str) -> bool:
        """
        Validates that the XML data has the expected structure for ADS forms.
        
        Args:
            xml_data: The XML string to validate
            
        Returns:
            bool: True if the XML structure is valid
        """
        try:
            # Check for required root elements
            required_elements = [
                '<xfa:datasets',
                '<xfa:data>',
                '<us-request>',
                '<ContentArea1>',
                '<ContentArea2>',
                '<ContentArea3>'
            ]
            
            for element in required_elements:
                if element not in xml_data:
                    logger.warning(f"Missing required XML element: {element}")
                    return False
            
            # Check for bug fixes indicators
            bug_fix_indicators = [
                'sfInventorRepInfo',  # Bug 5 fix
                'sfAssigneeHeader',   # Bug 4 fix
                'ResidencyRadio',     # Bug 1 fix
                'CitizedDropDown'     # Bug 3 fix
            ]
            
            fixes_found = 0
            for indicator in bug_fix_indicators:
                if indicator in xml_data:
                    fixes_found += 1
            
            logger.info(f"XML validation: {fixes_found}/{len(bug_fix_indicators)} bug fix indicators found")
            return fixes_found >= 3  # At least 3 out of 4 indicators should be present
            
        except Exception as e:
            logger.error(f"XML validation failed: {e}")
            return False