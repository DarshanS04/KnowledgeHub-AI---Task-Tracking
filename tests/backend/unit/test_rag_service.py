import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from app.services.rag_service import RagService


@pytest.mark.asyncio
async def test_answer_query_no_context():
    # Test fallback message when context matches are empty
    service = RagService()
    service.retrieve_context = AsyncMock(return_value=[])

    user_id = uuid.uuid4()
    answer, citations = await service.answer_query("Is there an AWS doc?", user_id)
    
    assert "I couldn't find this information" in answer
    assert len(citations) == 0


@pytest.mark.asyncio
@patch("app.services.rag_service.GeminiProvider")
async def test_answer_query_success(mock_llm_provider):
    # Mock LLM provider response
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "AWS S3 stands for Simple Storage Service."
    mock_llm_provider.return_value = mock_llm

    service = RagService()
    
    # Mock context hits
    mock_hits = [
        {
            "score": 0.895,
            "payload": {
                "filename": "AWS.pdf",
                "page_number": 2,
                "chunk_number": 4,
                "text": "Amazon Simple Storage Service (Amazon S3) is an object storage service..."
            }
        }
    ]
    service.retrieve_context = AsyncMock(return_value=mock_hits)

    user_id = uuid.uuid4()
    answer, citations = await service.answer_query("What does S3 stand for?", user_id)
    
    assert "Simple Storage Service" in answer
    assert len(citations) == 1
    assert citations[0]["filename"] == "AWS.pdf"
    assert citations[0]["similarity_score"] == 0.895
