"""
PDF text extraction utilities for QA application.
Extracts text content from PDF files.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Handles text extraction from PDF files with fallback to OCR."""
    
    @staticmethod
    def extract_text(pdf_path: str, use_ocr: bool = False) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            use_ocr: Whether to use OCR for all pages
            
        Returns:
            Extracted text as a string
        """
        logger.info(f"Extracting text from PDF: {pdf_path}")
        
        try:
            # Try using PyMuPDF first (usually faster and more accurate)
            if not use_ocr:
                extracted_text = PDFExtractor._extract_with_pymupdf(pdf_path)
                
                # If we got minimal text, fallback to OCR
                if len(extracted_text.strip()) < 100:
                    logger.info("Minimal text extracted, falling back to OCR")
                    extracted_text = PDFExtractor._extract_with_ocr(pdf_path)
                
                return extracted_text
            else:
                # Use OCR directly if specified
                return PDFExtractor._extract_with_ocr(pdf_path)
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise RuntimeError(f"Failed to extract text from PDF: {e}")
    
    @staticmethod
    def _extract_with_pymupdf(pdf_path: str) -> str:
        """
        Extract text from PDF using PyMuPDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        text_content = []
        
        # Open the PDF
        with fitz.open(pdf_path) as pdf_document:
            # Iterate through each page
            for page_num in range(len(pdf_document)):
                # Get the page
                page = pdf_document.load_page(page_num)
                
                # Extract text
                page_text = page.get_text("text")
                text_content.append(page_text)
        
        return "\n\n".join(text_content)
    
    @staticmethod
    def _extract_with_ocr(pdf_path: str) -> str:
        """
        Extract text from PDF using OCR (Tesseract).
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        text_content = []
        
        with fitz.open(pdf_path) as pdf_document:
            # Iterate through each page
            for page_num in range(len(pdf_document)):
                # Get the page
                page = pdf_document.load_page(page_num)
                
                # Render page to an image (higher resolution for better OCR)
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Perform OCR
                page_text = pytesseract.image_to_string(img, lang='eng')
                text_content.append(page_text)
        
        return "\n\n".join(text_content)

    @staticmethod
    def get_metadata(pdf_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing metadata
        """
        metadata = {}
        
        try:
            with fitz.open(pdf_path) as pdf_document:
                # Get basic document info
                metadata = {
                    "title": pdf_document.metadata.get("title", ""),
                    "author": pdf_document.metadata.get("author", ""),
                    "subject": pdf_document.metadata.get("subject", ""),
                    "keywords": pdf_document.metadata.get("keywords", ""),
                    "creator": pdf_document.metadata.get("creator", ""),
                    "producer": pdf_document.metadata.get("producer", ""),
                    "page_count": len(pdf_document),
                    "file_size_kb": os.path.getsize(pdf_path) / 1024
                }
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")
            
        return metadata