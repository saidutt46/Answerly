"""Platform detection and configuration for ML environment."""
import platform
import subprocess
import sys
import os

def configure_environment():
    """
    Configure the environment based on the detected platform.
    Returns information about the platform setup.
    """
    system = platform.system()
    machine = platform.machine()
    
    print(f"Detected platform: {system} on {machine}")
    
    if system == "Darwin" and machine in ["arm64", "M1", "M2"]:
        print("Apple Silicon (M1/M2) Mac detected")
        
        # Set environment variables for Apple Silicon
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
        
        # Check if PyTorch is installed with MPS support
        try:
            import torch
            if torch.backends.mps.is_available():
                print("MPS (Metal Performance Shaders) is available for acceleration")
                os.environ["DEVICE"] = "mps"
            else:
                print("MPS not available, using CPU")
                os.environ["DEVICE"] = "cpu"
        except (ImportError, AttributeError):
            print("PyTorch not installed or MPS not supported in this version")
            print("Installing PyTorch with MPS support...")
            
            # Install PyTorch with MPS support
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "torch", "torchvision", 
                "--index-url", "https://download.pytorch.org/whl/nightly/cpu"
            ])
            
            os.environ["DEVICE"] = "cpu"  # Default to CPU after install
            
    elif system == "Linux":
        print("Linux detected")
        # Check for CUDA
        try:
            import torch
            if torch.cuda.is_available():
                print(f"CUDA available: {torch.cuda.get_device_name(0)}")
                os.environ["DEVICE"] = "cuda"
            else:
                print("CUDA not available, using CPU")
                os.environ["DEVICE"] = "cpu"
        except ImportError:
            print("PyTorch not installed")
            os.environ["DEVICE"] = "cpu"
    else:
        # Windows or other platforms
        os.environ["DEVICE"] = "cpu"
        
    return {
        "system": system,
        "machine": machine,
        "device": os.environ.get("DEVICE", "cpu")
    }

if __name__ == "__main__":
    # When run directly, configure and print status
    platform_info = configure_environment()
    print("\nPlatform configuration complete:")
    for key, value in platform_info.items():
        print(f"  {key}: {value}")