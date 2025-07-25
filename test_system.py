# Test Script for Document Intelligence System
# Tests the system with example inputs

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from main import DocumentIntelligenceSystem

def create_test_pdf(content: str, filename: str) -> str:
    """Create a simple test PDF file with given content."""
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open()  # Create new PDF
        page = doc.new_page()
        
        # Insert text
        text_rect = fitz.Rect(50, 50, 500, 750)
        page.insert_textbox(text_rect, content, fontsize=12)
        
        doc.save(filename)
        doc.close()
        
        return filename
    except ImportError:
        print("PyMuPDF not installed. Cannot create test PDFs.")
        return None

def test_system():
    """Test the document intelligence system."""
    print("Testing Adobe Challenge 1B Document Intelligence System")
    print("=" * 60)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        
        input_dir.mkdir()
        output_dir.mkdir()
        
        # Create test PDF content
        test_content = """
        Introduction to Machine Learning
        
        Machine learning is a subset of artificial intelligence that focuses on 
        algorithms that can learn and make predictions from data. This field has 
        grown significantly in recent years.
        
        Methodology
        
        Our research methodology involves collecting data from various sources,
        preprocessing the information, and applying different machine learning
        algorithms to analyze patterns and trends.
        
        Results and Analysis
        
        The results show significant improvements in accuracy when using deep
        learning approaches compared to traditional methods. Performance metrics
        indicate a 15% increase in precision and 12% improvement in recall.
        
        Conclusion
        
        This study demonstrates the effectiveness of modern machine learning
        techniques in solving complex data analysis problems.
        """
        
        # Create test PDF
        pdf_path = input_dir / "test_document.pdf"
        if create_test_pdf(test_content, str(pdf_path)):
            print(f"✓ Created test PDF: {pdf_path}")
        else:
            print("✗ Failed to create test PDF")
            return False
        
        # Create test input configuration
        test_input = {
            "challenge_info": {
                "challenge_id": "test_case",
                "test_case_name": "academic_test",
                "description": "Test case for academic research"
            },
            "documents": ["test_document.pdf"],
            "persona": {
                "role": "PhD Student"
            },
            "job_to_be_done": {
                "task": "Analyze machine learning research methodologies and results"
            }
        }
        
        # Save input configuration
        input_config_path = input_dir / "input.json"
        with open(input_config_path, 'w') as f:
            json.dump(test_input, f, indent=2)
        
        print(f"✓ Created test input: {input_config_path}")
        
        # Initialize and test the system
        try:
            system = DocumentIntelligenceSystem()
            print("✓ System initialized successfully")
            
            # Run processing
            result = system.process_collection(str(input_dir), str(output_dir))
            
            if result['status'] == 'success':
                print(f"✓ Processing completed successfully!")
                print(f"  - Processing time: {result['processing_time']:.2f} seconds")
                print(f"  - Sections extracted: {result['sections_extracted']}")
                print(f"  - Subsections analyzed: {result['subsections_analyzed']}")
                
                # Validate output
                output_path = Path(result['output_path'])
                if output_path.exists():
                    with open(output_path, 'r') as f:
                        output_data = json.load(f)
                    
                    print(f"✓ Output file created: {output_path}")
                    print(f"  - Metadata fields: {list(output_data.get('metadata', {}).keys())}")
                    print(f"  - Extracted sections: {len(output_data.get('extracted_sections', []))}")
                    print(f"  - Subsection analyses: {len(output_data.get('subsection_analysis', []))}")
                    
                    return True
                else:
                    print("✗ Output file not found")
                    return False
            else:
                print(f"✗ Processing failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"✗ System test failed: {str(e)}")
            return False

def main():
    """Main test function."""
    try:
        success = test_system()
        if success:
            print("\n🎉 All tests passed! System is ready for deployment.")
        else:
            print("\n❌ Tests failed. Please check the implementation.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
