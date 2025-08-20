@echo off
REM Installation script for AWS Billing Dashboard (Windows)

echo 🚀 Installing AWS Billing Dashboard
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set python_version=%%i
echo ✅ Python %python_version% detected

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Run tests
echo 🧪 Running tests...
python run_tests.py

echo.
echo ✅ Installation complete!
echo.
echo To run the dashboard:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Configure AWS credentials: aws configure
echo 3. Run the app: streamlit run app.py

pause