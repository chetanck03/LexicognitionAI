"""PDF parsing and text extraction component."""
import logging
from pathlib import Path
from typing import Optional
import PyPDF2
import pdfplumber
from config import settings
from src.models import ParsedDocument, Section

logger = logging.getLogger(__name__)


class PDFParserError(Exception):
    """Custom exception for PDF parsing errors."""
    pass


class PDFParser:
    """Handles PDF file parsing and text extraction."""
    
    def __init__(self):
        self.max_file_size = settings.max_file_size_bytes
    
    def validate_file(self, file_path: Path) -> None:
        """
        Validate PDF file before processing.
        
        Args:
            file_path: Path to the PDF file
            
        Raises:
            PDFParserError: If file is invalid
        """
        if not file_path.exists():
            raise PDFParserError(f"File not found: {file_path}")
        
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            max_mb = self.max_file_size / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            raise PDFParserError(
                f"File size ({actual_mb:.1f}MB) exceeds maximum allowed size ({max_mb}MB)"
            )
        
        if file_path.suffix.lower() != '.pdf':
            raise PDFParserError(f"Invalid file type. Expected PDF, got {file_path.suffix}")
    
    def extract_metadata(self, pdf_path: Path) -> dict:
        """
        Extract metadata from PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing metadata
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata = reader.metadata or {}
                
                return {
                    'title': metadata.get('/Title', pdf_path.stem),
                    'authors': [metadata.get('/Author', 'Unknown')] if metadata.get('/Author') else [],
                    'page_count': len(reader.pages),
                    'creator': metadata.get('/Creator', ''),
                    'producer': metadata.get('/Producer', ''),
                }
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
            return {
                'title': pdf_path.stem,
                'authors': [],
                'page_count': 0,
            }
    
    def extract_text_pypdf2(self, pdf_path: Path) -> str:
        """
        Extract text using PyPDF2 (fallback method).
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        text_parts = []
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        
        return '\n\n'.join(text_parts)
    
    def extract_text_pdfplumber(self, pdf_path: Path) -> tuple[str, list[Section]]:
        """
        Extract text using pdfplumber (primary method, better for complex layouts).
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (full_text, sections)
        """
        text_parts = []
        sections = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    text_parts.append(text)
                    
                    # Simple section detection based on formatting
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        # Heuristic: lines that are short, uppercase, or numbered might be headings
                        if self._is_likely_heading(line):
                            content = '\n'.join(lines[i+1:i+20])  # Get next 20 lines as content
                            sections.append(Section(
                                heading=line.strip(),
                                content=content,
                                page_number=page_num
                            ))
        
        full_text = '\n\n'.join(text_parts)
        return full_text, sections
    
    def _is_likely_heading(self, line: str) -> bool:
        """
        Heuristic to detect if a line is likely a section heading.
        
        Args:
            line: Text line to check
            
        Returns:
            True if line appears to be a heading
        """
        line = line.strip()
        if not line:
            return False
        
        # Check for common heading patterns
        if len(line) < 100 and (
            line.isupper() or  # All caps
            line[0].isdigit() or  # Starts with number
            line.endswith(':') or  # Ends with colon
            (len(line.split()) <= 6 and line[0].isupper())  # Short and capitalized
        ):
            return True
        
        return False
    
    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse a PDF file and extract structured content.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            ParsedDocument with extracted content
            
        Raises:
            PDFParserError: If parsing fails
        """
        try:
            # Validate file
            self.validate_file(file_path)
            
            # Extract metadata
            metadata = self.extract_metadata(file_path)
            
            # Extract text and sections
            try:
                text, sections = self.extract_text_pdfplumber(file_path)
                logger.info(f"Extracted text using pdfplumber: {len(text)} characters")
            except Exception as e:
                logger.warning(f"pdfplumber failed, falling back to PyPDF2: {e}")
                text = self.extract_text_pypdf2(file_path)
                sections = []
                logger.info(f"Extracted text using PyPDF2: {len(text)} characters")
            
            if not text or len(text.strip()) < 100:
                raise PDFParserError("Extracted text is empty or too short. PDF may be image-based or corrupted.")
            
            return ParsedDocument(
                text=text,
                metadata=metadata,
                sections=sections
            )
            
        except PDFParserError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing PDF: {e}", exc_info=True)
            raise PDFParserError(f"Failed to parse PDF: {str(e)}")
