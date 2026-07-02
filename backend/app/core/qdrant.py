import logging
from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.http import models
from app.config import settings

logger = logging.getLogger(__name__)

# Async Qdrant client
async_qdrant_client: AsyncQdrantClient = None


def get_qdrant_client() -> AsyncQdrantClient:
    """Returns the global active AsyncQdrantClient instance."""
    global async_qdrant_client
    if async_qdrant_client is None:
        if settings.ENVIRONMENT == "test":
            # For testing, we can use local client in-memory if needed, but
            # AsyncQdrantClient doesn't support :memory: directly, so we use
            # standard AsyncQdrantClient pointing to localhost or a mock.
            # QdrantClient(location=":memory:") is sync only.
            # We will default to the host/port in settings or host docker.
            pass
        async_qdrant_client = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
    return async_qdrant_client


async def init_qdrant() -> None:
    """
    Initializes the Qdrant database. Creates the collection and payload indexes
    if they do not already exist.
    """
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION_NAME

    try:
        # Check if collection exists
        collections = await client.get_collections()
        exists = any(c.name == collection_name for c in collections.collections)

        if not exists:
            logger.info(f"Creating Qdrant collection: {collection_name}")
            # BAAI/bge-small-en-v1.5 vector size is 384
            await client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE,
                ),
            )

            # Create payload indexes for fast filtering
            logger.info("Creating Qdrant payload indexes...")
            await client.create_payload_index(
                collection_name=collection_name,
                field_name="user_id",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            await client.create_payload_index(
                collection_name=collection_name,
                field_name="source_type",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            await client.create_payload_index(
                collection_name=collection_name,
                field_name="document_id",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            logger.info("Qdrant collection and indexes setup completed.")
        else:
            logger.info(f"Qdrant collection '{collection_name}' already exists.")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant: {e}")
        # In test mode or local startup without Qdrant running yet, don't crash, just log warning
        if settings.ENVIRONMENT == "production":
            raise
