@echo off
echo Adobe Challenge 1B - Document Intelligence System
echo ================================================

echo.
echo Checking Python installation...
python --version
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); print('NLTK data downloaded')"

echo.
echo Creating output directory...
if not exist "output" mkdir output

echo.
echo Testing system...
python test_system.py

echo.
echo Setup completed!
echo.
echo Next steps:
echo 1. Run: python main.py --input ./examples --output ./output
echo 2. Build Docker: docker build -t adobe-challenge-1b .
echo 3. Run Docker: docker run --rm -v %CD%/examples:/app/input -v %CD%/output:/app/output --network none adobe-challenge-1b

pause
