#!/bin/bash
# Installation script for AWS Billing Dashboard

set -e

echo "🚀 Installing AWS Billing Dashboard"
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
python run_tests.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "To run the dashboard:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Configure AWS credentials: aws configure"
echo "3. Run the app: streamlit run app.py"