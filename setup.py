#!/usr/bin/env python3
"""
Setup script for Adobe Challenge 1B Document Intelligence System
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def setup_environment():
    """Set up the development environment."""
    print("Adobe Challenge 1B - Document Intelligence System Setup")
    print("=" * 60)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return False
    
    print("✓ Python version is compatible")
    
    # Install dependencies
    print("\\nInstalling dependencies...")
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                      "Installing Python packages"):
        return False
    
    # Download NLTK data
    print("\\nDownloading NLTK data...")
    nltk_setup = """
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    print('✓ NLTK data downloaded successfully')
except Exception as e:
    print(f'✗ NLTK download failed: {e}')
"""
    
    if not run_command(f"{sys.executable} -c \"{nltk_setup}\"", 
                      "Downloading NLTK data"):
        print("Warning: NLTK data download failed, but continuing...")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Created output directory: {output_dir}")
    
    # Test basic imports
    print("\\nTesting imports...")
    test_imports = """
try:
    import fitz
    import nltk
    import numpy as np
    print('✓ All imports successful')
except ImportError as e:
    print(f'✗ Import failed: {e}')
    exit(1)
"""
    
    if not run_command(f"{sys.executable} -c \"{test_imports}\"", 
                      "Testing imports"):
        return False
    
    print("\\n🎉 Setup completed successfully!")
    print("\\nNext steps:")
    print("1. Run the test system: python test_system.py")
    print("2. Try with examples: python main.py --input ./examples --output ./output")
    print("3. Build Docker image: docker build -t adobe-challenge-1b .")
    
    return True

def main():
    """Main setup function."""
    try:
        success = setup_environment()
        if not success:
            print("\\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\\n⏹️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n💥 Unexpected error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
