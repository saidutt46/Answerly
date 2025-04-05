"""
File handling utilities for QA application.
Handles file uploads, validation, and storage.
"""
import os
import uuid
import logging
from pathlib import Path
from typing import Tuple, List, Optional
from fastapi import UploadFile, HTTPException
from config import settings

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles file operations for the QA application."""
    
    @staticmethod
    async def save_upload(upload_file: UploadFile) -> Tuple[str, str]:
        """
        Save an uploaded file to disk.
        
        Args:
            upload_file: The uploaded file object
            
        Returns:
            Tuple containing (file_path, file_extension)
            
        Raises:
            HTTPException: If file validation fails
        """
        # Validate file
        FileHandler._validate_file(upload_file)
        
        # Generate unique filename to prevent collisions
        original_filename = upload_file.filename
        extension = os.path.splitext(original_filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{extension}"
        
        # Create full file path
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save file
        try:
            contents = await upload_file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
            
            logger.info(f"File saved: {file_path} (Original: {original_filename})")
            return file_path, extension
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to save uploaded file"
            )
    
    @staticmethod
    def _validate_file(upload_file: UploadFile) -> None:
        """
        Validate the uploaded file.
        
        Args:
            upload_file: The uploaded file object
            
        Raises:
            HTTPException: If validation fails
        """
        # Check if file provided
        if not upload_file.filename:
            raise HTTPException(
                status_code=400, 
                detail="No file provided"
            )
        
        # Check file extension
        file_ext = os.path.splitext(upload_file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size by reading content length header
        content_length = 0
        if upload_file.headers and "content-length" in upload_file.headers:
            content_length = int(upload_file.headers["content-length"])
        
        if content_length > settings.MAX_UPLOAD_SIZE:
            max_size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {max_size_mb:.1f}MB"
            )
    
    @staticmethod
    def clean_old_files(max_age_hours: int = 24) -> None:
        """
        Remove old uploaded files to free up disk space.
        
        Args:
            max_age_hours: Maximum age of files in hours before deletion
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            # Get list of files in upload directory
            for filename in os.listdir(settings.UPLOAD_DIR):
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                
                # Check if it's a file (not a directory)
                if os.path.isfile(file_path):
                    # Get file modification time
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    # Remove if older than max age
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        logger.info(f"Removed old file: {file_path}")
                        
        except Exception as e:
            logger.error(f"Error cleaning old files: {e}")