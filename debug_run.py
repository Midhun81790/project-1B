#!/usr/bin/env python3
"""
Debug runner for the Document Intelligence System
Provides detailed step-by-step output to troubleshoot processing issues
"""

import json
import sys
import traceback
from pathlib import Path

print("🔍 Debug Runner for Document Intelligence System")
print("=" * 60)

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("📦 Importing modules...")
    from main import DocumentIntelligenceSystem
    print("✅ Successfully imported DocumentIntelligenceSystem")
    
    # Initialize the system
    print("\n🚀 Initializing system...")
    system = DocumentIntelligenceSystem()
    print("✅ System initialized successfully")
    
    # Check input directory
    input_dir = "input"
    output_dir = "output"
    
    print(f"\n📁 Checking directories...")
    print(f"   Input dir: {Path(input_dir).absolute()}")
    print(f"   Output dir: {Path(output_dir).absolute()}")
    
    if not Path(input_dir).exists():
        print(f"❌ Input directory does not exist: {input_dir}")
        sys.exit(1)
    
    # List input files
    input_files = list(Path(input_dir).iterdir())
    print(f"\n📄 Found {len(input_files)} files in input directory:")
    for file in input_files:
        print(f"   - {file.name} ({file.stat().st_size} bytes)")
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"\n🔄 Starting document processing...")
    result = system.process_collection(input_dir, output_dir)
    
    print(f"\n📊 Processing Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
        print(f"   Output path: {result.get('output_path', 'unknown')}")
        print(f"   Sections extracted: {result.get('sections_extracted', 0)}")
        print(f"   Subsections analyzed: {result.get('subsections_analyzed', 0)}")
    else:
        print(f"   Error: {result.get('error', 'unknown error')}")
    
    # Check output directory
    print(f"\n📁 Checking output directory...")
    output_files = list(Path(output_dir).iterdir())
    print(f"   Found {len(output_files)} files:")
    for file in output_files:
        print(f"   - {file.name} ({file.stat().st_size} bytes)")
        
    print(f"\n✅ Debug run completed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Checking if all modules are available...")
    
    modules_to_check = [
        "src.pdf_processor",
        "src.text_analyzer", 
        "src.persona_matcher",
        "src.section_ranker",
        "src.output_generator"
    ]
    
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as import_err:
            print(f"   ❌ {module}: {import_err}")
            
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"📍 Error details:")
    traceback.print_exc()
