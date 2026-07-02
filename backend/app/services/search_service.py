import uuid
import logging
from typing import List, Optional
from datetime import datetime
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.schemas.search import SearchResult

logger = logging.getLogger(__name__)


class SearchService:
    """
    Service class managing raw semantic keyword searches and document filtering.
    """
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()

    async def execute_search(
        self,
        query: str,
        user_id: uuid.UUID,
        source_type: Optional[str] = None,
        limit: int = 5
    ) -> List[SearchResult]:
        """
        Encodes query string, searches Qdrant, and returns results formatted as SearchResults.
        """
        # Encode query (using query retrieval prefix)
        query_vector = self.embedding_service.generate_query_embedding(query)
        
        # Search similarities in Qdrant
        hits = await self.vector_service.search_similar(
            query_vector=query_vector,
            user_id=user_id,
            source_type=source_type,
            limit=limit
        )

        results = []
        for hit in hits:
            payload = hit["payload"]
            results.append(SearchResult(
                filename=payload.get("filename", "Unknown File"),
                page=payload.get("page_number"),
                chunk_number=payload.get("chunk_number", 0),
                similarity_score=hit["score"],
                preview_snippet=payload.get("text", "")[:300], # return a 300 char snippet
                document_id=payload.get("document_id", "")
            ))
            
        return results
