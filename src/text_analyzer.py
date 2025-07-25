# Text Analysis Module
# Advanced text processing and section extraction

import re
import nltk
from typing import Dict, List, Any, Tuple
import numpy as np
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class TextAnalyzer:
    """
    Handles text analysis, section extraction, and content processing.
    """
    
    def __init__(self):
        self._download_nltk_data()
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
        
        # Domain-specific keywords for different personas
        self.domain_keywords = {
            'academic': [
                'research', 'study', 'analysis', 'methodology', 'findings',
                'literature', 'experiment', 'hypothesis', 'theory', 'data',
                'results', 'discussion', 'conclusion', 'references', 'abstract'
            ],
            'business': [
                'revenue', 'profit', 'market', 'strategy', 'growth', 'analysis',
                'performance', 'investment', 'financial', 'competitive', 'trends',
                'forecast', 'opportunity', 'risk', 'management', 'stakeholder'
            ],
            'technical': [
                'implementation', 'system', 'architecture', 'framework', 'solution',
                'development', 'integration', 'performance', 'optimization', 'design',
                'specification', 'requirements', 'testing', 'deployment', 'maintenance'
            ],
            'food': [
                'recipe', 'ingredients', 'cooking', 'preparation', 'vegetarian',
                'gluten-free', 'nutrition', 'serving', 'meal', 'buffet', 'menu',
                'dietary', 'cuisine', 'flavor', 'technique', 'temperature'
            ],
            'travel': [
                'destination', 'accommodation', 'transportation', 'activities',
                'attractions', 'culture', 'local', 'budget', 'itinerary', 'booking',
                'recommendation', 'experience', 'sightseeing', 'restaurant', 'hotel'
            ]
        }
    
    def _download_nltk_data(self):
        """Download required NLTK data."""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
    
    def extract_sections(self, doc_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract meaningful sections from document content.
        
        Args:
            doc_content: Document content with pages and text
            
        Returns:
            List of extracted sections with metadata
        """
        sections = []
        
        # Method 1: Header-based extraction
        header_sections = self._extract_by_headers(doc_content)
        sections.extend(header_sections)
        
        # Method 2: Paragraph-based extraction for documents without clear headers
        if len(header_sections) < 3:
            paragraph_sections = self._extract_by_paragraphs(doc_content)
            sections.extend(paragraph_sections)
        
        # Method 3: Sliding window approach for continuous text
        if len(sections) < 5:
            window_sections = self._extract_by_sliding_window(doc_content)
            sections.extend(window_sections)
        
        # Remove duplicates and merge similar sections
        sections = self._deduplicate_sections(sections)
        
        # Add text statistics
        for section in sections:
            section.update(self._calculate_text_stats(section['content']))
        
        return sections
    
    def _extract_by_headers(self, doc_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sections using document headers."""
        sections = []
        current_section = None
        
        for page in doc_content['pages']:
            page_num = page['page_number']
            
            # Look for headers in structured content
            if 'structured_content' in page:
                headers = page['structured_content'].get('headers', [])
                
                for header in headers:
                    # Save previous section
                    if current_section and current_section['content'].strip():
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        'title': header['text'],
                        'page_number': page_num,
                        'content': '',
                        'extraction_method': 'header_based'
                    }
                
                # Add paragraphs to current section
                if current_section:
                    paragraphs = page['structured_content'].get('paragraphs', [])
                    for paragraph in paragraphs:
                        current_section['content'] += paragraph['text'] + "\\n\\n"
            
            # Fallback: extract from raw text
            else:
                text_lines = page['raw_text'].split('\\n')
                for line in text_lines:
                    line = line.strip()
                    if self._is_likely_header(line):
                        if current_section and current_section['content'].strip():
                            sections.append(current_section)
                        
                        current_section = {
                            'title': line,
                            'page_number': page_num,
                            'content': '',
                            'extraction_method': 'header_based'
                        }
                    elif current_section and line:
                        current_section['content'] += line + "\\n"
        
        # Add final section
        if current_section and current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _extract_by_paragraphs(self, doc_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sections by grouping paragraphs."""
        sections = []
        
        for page in doc_content['pages']:
            page_num = page['page_number']
            
            # Split text into paragraphs
            paragraphs = re.split(r'\\n\\s*\\n', page['raw_text'])
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            # Group paragraphs into sections (3-5 paragraphs per section)
            for i in range(0, len(paragraphs), 4):
                section_paragraphs = paragraphs[i:i+4]
                content = '\\n\\n'.join(section_paragraphs)
                
                if len(content.split()) >= 50:  # Minimum word count
                    # Generate title from first sentence
                    first_sentence = re.split(r'[.!?]', content)[0]
                    title = self._generate_section_title(first_sentence)
                    
                    sections.append({
                        'title': title,
                        'page_number': page_num,
                        'content': content,
                        'extraction_method': 'paragraph_based'
                    })
        
        return sections
    
    def _extract_by_sliding_window(self, doc_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sections using sliding window approach."""
        sections = []
        window_size = 250  # words per section
        overlap = 50      # words overlap
        
        full_text = doc_content['full_text']
        words = full_text.split()
        
        if len(words) < window_size:
            return sections
        
        for i in range(0, len(words) - window_size + 1, window_size - overlap):
            section_words = words[i:i + window_size]
            content = ' '.join(section_words)
            
            # Find the page number for this section
            page_num = self._find_page_for_text(content, doc_content['pages'])
            
            # Generate title
            title = self._generate_section_title(content[:100])
            
            sections.append({
                'title': title,
                'page_number': page_num,
                'content': content,
                'extraction_method': 'sliding_window'
            })
        
        return sections
    
    def _is_likely_header(self, text: str) -> bool:
        """Determine if text is likely a section header."""
        text = text.strip()
        
        if not text or len(text) > 150:
            return False
        
        # Check for common header patterns
        header_patterns = [
            r'^\\d+\\.?\\s+[A-Z]',  # Numbered sections
            r'^[A-Z][A-Z\\s]+$',     # ALL CAPS
            r'^[A-Z][a-z\\s]+:$',    # Title case with colon
            r'^(Abstract|Introduction|Conclusion|References|Executive Summary)',
            r'^(Overview|Results|Discussion|Methodology|Background)'
        ]
        
        for pattern in header_patterns:
            if re.match(pattern, text):
                return True
        
        # Additional heuristics
        if text.isupper() and len(text.split()) <= 8:
            return True
        
        if text.endswith(':') and len(text.split()) <= 6:
            return True
        
        return False
    
    def _generate_section_title(self, text: str) -> str:
        """Generate a meaningful title from text content."""
        # Clean the text
        text = re.sub(r'[^a-zA-Z0-9\\s]', '', text)
        words = text.split()[:10]  # First 10 words
        
        if len(words) >= 3:
            return ' '.join(words[:6]) + "..."
        else:
            return ' '.join(words) if words else "Untitled Section"
    
    def _find_page_for_text(self, text: str, pages: List[Dict[str, Any]]) -> int:
        """Find which page contains the given text."""
        text_start = text[:50]  # First 50 characters
        
        for page in pages:
            if text_start in page['raw_text']:
                return page['page_number']
        
        return 1  # Default to first page
    
    def _deduplicate_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or very similar sections."""
        if not sections:
            return sections
        
        unique_sections = []
        seen_content = set()
        
        for section in sections:
            # Create a hash of the first 100 characters
            content_hash = section['content'][:100].lower().replace(' ', '')
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_sections.append(section)
        
        return unique_sections
    
    def _calculate_text_stats(self, text: str) -> Dict[str, Any]:
        """Calculate text statistics for a section."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'char_count': len(text),
            'avg_word_length': np.mean([len(word) for word in words]) if words else 0
        }
    
    def analyze_subsections(self, section: Dict[str, Any], 
                          persona_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze and extract refined sub-sections from a main section.
        
        Args:
            section: Main section to analyze
            persona_profile: Persona and job requirements
            
        Returns:
            List of refined sub-sections
        """
        content = section['content']
        
        # Split into paragraphs
        paragraphs = re.split(r'\\n\\s*\\n', content)
        paragraphs = [p.strip() for p in paragraphs if p.strip() and len(p.split()) >= 10]
        
        subsections = []
        
        # Method 1: Individual high-quality paragraphs
        for paragraph in paragraphs:
            if self._is_high_quality_paragraph(paragraph, persona_profile):
                subsections.append({
                    'document': section.get('document_name', ''),
                    'page_number': section['page_number'],
                    'refined_text': paragraph.strip(),
                    'analysis_method': 'paragraph_selection'
                })
        
        # Method 2: Combine related paragraphs
        if len(subsections) < 2:
            combined_subsections = self._combine_related_paragraphs(paragraphs, persona_profile)
            for subsection in combined_subsections:
                subsection.update({
                    'document': section.get('document_name', ''),
                    'page_number': section['page_number'],
                    'analysis_method': 'paragraph_combination'
                })
            subsections.extend(combined_subsections)
        
        return subsections[:3]  # Return top 3 subsections
    
    def _is_high_quality_paragraph(self, paragraph: str, persona_profile: Dict[str, Any]) -> bool:
        """Check if paragraph is high quality and relevant."""
        words = paragraph.split()
        
        # Basic quality checks
        if len(words) < 20 or len(words) > 200:
            return False
        
        # Check for domain relevance
        domain = persona_profile.get('domain', 'general')
        domain_keywords = self.domain_keywords.get(domain, [])
        
        # Count relevant keywords
        relevant_keywords = sum(1 for word in words 
                              if word.lower() in domain_keywords)
        
        keyword_ratio = relevant_keywords / len(words)
        
        # Quality threshold
        return keyword_ratio > 0.02  # At least 2% relevant keywords
    
    def _combine_related_paragraphs(self, paragraphs: List[str], 
                                  persona_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Combine related paragraphs into coherent subsections."""
        if len(paragraphs) < 2:
            return []
        
        combined = []
        
        # Simple approach: combine 2-3 consecutive paragraphs
        for i in range(0, len(paragraphs) - 1, 2):
            combined_text = '\\n\\n'.join(paragraphs[i:i+2])
            
            if len(combined_text.split()) >= 40:
                combined.append({
                    'refined_text': combined_text
                })
        
        return combined[:2]  # Return top 2 combinations
