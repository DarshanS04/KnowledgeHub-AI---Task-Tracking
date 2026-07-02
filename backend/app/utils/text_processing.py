import re
import unicodedata
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Create standard clean text function
def clean_text(text: str) -> str:
    """
    Cleans raw extracted text by normalizing whitespaces, removing null characters,
    and unifying unicode formats.
    """
    if not text:
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize("NFKC", text)
    
    # Replace null characters
    text = text.replace("\x00", "")
    
    # Replace multiple newlines or whitespaces with single ones
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    
    return text.strip()


class TokenBasedTextSplitter:
    """
    Splits text into chunks of roughly 512 tokens (approx 2000 characters)
    with a 50 token overlap (approx 200 characters).
    """
    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 200):
        # We configure it with characters assuming ~4 characters per token
        # This keeps chunk_size around 512 tokens and chunk_overlap around 50 tokens.
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True
        )

    def split(self, text: str) -> List[str]:
        """Splits cleaned text into chunks."""
        cleaned = clean_text(text)
        if not cleaned:
            return []
        return self.splitter.split_text(cleaned)
