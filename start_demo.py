#!/usr/bin/env python3
"""
Startup script for AWS Billing Dashboard Demo
"""
import subprocess
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """Open browser after a delay"""
    time.sleep(3)  # Wait 3 seconds for server to start
    webbrowser.open('http://localhost:8501')

def main():
    print("🚀 Starting AWS Billing Dashboard Demo")
    print("=" * 50)
    print("📊 Demo Features:")
    print("  • Interactive cost trend charts")
    print("  • Service cost breakdown")
    print("  • Month-over-month analysis")
    print("  • Sample data (no AWS credentials needed)")
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
            sys.executable, "-m", "streamlit", "run", "demo.py",
            "--server.headless", "true",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n👋 Demo stopped. Thanks for trying the AWS Billing Dashboard!")

if __name__ == "__main__":
    main()