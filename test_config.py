"""Test configuration module."""
from config import settings

def test_config():
    """Test configuration loading."""
    print("Available models:")
    for name, model_id in settings.MODELS.items():
        print(f"- {name}: {model_id}")
    print(f"Default model: {settings.DEFAULT_MODEL}")
    print(f"Upload directory: {settings.UPLOAD_DIR}")

if __name__ == "__main__":
    test_config()