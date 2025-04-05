"""Pydantic schemas for the API."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class QARequest(BaseModel):
    """Request model for QA endpoint with text input."""
    question: str
    context: str
    model_name: Optional[str] = None

class QAResponse(BaseModel):
    """Response model for QA answers."""
    answer: str
    confidence: float
    context: str
    model_used: str
    processing_time: float

class ModelsResponse(BaseModel):
    """Response model for available models."""
    models: Dict[str, Dict[str, Any]]
    default_model: str