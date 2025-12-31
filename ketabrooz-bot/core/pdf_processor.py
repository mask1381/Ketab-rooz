"""
PDF text extraction and processing using PyMuPDF (fitz)
"""
try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    try:
        import pypdf
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False

from typing import Optional
import io


class PDFProcessor:
    """PDF processing utilities using PyMuPDF (preferred) or pypdf (fallback)"""
    
    @staticmethod
    def extract_text(pdf_data: bytes, max_pages: Optional[int] = None) -> str:
        """
        Extract text from PDF using PyMuPDF or pypdf
        """
        if FITZ_AVAILABLE:
            try:
                pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
                text_parts = []
                
                page_count = min(len(pdf_document), max_pages) if max_pages else len(pdf_document)
                
                for page_num in range(page_count):
                    page = pdf_document[page_num]
                    text = page.get_text()
                    if text:
                        text_parts.append(text)
                
                pdf_document.close()
                return "\n\n".join(text_parts)
            except Exception as e:
                raise Exception(f"Failed to extract text from PDF: {str(e)}")
        
        elif PYPDF_AVAILABLE:
            try:
                stream = io.BytesIO(pdf_data)
                reader = pypdf.PdfReader(stream)
                text_parts = []
                
                page_count = min(len(reader.pages), max_pages) if max_pages else len(reader.pages)
                
                for page_num in range(page_count):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                
                return "\n\n".join(text_parts)
            except Exception as e:
                raise Exception(f"Failed to extract text from PDF: {str(e)}")
        else:
            return "Error: Neither PyMuPDF nor pypdf library is installed."
    
    @staticmethod
    def extract_cover(pdf_data: bytes) -> Optional[bytes]:
        """
        Extract cover image (first page) from PDF using PyMuPDF
        """
        if not FITZ_AVAILABLE:
            return None  # pypdf doesn't support image extraction easily
            
        try:
            pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
            
            if len(pdf_document) == 0:
                pdf_document.close()
                return None
            
            # Get first page
            first_page = pdf_document[0]
            
            # Render page to image with good quality
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = first_page.get_pixmap(matrix=mat)
            
            # Convert to PNG bytes
            img_bytes = pix.tobytes("png")
            
            pdf_document.close()
            return img_bytes
        
        except Exception as e:
            print(f"Failed to extract cover: {str(e)}")
            return None
    
    @staticmethod
    def get_page_count(pdf_data: bytes) -> int:
        """
        Get total number of pages in PDF
        """
        if FITZ_AVAILABLE:
            try:
                pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
                count = len(pdf_document)
                pdf_document.close()
                return count
            except Exception as e:
                print(f"Failed to get page count: {str(e)}")
                return 0
        
        elif PYPDF_AVAILABLE:
            try:
                stream = io.BytesIO(pdf_data)
                reader = pypdf.PdfReader(stream)
                return len(reader.pages)
            except Exception as e:
                print(f"Failed to get page count: {str(e)}")
                return 0
        else:
            return 0
