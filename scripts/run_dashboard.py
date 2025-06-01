#!/usr/bin/env python3
"""
Utility script to run the Streamlit dashboard locally
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit dashboard"""
    
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("Error: Streamlit is not installed. Please run: pip install streamlit")
        sys.exit(1)
    
    # Set environment variables if .env file exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"Loading environment from {env_file}")
        # You could use python-dotenv here, but for simplicity we'll just remind the user
        print("Make sure your .env file is properly configured with MongoDB and other settings")
    else:
        print("Warning: .env file not found. Please create one from env.example")
    
    # Run streamlit
    print("Starting Streamlit dashboard...")
    print("Dashboard will be available at: http://localhost:8501")
    print("Default password: admin123 (configurable via STREAMLIT_PASSWORD)")

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.address", "0.0.0.0",
            "--server.port", "8501"
        ], check=True)
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error running dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 