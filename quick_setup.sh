#!/bin/bash
# Adobe Challenge 1B - Universal Quick Setup Script
# Works on macOS, Linux, WSL, and most Unix-like systems

echo "🚀 Adobe India Hackathon Challenge 1B - Quick Setup"
echo "=================================================="

# Check if we're already in the project directory
if [ -f "main.py" ] && [ -f "requirements.txt" ]; then
    echo "✅ Already in project directory"
else
    echo "📥 Cloning repository..."
    git clone https://github.com/Midhun81790/project-1B.git
    cd project-1B
fi

echo "📦 Installing dependencies..."
python3 -m pip install -r requirements.txt

echo "🧪 Testing system..."
python3 test_imports.py

echo "🎯 Running document intelligence system..."
python3 main.py --input ./input --output ./output

echo ""
echo "✅ Setup complete! Your results are in the ./output folder"
echo "🌐 Repository: https://github.com/Midhun81790/project-1B"
echo "📖 Full documentation: See README.md and USAGE.md"
