import logging
import torch
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)

# Global singleton model variable
_embedding_model: SentenceTransformer = None


def get_embedding_model() -> SentenceTransformer:
    """
    Returns the loaded global SentenceTransformer model instance (Singleton).
    Automatically downloads the model on first call if not cached.
    """
    global _embedding_model
    if _embedding_model is None:
        model_name = "BAAI/bge-small-en-v1.5"
        fallback_name = "all-MiniLM-L6-v2"
        
        # Detect acceleration (CUDA, MPS for Mac, or CPU)
        device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
        logger.info(f"Loading embedding model '{model_name}' on device '{device}'...")
        
        try:
            _embedding_model = SentenceTransformer(model_name, device=device)
        except Exception as e:
            logger.warning(f"Failed to load preferred model '{model_name}': {e}. Falling back to '{fallback_name}'...")
            try:
                _embedding_model = SentenceTransformer(fallback_name, device=device)
            except Exception as fe:
                logger.critical(f"Failed to load fallback embedding model: {fe}")
                raise RuntimeError(f"Could not load any embedding models: {fe}")

    return _embedding_model


class EmbeddingService:
    """
    Service wrapper managing vector generation for ingestion chunks or search queries.
    """
    def __init__(self):
        self.model = get_embedding_model()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates list of embeddings for list of raw text strings (batch)."""
        if not texts:
            return []
        
        # generate embeddings and normalize them (optimal for cosine distance search)
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generates query embedding, prefixing with 'query: ' for optimal BGE model performance.
        """
        # Per BAAI/bge-small-en-v1.5 specifications, retrieval queries should be prefixed
        query_text = f"query: {query}"
        embeddings = self.model.encode(
            [query_text],
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings[0].tolist()
