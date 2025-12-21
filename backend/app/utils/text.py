"""Text utilities."""

import re


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def clean_text(text: str) -> str:
    """Clean text for voice output."""
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove extra punctuation
    text = re.sub(r'[^\w\s.!?,-]', '', text)
    
    return text.strip()


def split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def extract_phone(text: str) -> str:
    """Extract phone number from text."""
    # Simple US phone pattern
    match = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
    if match:
        return match.group()
    return None


def extract_email(text: str) -> str:
    """Extract email from text."""
    match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if match:
        return match.group()
    return None


def format_response_for_voice(text: str, max_sentences: int = 2) -> str:
    """
    Format text for voice output.
    
    Args:
        text: Text to format
        max_sentences: Maximum sentences to include
    
    Returns:
        Formatted text suitable for voice
    """
    # Clean the text
    text = clean_text(text)
    
    # Split into sentences and limit
    sentences = split_sentences(text)
    limited = sentences[:max_sentences]
    
    # Join back together
    return " ".join(limited)
