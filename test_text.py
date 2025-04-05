"""Test text processing components."""
from processing.text_processor import TextProcessor

def test_text_processor():
    """Test text cleaning and chunking."""
    # Sample text
    sample_text = """
    This is a sample text for testing.
    It has multiple lines and paragraphs.
    
    This is a second paragraph with some content.
    We want to see how the chunking works.
    
    This is a third paragraph that should be in a different chunk
    if we use a small chunk size.
    """
    
    # Test cleaning
    cleaned = TextProcessor.clean_text(sample_text)
    print("Cleaned text:")
    print(cleaned)
    print("-" * 50)
    
    # Test chunking
    chunks = TextProcessor.chunk_text(cleaned, chunk_size=50, chunk_overlap=10)
    print(f"Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}:")
        print(f"Word count: {chunk['word_count']}")
        print(f"Text: {chunk['text'][:100]}...")
        print("-" * 30)

if __name__ == "__main__":
    test_text_processor()