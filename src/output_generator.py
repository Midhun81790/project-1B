# Output Generation Module
# Generates structured JSON output in the required format

import json
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class OutputGenerator:
    """
    Generates structured output in the required JSON format.
    """
    
    def __init__(self):
        pass
    
    def generate_output(self, input_config: Dict[str, Any],
                       ranked_sections: List[Dict[str, Any]],
                       subsections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate final output in the required JSON format.
        
        Args:
            input_config: Original input configuration
            ranked_sections: Ranked sections with importance scores
            subsections: Analyzed subsections
            
        Returns:
            Structured output dictionary
        """
        # Extract document filenames
        if isinstance(input_config.get('documents'), list):
            if input_config['documents'] and isinstance(input_config['documents'][0], dict):
                # Format: [{"filename": "doc.pdf", "title": "Title"}]
                input_documents = [doc.get('filename', '') for doc in input_config['documents']]
            else:
                # Format: ["doc1.pdf", "doc2.pdf"]
                input_documents = input_config['documents']
        else:
            input_documents = []
        
        # Generate metadata
        metadata = self._generate_metadata(input_config, input_documents)
        
        # Generate extracted sections (top sections)
        extracted_sections = self._generate_extracted_sections(ranked_sections)
        
        # Generate subsection analysis
        subsection_analysis = self._generate_subsection_analysis(subsections)
        
        output = {
            "metadata": metadata,
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
        
        logger.info(f"Generated output with {len(extracted_sections)} sections and {len(subsection_analysis)} subsections")
        
        return output
    
    def _generate_metadata(self, input_config: Dict[str, Any], 
                          input_documents: List[str]) -> Dict[str, Any]:
        """Generate metadata section."""
        persona_role = input_config.get('persona', {}).get('role', 'Unknown')
        job_task = input_config.get('job_to_be_done', {}).get('task', 'Unknown')
        
        metadata = {
            "input_documents": input_documents,
            "persona": persona_role,
            "job_to_be_done": job_task,
            "processing_timestamp": datetime.now().isoformat()
        }
        
        # Add challenge info if available
        if 'challenge_info' in input_config:
            challenge_info = input_config['challenge_info']
            metadata.update({
                "challenge_id": challenge_info.get('challenge_id', ''),
                "test_case_name": challenge_info.get('test_case_name', ''),
                "description": challenge_info.get('description', '')
            })
        
        return metadata
    
    def _generate_extracted_sections(self, ranked_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate extracted sections list."""
        extracted_sections = []
        
        # Take top sections (limit to reasonable number)
        top_sections = ranked_sections[:10]  # Top 10 sections
        
        for section in top_sections:
            section_entry = {
                "document": section.get('document_name', section.get('name', 'unknown.pdf')),
                "section_title": section.get('title', 'Untitled Section'),
                "importance_rank": section.get('importance_rank', 1),
                "page_number": section.get('page_number', 1)
            }
            
            # Add optional fields if available
            if 'relevance_score' in section:
                section_entry["relevance_score"] = round(section['relevance_score'], 3)
            
            if 'final_score' in section:
                section_entry["final_score"] = round(section['final_score'], 3)
            
            extracted_sections.append(section_entry)
        
        return extracted_sections
    
    def _generate_subsection_analysis(self, subsections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate subsection analysis list."""
        subsection_analysis = []
        
        for subsection in subsections:
            analysis_entry = {
                "document": subsection.get('document', 'unknown.pdf'),
                "refined_text": subsection.get('refined_text', ''),
                "page_number": subsection.get('page_number', 1)
            }
            
            # Add optional fields if available
            if 'analysis_method' in subsection:
                analysis_entry["analysis_method"] = subsection['analysis_method']
            
            if 'relevance_score' in subsection:
                analysis_entry["relevance_score"] = round(subsection['relevance_score'], 3)
            
            subsection_analysis.append(analysis_entry)
        
        return subsection_analysis
    
    def save_output(self, output_data: Dict[str, Any], output_path: str) -> bool:
        """
        Save output data to JSON file.
        
        Args:
            output_data: Generated output data
            output_path: Path to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Output saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving output to {output_path}: {str(e)}")
            return False
    
    def validate_output_format(self, output_data: Dict[str, Any]) -> tuple:
        """
        Validate output format against requirements.
        
        Args:
            output_data: Generated output data
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required top-level fields
        required_fields = ['metadata', 'extracted_sections', 'subsection_analysis']
        for field in required_fields:
            if field not in output_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate metadata
        if 'metadata' in output_data:
            metadata = output_data['metadata']
            required_metadata = ['input_documents', 'persona', 'job_to_be_done', 'processing_timestamp']
            
            for field in required_metadata:
                if field not in metadata:
                    errors.append(f"Missing required metadata field: {field}")
        
        # Validate extracted sections
        if 'extracted_sections' in output_data:
            sections = output_data['extracted_sections']
            if not isinstance(sections, list):
                errors.append("extracted_sections must be a list")
            else:
                for i, section in enumerate(sections):
                    required_section_fields = ['document', 'section_title', 'importance_rank', 'page_number']
                    for field in required_section_fields:
                        if field not in section:
                            errors.append(f"Missing field '{field}' in extracted_sections[{i}]")
        
        # Validate subsection analysis
        if 'subsection_analysis' in output_data:
            subsections = output_data['subsection_analysis']
            if not isinstance(subsections, list):
                errors.append("subsection_analysis must be a list")
            else:
                for i, subsection in enumerate(subsections):
                    required_subsection_fields = ['document', 'refined_text', 'page_number']
                    for field in required_subsection_fields:
                        if field not in subsection:
                            errors.append(f"Missing field '{field}' in subsection_analysis[{i}]")
        
        is_valid = len(errors) == 0
        return is_valid, errors
