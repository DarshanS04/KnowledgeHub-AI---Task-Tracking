import uuid
import logging
from typing import List, Dict, Any, Optional
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from app.config import settings
from app.core.qdrant import get_qdrant_client

logger = logging.getLogger(__name__)


class VectorService:
    """
    Service class managing vector insertions, deletions, and semantic search queries
    within Qdrant.
    """
    def __init__(self):
        self.client = get_qdrant_client()
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    async def upsert_chunks(
        self,
        chunk_ids: List[uuid.UUID],
        embeddings: List[List[float]],
        payloads: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Upserts multiple document chunk embeddings and payloads into Qdrant collection.
        Returns: list of created Qdrant point IDs (string representation of UUID).
        """
        if not chunk_ids or not embeddings or not payloads:
            return []

        points = []
        point_ids = []
        for cid, vector, payload in zip(chunk_ids, embeddings, payloads):
            point_id = str(cid)
            points.append(PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            ))
            point_ids.append(point_id)

        try:
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Successfully upserted {len(points)} points to Qdrant collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Failed to upsert points to Qdrant: {e}")
            raise RuntimeError(f"Qdrant upload failed: {str(e)}")

        return point_ids

    async def delete_by_document(self, document_id: uuid.UUID) -> None:
        """Deletes all vector points associated with a given document ID."""
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=str(document_id))
                        )
                    ]
                )
            )
            logger.info(f"Successfully deleted vectors for document '{document_id}' in Qdrant")
        except Exception as e:
            logger.error(f"Failed to delete vectors for document {document_id}: {e}")
            raise RuntimeError(f"Qdrant deletion failed: {str(e)}")

    async def search_similar(
        self,
        query_vector: List[float],
        user_id: uuid.UUID,
        source_type: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Searches Qdrant for similar vectors matching the query vector,
        filtered by user_id and optionally source_type.
        """
        # Build filter conditions
        must_conditions = [
            FieldCondition(
                key="user_id",
                match=MatchValue(value=str(user_id))
            )
        ]

        if source_type:
            must_conditions.append(
                FieldCondition(
                    key="source_type",
                    match=MatchValue(value=source_type)
                )
            )

        query_filter = Filter(must=must_conditions)

        try:
            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            hits = []
            for hit in results:
                hits.append({
                    "point_id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                })
            return hits
        except Exception as e:
            logger.error(f"Qdrant similarity search failed: {e}")
            raise RuntimeError(f"Qdrant search failed: {str(e)}")
