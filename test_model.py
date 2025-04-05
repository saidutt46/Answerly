"""Test model loading and inference."""
from models.model_manager import ModelManager

def test_model_loading():
    """Test model loading and basic inference."""
    # Initialize model manager
    model_manager = ModelManager()
    
    # Get available models
    models_info = model_manager.get_available_models()
    print("Available models:")
    for model_id, info in models_info.items():
        print(f"- {info['name']} ({model_id})")
    
    # Test inference with a simple example
    question = "What is Python?"
    context = "Python is a programming language. It was created by Guido van Rossum."
    
    print("\nTesting inference:")
    print(f"Question: {question}")
    print(f"Context: {context}")
    
    result = model_manager.answer_question(question, context)
    print("\nResult:")
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']:.4f}")
    print(f"Model used: {result['model_used']}")
    print(f"Processing time: {result['processing_time']:.4f} seconds")

if __name__ == "__main__":
    test_model_loading()