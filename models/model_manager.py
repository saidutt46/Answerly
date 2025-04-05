"""
Model manager for loading and using Hugging Face QA models.
"""
import os
import time
import logging
from typing import Dict, Any, List, Optional, Tuple

from setup_platform import configure_environment

# Configure platform-specific settings
platform_info = configure_environment()
device_name = platform_info["device"]

import torch
from transformers import (
    AutoModelForQuestionAnswering, 
    AutoTokenizer,
    pipeline
)
from config import settings

logger = logging.getLogger(__name__)

class ModelManager:
    """Manager for Hugging Face QA models."""
    
    def __init__(self):
        """Initialize model manager."""
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        self.model_info = {}
        self.device = device_name

        logger.info(f"Model manager initialized with device: {self.device}")
        
        # Load model metadata
        self._load_model_metadata()
        
        # Preload default model if specified
        if settings.DEFAULT_MODEL:
            logger.info(f"Preloading default model: {settings.DEFAULT_MODEL}")
            self._load_model(settings.DEFAULT_MODEL)

    def _load_model_metadata(self):
        """Load metadata for available models."""
        for name, model_id in settings.MODELS.items():
            # Basic info about each model
            self.model_info[model_id] = {
                "name": name,
                "model_id": model_id,
                "is_loaded": False,
                "description": self._get_model_description(name, model_id)
            }
            
    def _get_model_description(self, name: str, model_id: str) -> str:
        """Get description for a model."""
        descriptions = {
            "distilbert-base-uncased-distilled-squad": 
                "A lightweight and fast model distilled from BERT. Good balance of speed and accuracy.",
            
            "deepset/roberta-base-squad2": 
                "Based on RoBERTa, optimized for SQuAD 2.0. Handles unanswerable questions well.",
            
            "bert-large-uncased-whole-word-masking-finetuned-squad":
                "Large BERT model with whole word masking. High accuracy but slower inference.",
            
            "google/electra-small-discriminator":
                "Small and efficient ELECTRA model. Faster than BERT with comparable performance."
        }
        
        return descriptions.get(model_id, f"A QA model based on {model_id.split('/')[-1].split('-')[0].upper()}")

    def _load_model(self, model_id: str) -> Tuple[Any, Any, Any]:
        """
        Load a model and its tokenizer.
        
        Args:
            model_id: Hugging Face model identifier
            
        Returns:
            Tuple of (model, tokenizer, pipeline)
        """
        if model_id in self.pipelines:
            return self.models[model_id], self.tokenizers[model_id], self.pipelines[model_id]
        
        logger.info(f"Loading model: {model_id}")
        
        try:
            # Set up device based on platform detection
            if self.device == "cuda":
                device = 0  # First CUDA device
            elif self.device == "mps":
                device = "mps"  # Apple Metal
            else:
                device = -1  # CPU
                
            logger.info(f"Using device: {self.device}")
            
            # Load from cache directory if specified
            cache_dir = settings.MODEL_CACHE_DIR
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)
            model = AutoModelForQuestionAnswering.from_pretrained(model_id, cache_dir=cache_dir)
            
            # Create pipeline with appropriate device
            qa_pipeline = pipeline(
                "question-answering",
                model=model,
                tokenizer=tokenizer,
                device=device
            )
            
            # Store in memory
            self.models[model_id] = model
            self.tokenizers[model_id] = tokenizer
            self.pipelines[model_id] = qa_pipeline
            
            # Update metadata
            if model_id in self.model_info:
                self.model_info[model_id]["is_loaded"] = True
            
            return model, tokenizer, qa_pipeline
            
        except Exception as e:
            logger.error(f"Error loading model {model_id}: {e}")
            
            # For M1 Mac with NumPy issues, provide more specific error
            if "NumPy is not available" in str(e):
                logger.error("NumPy compatibility issue detected with PyTorch.")
                logger.error("Try running: pip install numpy==1.24.3")
                
            raise RuntimeError(f"Failed to load model {model_id}: {e}")

    def answer_question(self, question: str, context: str, model_name: str = None) -> Dict[str, Any]:
        """
        Get answer for a question given context.
        
        Args:
            question: The question to answer
            context: Text context to find answer in
            model_name: Model to use (default will be used if None)
            
        Returns:
            Dict with answer and metadata
        """
        # Use default model if none specified
        if not model_name:
            model_name = settings.DEFAULT_MODEL
            
        # Get model from list of available models if display name is used
        if model_name in settings.MODELS:
            model_name = settings.MODELS[model_name]
            
        # Load model if not already loaded
        _, _, qa_pipeline = self._load_model(model_name)
        
        # Measure processing time
        start_time = time.time()
        
        # Get answer
        try:
            result = qa_pipeline(
                question=question,
                context=context,
                handle_impossible_answer=True,
                max_answer_len=100,
                max_seq_len=settings.MAX_SEQ_LENGTH,
                truncation=True
            )
            
            processing_time = time.time() - start_time
            
            # Format response
            response = {
                "answer": result["answer"],
                "confidence": result["score"],
                "context": context,
                "model_used": model_name,
                "processing_time": processing_time
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting answer: {e}")
            raise RuntimeError(f"Failed to get answer: {e}")
            
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available models.
        
        Returns:
            Dict with model information
        """
        return self.model_info
        
    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model from memory.
        
        Args:
            model_id: Model ID to unload
            
        Returns:
            True if successful
        """
        if model_id in self.models:
            try:
                # Remove from dictionaries
                del self.models[model_id]
                del self.tokenizers[model_id]
                del self.pipelines[model_id]
                
                # Update metadata
                if model_id in self.model_info:
                    self.model_info[model_id]["is_loaded"] = False
                    
                # Force garbage collection
                import gc
                gc.collect()
                
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
                logger.info(f"Unloaded model: {model_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error unloading model {model_id}: {e}")
                
        return False