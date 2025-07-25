# Multi-Collection PDF Document Intelligence System
# Adobe India Hackathon 2025 - Challenge 1B

import json
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
import argparse

# Core modules
from src.pdf_processor import PDFProcessor
from src.text_analyzer import TextAnalyzer
from src.persona_matcher import PersonaMatcher
from src.section_ranker import SectionRanker
from src.output_generator import OutputGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentIntelligenceSystem:
    """
    Main system for persona-driven document intelligence.
    Extracts and ranks relevant sections from PDF collections.
    """
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.text_analyzer = TextAnalyzer()
        self.persona_matcher = PersonaMatcher()
        self.section_ranker = SectionRanker()
        self.output_generator = OutputGenerator()
        
    def process_collection(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """
        Process a complete document collection.
        
        Args:
            input_dir: Directory containing input.json and PDF files
            output_dir: Directory for output files
            
        Returns:
            Processing results dictionary
        """
        start_time = time.time()
        
        try:
            # Load input configuration
            input_config = self._load_input_config(input_dir)
            
            # Extract text from all PDFs
            logger.info("Extracting text from PDF documents...")
            documents = self._extract_documents(input_dir, input_config['documents'])
            
            # Analyze persona and job requirements
            logger.info("Analyzing persona and job requirements...")
            persona_profile = self.persona_matcher.analyze_persona(
                input_config['persona'], 
                input_config['job_to_be_done']
            )
            
            # Extract and rank sections
            logger.info("Extracting and ranking relevant sections...")
            sections = self._extract_sections(documents, persona_profile)
            ranked_sections = self.section_ranker.rank_sections(sections, persona_profile)
            
            # Generate sub-section analysis
            logger.info("Generating sub-section analysis...")
            subsections = self._analyze_subsections(ranked_sections, persona_profile)
            
            # Generate output
            output_data = self.output_generator.generate_output(
                input_config, ranked_sections, subsections
            )
            
            # Save output
            output_path = Path(output_dir) / "output.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            processing_time = time.time() - start_time
            logger.info(f"Processing completed in {processing_time:.2f} seconds")
            
            return {
                'status': 'success',
                'processing_time': processing_time,
                'output_path': str(output_path),
                'sections_extracted': len(ranked_sections),
                'subsections_analyzed': len(subsections)
            }
            
        except Exception as e:
            logger.error(f"Error processing collection: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _load_input_config(self, input_dir: str) -> Dict[str, Any]:
        """Load and validate input configuration."""
        # Try multiple input file names based on expected formats
        possible_files = [
            "persona.json",           # Expected format from requirements
            "input.json",             # Alternative format
            "challenge1b_input.json", # GitHub repository format
            "input_academic.json",    # Our example formats
            "input_business.json", 
            "input_food.json"
        ]
        
        config = None
        input_path = None
        
        for filename in possible_files:
            potential_path = Path(input_dir) / filename
            if potential_path.exists():
                input_path = potential_path
                break
        
        if not input_path:
            raise FileNotFoundError(f"No input configuration found in {input_dir}. Tried: {possible_files}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info(f"Loaded input configuration from: {input_path.name}")
        
        # Handle different input formats
        if 'persona' in config and 'job_to_be_done' in config:
            # Standard format - either direct or nested
            if 'documents' not in config:
                # Auto-detect document files in input directory (PDF and text fallbacks)
                pdf_files = [f.name for f in Path(input_dir).glob("*.pdf")]
                txt_files = [f.name for f in Path(input_dir).glob("*.pdf.txt")]
                all_docs = pdf_files + txt_files
                config['documents'] = all_docs
                logger.info(f"Auto-detected {len(all_docs)} documents: {all_docs}")
        
        # Validate required fields
        required_fields = ['persona', 'job_to_be_done']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field in input: {field}")
        
        # Ensure documents field exists
        if 'documents' not in config or not config['documents']:
            # Auto-detect document files if not specified (PDF and text fallbacks)
            pdf_files = [f.name for f in Path(input_dir).glob("*.pdf")]
            txt_files = [f.name for f in Path(input_dir).glob("*.pdf.txt")]
            all_docs = pdf_files + txt_files
            if not all_docs:
                raise ValueError("No PDF or text documents found and no documents specified in configuration")
            config['documents'] = all_docs
            logger.info(f"Auto-detected documents: {all_docs}")
        
        return config
    
    def _extract_documents(self, input_dir: str, document_list: List[str]) -> List[Dict[str, Any]]:
        """Extract text content from PDF documents."""
        documents = []
        
        for doc_name in document_list:
            doc_path = Path(input_dir) / doc_name
            if not doc_path.exists():
                logger.warning(f"Document not found: {doc_path}")
                continue
            
            try:
                doc_content = self.pdf_processor.extract_text(str(doc_path))
                doc_content['name'] = doc_name
                documents.append(doc_content)
                logger.info(f"Processed document: {doc_name}")
            except Exception as e:
                logger.error(f"Error processing {doc_name}: {str(e)}")
                continue
        
        return documents
    
    def _extract_sections(self, documents: List[Dict[str, Any]], 
                         persona_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract relevant sections from documents."""
        all_sections = []
        
        for doc in documents:
            sections = self.text_analyzer.extract_sections(doc)
            
            # Score sections based on persona relevance
            for section in sections:
                relevance_score = self.persona_matcher.calculate_relevance(
                    section, persona_profile
                )
                section['relevance_score'] = relevance_score
                section['document_name'] = doc['name']
                all_sections.append(section)
        
        return all_sections
    
    def _analyze_subsections(self, sections: List[Dict[str, Any]], 
                           persona_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze and extract refined sub-sections."""
        subsections = []
        
        for section in sections[:10]:  # Top 10 sections
            sub_analysis = self.text_analyzer.analyze_subsections(
                section, persona_profile
            )
            subsections.extend(sub_analysis)
        
        return subsections

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='Adobe Hackathon Challenge 1B - Document Intelligence System'
    )
    parser.add_argument(
        '--input', 
        default='/app/input',
        help='Input directory containing PDFs and input.json'
    )
    parser.add_argument(
        '--output', 
        default='/app/output',
        help='Output directory for results'
    )
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Ensure output directory exists
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    # Initialize and run the system
    system = DocumentIntelligenceSystem()
    result = system.process_collection(args.input, args.output)
    
    if result['status'] == 'success':
        logger.info("Document intelligence processing completed successfully!")
        logger.info(f"Output saved to: {result['output_path']}")
    else:
        logger.error("Processing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
