"""
Text processing utilities for QA application.
Handles text cleaning, normalization, and chunking.
"""
import re
import logging
from typing import List, Dict, Tuple, Any, Optional
import nltk
from nltk.tokenize import sent_tokenize
from config import settings

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

logger = logging.getLogger(__name__)

class TextProcessor:
    """Text processing utilities for QA application."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
            
        # Replace multiple whitespace with single space
        cleaned = re.sub(r'\s+', ' ', text)
        
        # Replace multiple newlines with double newline
        cleaned = re.sub(r'\n+', '\n\n', cleaned)
        
        # Remove non-printable characters
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', cleaned)
        
        # Fix common OCR errors
        cleaned = cleaned.replace('l|', 'll')
        cleaned = cleaned.replace('|l', 'll')
        cleaned = cleaned.replace('|', 'I')
        
        # Replace unicode quotation marks with ASCII ones
        cleaned = cleaned.replace(''', "'").replace(''', "'")
        cleaned = cleaned.replace('"', '"').replace('"', '"')
        
        # Fix spacing around punctuation
        cleaned = re.sub(r'\s+([,.!?;:])', r'\1', cleaned)
        
        return cleaned.strip()
    
    @staticmethod
    def chunk_text(text: str, chunk_size: Optional[int] = None, 
                  chunk_overlap: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks suitable for processing by models.
        
        Args:
            text: Input text
            chunk_size: Maximum size of each chunk (words)
            chunk_overlap: Number of overlapping words between chunks
            
        Returns:
            List of chunks with metadata
        """
        if not text:
            return []
        
        # Use default settings if not specified
        if chunk_size is None:
            chunk_size = settings.CHUNK_SIZE
        if chunk_overlap is None:
            chunk_overlap = settings.CHUNK_OVERLAP
            
        # Tokenize into sentences first
        sentences = sent_tokenize(text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for i, sentence in enumerate(sentences):
            # Count words in the sentence (approximate)
            sentence_words = len(sentence.split())
            
            # If adding this sentence exceeds the chunk size and we already have content,
            # finalize the current chunk and start a new one
            if current_size + sentence_words > chunk_size and current_chunk:
                # Join sentences into a single text
                chunk_text = " ".join(current_chunk)
                
                chunks.append({
                    "text": chunk_text,
                    "word_count": current_size,
                    "start_idx": i - len(current_chunk),
                    "end_idx": i - 1
                })
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk[-min(len(current_chunk), 3):]
                current_chunk = overlap_sentences
                current_size = sum(len(s.split()) for s in overlap_sentences)
            
            # Add the current sentence to the chunk
            current_chunk.append(sentence)
            current_size += sentence_words
        
        # Add the last chunk if it has content
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "word_count": current_size,
                "start_idx": len(sentences) - len(current_chunk),
                "end_idx": len(sentences) - 1
            })
            
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    @staticmethod
    def semantic_chunking(text: str, max_size: int = None) -> List[Dict[str, Any]]:
        """
        Advanced chunking that tries to preserve semantic units.
        
        Args:
            text: Input text
            max_size: Maximum size of each chunk (words)
            
        Returns:
            List of chunks with metadata
        """
        if max_size is None:
            max_size = settings.CHUNK_SIZE
            
        # This is a simplified version for now
        # In a production system, you might use more sophisticated NLP
        chunks = []
        
        # Split by double newline (usually indicates paragraphs)
        paragraphs = text.split('\n\n')
        
        current_chunk = []
        current_size = 0
        
        for i, paragraph in enumerate(paragraphs):
            # Skip empty paragraphs
            if not paragraph.strip():
                continue
                
            # Count words in paragraph
            paragraph_words = len(paragraph.split())
            
            # If this paragraph alone exceeds max size, we need to split it
            if paragraph_words > max_size:
                # If we have accumulated content, add it as a chunk
                if current_chunk:
                    chunks.append({
                        "text": '\n\n'.join(current_chunk),
                        "word_count": current_size,
                        "paragraph_ids": list(range(i - len(current_chunk), i))
                    })
                    current_chunk = []
                    current_size = 0
                
                # Split the large paragraph using sentence-based chunking
                sentences = sent_tokenize(paragraph)
                sent_chunk = []
                sent_size = 0
                
                for sentence in sentences:
                    sentence_words = len(sentence.split())
                    
                    if sent_size + sentence_words > max_size and sent_chunk:
                        # Add the sentence chunk
                        chunks.append({
                            "text": ' '.join(sent_chunk),
                            "word_count": sent_size,
                            "paragraph_ids": [i],
                            "is_split_paragraph": True
                        })
                        sent_chunk = []
                        sent_size = 0
                    
                    sent_chunk.append(sentence)
                    sent_size += sentence_words
                
                # Add any remaining sentences
                if sent_chunk:
                    chunks.append({
                        "text": ' '.join(sent_chunk),
                        "word_count": sent_size,
                        "paragraph_ids": [i],
                        "is_split_paragraph": True
                    })
            
            # If adding this paragraph exceeds the size and we have content, 
            # finalize current chunk
            elif current_size + paragraph_words > max_size and current_chunk:
                chunks.append({
                    "text": '\n\n'.join(current_chunk),
                    "word_count": current_size,
                    "paragraph_ids": list(range(i - len(current_chunk), i))
                })
                current_chunk = [paragraph]
                current_size = paragraph_words
            
            # Otherwise, add to the current chunk
            else:
                current_chunk.append(paragraph)
                current_size += paragraph_words
        
        # Add the final chunk if it has content
        if current_chunk:
            chunks.append({
                "text": '\n\n'.join(current_chunk),
                "word_count": current_size,
                "paragraph_ids": list(range(len(paragraphs) - len(current_chunk), len(paragraphs)))
            })
            
        logger.info(f"Performed semantic chunking: {len(chunks)} chunks created")
        return chunks