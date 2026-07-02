import pytest
from unittest.mock import MagicMock, patch
from app.services.embedding_service import EmbeddingService


@patch("app.services.embedding_service.get_embedding_model")
def test_generate_query_embedding(mock_get_model):
    # Mock SentenceTransformer model instance
    mock_model = MagicMock()
    mock_array = MagicMock()
    mock_array.__getitem__.return_value = MagicMock(tolist=lambda: [0.1, 0.2, 0.3])
    mock_model.encode.return_value = mock_array
    mock_get_model.return_value = mock_model

    service = EmbeddingService()
    vector = service.generate_query_embedding("What is RAG?")
    
    # Assert query model input uses the retrieval prefix
    mock_model.encode.assert_called_once_with(
        ["query: What is RAG?"],
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True
    )
    assert len(vector) == 3
