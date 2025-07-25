# PDF Processing Module
# Handles text extraction and document parsing

# Try to import PDF processing libraries
PDF_AVAILABLE = False
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    fitz = None
    
import re
import logging
from typing import Dict, List, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Handles PDF text extraction and document parsing.
    Optimized for academic and business documents.
    """
    
    def __init__(self):
        self.section_patterns = [
            r'^(\d+\.?\s+[A-Z][^.]*?)$',  # Numbered sections
            r'^([A-Z][A-Z\s]+)$',  # ALL CAPS headers
            r'^([A-Z][a-z\s]+)$',  # Title case headers
            r'^(Abstract|Introduction|Conclusion|References|Bibliography)$',  # Common sections
            r'^(Executive Summary|Overview|Results|Discussion|Methodology)$'  # Business sections
        ]
        
    def extract_text(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured text content from PDF.
        Falls back to text file reading if PDF processing is unavailable.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted content and metadata
        """
        try:
            pdf_file = Path(pdf_path)
            
            # Check for text file fallback (for demo/testing without PyMuPDF)
            txt_fallback = pdf_file.with_suffix('.pdf.txt')
            if not PDF_AVAILABLE or not pdf_file.exists():
                if txt_fallback.exists():
                    logger.info(f"Using text fallback for {pdf_file.name}")
                    return self._extract_from_text_file(str(txt_fallback))
                else:
                    logger.warning(f"PDF processing unavailable and no text fallback found for {pdf_file.name}")
                    return {
                        'text': '',
                        'pages': [{'page_number': 1, 'text': '', 'sections': []}],
                        'sections': [],
                        'metadata': {'filename': pdf_file.name, 'error': 'PDF processing unavailable'}
                    }
            
            # Original PDF processing
            doc = fitz.open(pdf_path)
            
            pages = []
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text with formatting
                text = page.get_text("text")
                
                # Extract text blocks for better structure
                blocks = page.get_text("dict")
                structured_content = self._parse_page_structure(blocks)
                
                page_data = {
                    'page_number': page_num + 1,
                    'raw_text': text,
                    'structured_content': structured_content,
                    'text_length': len(text.strip())
                }
                
                pages.append(page_data)
                full_text += text + "\n"
            
            doc.close()
            
            # Extract document metadata
            metadata = self._extract_metadata(pdf_path, doc)
            
            return {
                'pages': pages,
                'full_text': full_text,
                'metadata': metadata,
                'total_pages': len(pages),
                'total_length': len(full_text)
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise
    
    def _parse_page_structure(self, blocks: Dict[str, Any]) -> Dict[str, Any]:
        """Parse page structure from text blocks."""
        headers = []
        paragraphs = []
        
        for block in blocks.get('blocks', []):
            if 'lines' not in block:
                continue
                
            block_text = ""
            for line in block['lines']:
                for span in line.get('spans', []):
                    text = span.get('text', '').strip()
                    if text:
                        block_text += text + " "
            
            block_text = block_text.strip()
            if not block_text:
                continue
            
            # Classify as header or paragraph
            if self._is_header(block_text):
                headers.append({
                    'text': block_text,
                    'bbox': block.get('bbox', [])
                })
            else:
                paragraphs.append({
                    'text': block_text,
                    'bbox': block.get('bbox', [])
                })
        
        return {
            'headers': headers,
            'paragraphs': paragraphs
        }
    
    def _is_header(self, text: str) -> bool:
        """Determine if text is likely a header/section title."""
        # Check against section patterns
        for pattern in self.section_patterns:
            if re.match(pattern, text.strip()):
                return True
        
        # Additional heuristics
        if len(text) < 100 and text.isupper():
            return True
        
        if len(text) < 80 and text.endswith(':'):
            return True
        
        # Check for numbered sections
        if re.match(r'^\d+\.?\d*\.?\s+[A-Z]', text):
            return True
        
        return False
    
    def _extract_metadata(self, pdf_path: str, doc) -> Dict[str, Any]:
        """Extract document metadata."""
        try:
            metadata = doc.metadata
            file_stats = Path(pdf_path).stat()
            
            return {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'file_size': file_stats.st_size,
                'file_name': Path(pdf_path).name
            }
        except Exception as e:
            logger.warning(f"Could not extract metadata: {str(e)}")
            return {
                'file_name': Path(pdf_path).name,
                'file_size': 0
            }
    
    def extract_sections_by_headers(self, doc_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract document sections based on identified headers.
        
        Args:
            doc_content: Document content from extract_text()
            
        Returns:
            List of sections with headers and content
        """
        sections = []
        current_section = None
        
        for page in doc_content['pages']:
            page_num = page['page_number']
            
            for header in page['structured_content']['headers']:
                # Save previous section if exists
                if current_section:
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'title': header['text'],
                    'page_number': page_num,
                    'content': '',
                    'start_bbox': header['bbox']
                }
            
            # Add paragraphs to current section
            if current_section:
                for paragraph in page['structured_content']['paragraphs']:
                    current_section['content'] += paragraph['text'] + "\n\n"
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        # Clean up sections
        for section in sections:
            section['content'] = section['content'].strip()
            section['word_count'] = len(section['content'].split())
        
        return sections
    
    def _extract_from_text_file(self, txt_path: str) -> Dict[str, Any]:
        """
        Extract content from a text file (fallback when PDF processing unavailable).
        
        Args:
            txt_path: Path to text file
            
        Returns:
            Dictionary with extracted content and metadata
        """
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse sections from markdown-style headers
            sections = []
            current_section = None
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines):
                line = line.strip()
                
                # Check for markdown headers
                if line.startswith('#'):
                    # Save previous section
                    if current_section and current_section['content'].strip():
                        sections.append(current_section)
                    
                    # Start new section
                    header_level = len(line) - len(line.lstrip('#'))
                    title = line.lstrip('#').strip()
                    
                    current_section = {
                        'title': title,
                        'page_number': 1,  # Assume single page for text files
                        'content': '',
                        'header_level': header_level,
                        'start_line': line_num
                    }
                elif current_section is not None:
                    current_section['content'] += line + '\n'
                elif not sections:
                    # Create default section for content before first header
                    current_section = {
                        'title': 'Introduction',
                        'page_number': 1,
                        'content': line + '\n',
                        'header_level': 1,
                        'start_line': 0
                    }
            
            # Add final section
            if current_section and current_section['content'].strip():
                sections.append(current_section)
            
            # If no sections found, create one with all content
            if not sections and content.strip():
                sections = [{
                    'title': Path(txt_path).stem,
                    'page_number': 1,
                    'content': content,
                    'header_level': 1,
                    'start_line': 0
                }]
            
            # Clean up sections
            for section in sections:
                section['content'] = section['content'].strip()
                section['word_count'] = len(section['content'].split())
            
            result = {
                'text': content,
                'pages': [{
                    'page_number': 1,
                    'text': content,
                    'sections': sections
                }],
                'sections': sections,
                'metadata': {
                    'filename': Path(txt_path).name,
                    'processing_method': 'text_fallback',
                    'total_sections': len(sections)
                }
            }
            
            logger.info(f"Extracted {len(content)} characters from text file with {len(sections)} sections")
            return result
            
        except Exception as e:
            logger.error(f"Error reading text file {txt_path}: {e}")
            return {
                'text': '',
                'pages': [{'page_number': 1, 'text': '', 'sections': []}],
                'sections': [],
                'metadata': {'filename': Path(txt_path).name, 'error': str(e)}
            }
