#!/usr/bin/env python3
"""
Direct execution script for document intelligence system
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Direct execution of the document intelligence system."""
    
    print("🚀 Document Intelligence System - Direct Execution")
    print("=" * 60)
    
    input_dir = Path("input")
    output_dir = Path("output")
    
    # Import system components
    from main import DocumentIntelligenceSystem
    
    try:
        # Initialize system
        print("⚡ Initializing system components...")
        system = DocumentIntelligenceSystem()
        
        # Run processing
        print("🔄 Starting document processing...")
        result = system.process_collection(str(input_dir), str(output_dir))
        
        print("\n📊 Processing Results:")
        print(f"Status: {result.get('status')}")
        print(f"Processing time: {result.get('processing_time', 0):.2f} seconds")
        print(f"Sections extracted: {result.get('sections_extracted', 0)}")
        print(f"Subsections analyzed: {result.get('subsections_analyzed', 0)}")
        print(f"Output file: {result.get('output_path')}")
        
        # Verify output
        if result.get('status') == 'success':
            output_path = Path(result.get('output_path'))
            if output_path.exists():
                with open(output_path, 'r', encoding='utf-8') as f:
                    output_data = json.load(f)
                
                print(f"\n✅ Output file created successfully!")
                print(f"📋 Output structure:")
                print(f"  - Metadata fields: {len(output_data.get('metadata', {}))}")
                print(f"  - Extracted sections: {len(output_data.get('extracted_sections', []))}")
                print(f"  - Subsection analyses: {len(output_data.get('subsection_analysis', []))}")
                
                # Show sample section
                sections = output_data.get('extracted_sections', [])
                if sections:
                    print(f"\n📖 Sample section (rank {sections[0].get('importance_rank', 'N/A')}):")
                    print(f"  Title: {sections[0].get('section_title', 'N/A')}")
                    print(f"  Document: {sections[0].get('document', 'N/A')}")
                    print(f"  Relevance: {sections[0].get('relevance_score', 'N/A'):.3f}")
                
                return True
            else:
                print("❌ Output file was not created")
                return False
        else:
            print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"💥 System execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Document processing completed successfully!")
        print("📁 Check the output directory for generated results.")
    else:
        print("\n❌ Document processing failed.")
        sys.exit(1)
