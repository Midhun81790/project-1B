@echo off
REM Adobe Challenge 1B - Universal Quick Setup Script for Windows
REM Works on Windows PowerShell and Command Prompt

echo 🚀 Adobe India Hackathon Challenge 1B - Quick Setup
echo ==================================================

REM Check if we're already in the project directory
if exist "main.py" if exist "requirements.txt" (
    echo ✅ Already in project directory
) else (
    echo 📥 Cloning repository...
    git clone https://github.com/Midhun81790/project-1B.git
    cd project-1B
)

echo 📦 Installing dependencies...
python -m pip install -r requirements.txt

echo 🧪 Testing system...
python test_imports.py

echo 🎯 Running document intelligence system...
python main.py --input .\input --output .\output

echo.
echo ✅ Setup complete! Your results are in the .\output folder
echo 🌐 Repository: https://github.com/Midhun81790/project-1B
echo 📖 Full documentation: See README.md and USAGE.md
pause
