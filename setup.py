"""
Setup script for QA application.
Ensures correct dependencies are installed for the current platform.
"""
import platform
import subprocess
import sys
import os

def setup_environment():
    """Set up dependencies based on platform."""
    system = platform.system()
    machine = platform.machine()
    
    print(f"Setting up environment for {system} on {machine}...")
    
    # Install base requirements
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
    ])
    
    # Platform-specific setup
    if system == "Darwin" and machine in ["arm64", "M1", "M2"]:
        print("Setting up for Apple Silicon...")
        
        # Uninstall existing torch if any
        subprocess.call([
            sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision"
        ])
        
        # Install Apple Silicon optimized PyTorch
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "torch", "torchvision",
            "--extra-index-url", "https://download.pytorch.org/whl/nightly/cpu"
        ])
        
        # Fix numpy version (1.24.3 is known to work with PyTorch on M1)
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "numpy==1.24.3", "--force-reinstall"
        ])
        
    elif system == "Linux":
        # Check if CUDA is available
        try:
            import torch
            if not torch.cuda.is_available():
                print("CUDA not detected, installing CPU version of PyTorch")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "torch", "torchvision",
                    "--index-url", "https://download.pytorch.org/whl/cpu"
                ])
        except ImportError:
            print("Installing CPU version of PyTorch")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "torch", "torchvision",
                "--index-url", "https://download.pytorch.org/whl/cpu"
            ])
    
    # Download NLTK data
    print("Downloading NLTK data...")
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    import nltk
    nltk.download('punkt')
    
    print("Setup complete!")

if __name__ == "__main__":
    setup_environment()