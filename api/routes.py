"""
API routes for the QA application.
"""
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models.model_manager import ModelManager
from processing.file_handler import FileHandler
from processing.pdf_extractor import PDFExtractor
from processing.text_processor import TextProcessor
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize model manager
model_manager = ModelManager()

# Request and response models
class QARequest(BaseModel):
    """Request model for QA endpoint with text input."""
    question: str
    context: str
    model_name: str = settings.DEFAULT_MODEL

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

@router.get("/models", response_model=ModelsResponse)
async def get_available_models():
    """Get list of available models with metadata."""
    models_info = model_manager.get_available_models()
    return {"models": models_info, "default_model": settings.DEFAULT_MODEL}

@router.post("/qa", response_model=QAResponse)
async def question_answering(qa_request: QARequest):
    """
    Answer a question based on provided context.
    
    Args:
        qa_request: Question, context and model selection
        
    Returns:
        Answer with metadata
    """
    logger.info(f"QA request received with model: {qa_request.model_name}")
    
    # Clean the input text
    clean_context = TextProcessor.clean_text(qa_request.context)
    
    # Check if context is too long for model
    if len(clean_context.split()) > settings.MAX_SEQ_LENGTH - 50:  # Leave room for question
        # Chunk the context
        chunks = TextProcessor.chunk_text(clean_context)
        logger.info(f"Context too long, split into {len(chunks)} chunks")
        
        # TODO: Implement proper chunking strategy with aggregation
        # For now, use just the first chunk
        clean_context = chunks[0]["text"] if chunks else clean_context
    
    # Get answer from model
    try:
        result = model_manager.answer_question(
            question=qa_request.question,
            context=clean_context,
            model_name=qa_request.model_name
        )
        return result
    except Exception as e:
        logger.error(f"Error processing QA request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=QAResponse)
async def upload_file_qa(
    file: UploadFile = File(...),
    question: str = Form(...),
    model_name: str = Form(settings.DEFAULT_MODEL)
):
    """
    Process an uploaded file and answer a question.
    
    Args:
        file: Uploaded file (PDF or text)
        question: Question to answer
        model_name: Model to use
        
    Returns:
        Answer with metadata
    """
    logger.info(f"File upload received: {file.filename}")
    
    try:
        # Save the uploaded file
        file_path, extension = await FileHandler.save_upload(file)
        
        # Extract text based on file type
        if extension.lower() == '.pdf':
            extracted_text = PDFExtractor.extract_text(file_path)
        else:  # Assume text file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                extracted_text = f.read()
        
        # Clean the extracted text
        clean_text = TextProcessor.clean_text(extracted_text)
        
        # Check if text is too long and chunk if needed
        if len(clean_text.split()) > settings.MAX_SEQ_LENGTH - 50:
            chunks = TextProcessor.chunk_text(clean_text)
            logger.info(f"Extracted text too long, split into {len(chunks)} chunks")
            
            # TODO: Implement proper chunking strategy
            # For now, use just the first chunk
            clean_text = chunks[0]["text"] if chunks else clean_text
        
        # Get answer from model
        result = model_manager.answer_question(
            question=question,
            context=clean_text,
            model_name=model_name
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing file upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))