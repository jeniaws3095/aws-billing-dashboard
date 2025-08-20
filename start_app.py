#!/usr/bin/env python3
"""
Startup script for AWS Billing Dashboard (with real AWS data)
"""
import subprocess
import sys
import webbrowser
import time
from threading import Timer
import os

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    if aws_access_key and aws_secret_key:
        return True
    
    # Check for AWS CLI credentials file
    aws_credentials_path = os.path.expanduser('~/.aws/credentials')
    if os.path.exists(aws_credentials_path):
        return True
    
    return False

def open_browser():
    """Open browser after a delay"""
    time.sleep(3)  # Wait 3 seconds for server to start
    webbrowser.open('http://localhost:8501')

def main():
    print("🚀 Starting AWS Billing Dashboard")
    print("=" * 50)
    
    # Check AWS credentials
    if not check_aws_credentials():
        print("⚠️  AWS Credentials Not Found")
        print()
        print("To use real AWS data, please configure your credentials:")
        print("  1. Run: aws configure")
        print("  2. Or set environment variables:")
        print("     - AWS_ACCESS_KEY_ID")
        print("     - AWS_SECRET_ACCESS_KEY")
        print("     - AWS_DEFAULT_REGION")
        print()
        print("💡 To try the demo with sample data instead:")
        print("   python start_demo.py")
        print()
        return
    
    print("✅ AWS credentials found!")
    print()
    print("📊 Dashboard Features:")
    print("  • Real-time AWS cost data")
    print("  • Interactive cost trend charts")
    print("  • Service cost breakdown")
    print("  • Month-over-month analysis")
    print("  • Data export capabilities")
    print()
    print("🌐 The dashboard will open in your browser automatically")
    print("📍 URL: http://localhost:8501")
    print()
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start browser opener in background
    Timer(3.0, open_browser).start()
    
    try:
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "true",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thanks for using the AWS Billing Dashboard!")

if __name__ == "__main__":
    main()