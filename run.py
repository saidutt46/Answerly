"""
Run script for QA application.
Ensures environment is properly configured before starting the server.
"""
import os
import sys
import subprocess
from setup_platform import configure_environment

def run_server():
    """Configure environment and run the FastAPI server."""
    # Configure platform settings
    platform_info = configure_environment()
    print(f"Running with device: {platform_info['device']}")
    
    # Start the server
    subprocess.call([
        sys.executable, "-m", "uvicorn", "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])

if __name__ == "__main__":
    run_server()