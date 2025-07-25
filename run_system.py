#!/usr/bin/env python3
"""
Simple test runner for the document intelligence system
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def run_system():
    """Run the document intelligence system with current input/output setup."""
    
    print("🚀 Running Document Intelligence System")
    print("=" * 50)
    
    # Check input directory
    input_dir = Path("input")
    output_dir = Path("output")
    
    print(f"📁 Input directory: {input_dir}")
    print(f"📁 Output directory: {output_dir}")
    
    # List input files
    input_files = list(input_dir.glob("*"))
    print(f"📄 Found {len(input_files)} input files:")
    for file in input_files:
        print(f"  - {file.name}")
    
    # Try to import and run the main system
    try:
        from main import DocumentIntelligenceSystem
        
        print("\n⚡ Initializing system...")
        system = DocumentIntelligenceSystem()
        
        print("🔄 Processing documents...")
        result = system.process_collection(str(input_dir), str(output_dir))
        
        print(f"\n✅ Processing completed!")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Processing time: {result.get('processing_time', 0):.2f} seconds")
        print(f"Output file: {result.get('output_path', 'unknown')}")
        
        # Check output
        output_files = list(output_dir.glob("*.json"))
        print(f"\n📋 Generated {len(output_files)} output files:")
        for file in output_files:
            print(f"  - {file.name} ({file.stat().st_size} bytes)")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Error running system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_system()
    if success:
        print("\n🎉 System run completed successfully!")
    else:
        print("\n💥 System run failed!")
        sys.exit(1)
