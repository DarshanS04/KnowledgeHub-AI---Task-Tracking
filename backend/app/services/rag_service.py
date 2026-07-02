import logging
import uuid
from typing import List, Dict, Any, Tuple, AsyncIterator
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.llm_service import GeminiProvider

logger = logging.getLogger(__name__)


class RagService:
    """
    Core RAG orchestration service coordinating embedding queries, Qdrant searches,
    prompt injection, and LLM completions.
    """
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
        self.llm_provider = GeminiProvider()

    async def retrieve_context(
        self,
        query: str,
        user_id: uuid.UUID,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generates query embedding and retrieves top-K matching documents from Qdrant.
        """
        query_vector = self.embedding_service.generate_query_embedding(query)
        hits = await self.vector_service.search_similar(
            query_vector=query_vector,
            user_id=user_id,
            limit=limit
        )
        return hits

    def build_prompt_and_instruction(
        self,
        query: str,
        hits: List[Dict[str, Any]],
        chat_history: List[Dict[str, str]] = None
    ) -> Tuple[str, str]:
        """
        Orchestrates RAG prompt templates and enforces citation/no-hallucination rules.
        """
        # 1. Format context text with citations markers
        context_blocks = []
        for hit in hits:
            payload = hit["payload"]
            filename = payload.get("filename", "Unknown File")
            page = payload.get("page_number", 1)
            chunk = payload.get("chunk_number", 1)
            text = payload.get("text", "")
            
            context_blocks.append(
                f"Source Document: {filename}\n"
                f"Page Reference: {page}\n"
                f"Chunk Reference: {chunk}\n"
                f"Content:\n{text}\n"
                f"----------------------------------------"
            )

        context_str = "\n\n".join(context_blocks)

        # 2. System instruction enforcing strict rules
        system_instruction = (
            "You are a highly precise and helpful Knowledge Assistant. Your primary task is to answer user queries "
            "strictly using the provided source context. You must adhere to these absolute rules:\n"
            "1. Answer the question using ONLY the provided text under 'Retrieved Context'.\n"
            "2. If the context does not contain the answer, reply exactly with: "
            "\"I couldn't find this information in your uploaded documents.\"\n"
            "3. Do NOT make up information or use any external knowledge. Absolutely no hallucinations.\n"
            "4. For every claim or statement you make, you MUST cite the source document. Format your citations "
            "in-line using brackets like: [Source: filename, Page X, Chunk Y]. Ensure filename matches the source "
            "exactly."
        )

        # 3. User prompt
        user_prompt = ""
        
        # Inject recent chat history if available
        if chat_history:
            user_prompt += "Recent Conversation History:\n"
            for msg in chat_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                user_prompt += f"{role}: {msg['content']}\n"
            user_prompt += "\n"

        user_prompt += (
            f"Retrieved Context:\n"
            f"{context_str}\n\n"
            f"User Question: {query}\n"
            f"Assistant Answer:"
        )

        return user_prompt, system_instruction

    async def answer_query(
        self,
        query: str,
        user_id: uuid.UUID,
        chat_history: List[Dict[str, str]] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Completes the full RAG cycle synchronously.
        Returns: Tuple of (answer_text, list of retrieved citations).
        """
        hits = await self.retrieve_context(query, user_id)
        if not hits:
            return "I couldn't find this information in your uploaded documents.", []

        prompt, system_instruction = self.build_prompt_and_instruction(query, hits, chat_history)
        answer = await self.llm_provider.generate(prompt, system_instruction)
        
        # Format citations to return to frontend
        citations = self._format_citations(hits)
        return answer, citations

    async def answer_query_stream(
        self,
        query: str,
        user_id: uuid.UUID,
        chat_history: List[Dict[str, str]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Streams RAG answers token-by-token.
        Yields: dict payloads containing either 'token' or 'citations' array.
        """
        hits = await self.retrieve_context(query, user_id)
        citations = self._format_citations(hits)
        
        # Immediately yield citations so the frontend can render them alongside the incoming text
        yield {"event": "citations", "data": citations}

        if not hits:
            yield {"event": "token", "data": "I couldn't find this information in your uploaded documents."}
            return

        prompt, system_instruction = self.build_prompt_and_instruction(query, hits, chat_history)
        
        # Stream response
        async for token in self.llm_provider.generate_stream(prompt, system_instruction):
            yield {"event": "token", "data": token}

    def _format_citations(self, hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Formats search hits into structured citation items."""
        citations = []
        for hit in hits:
            payload = hit["payload"]
            citations.append({
                "filename": payload.get("filename", "Unknown File"),
                "page_number": payload.get("page_number"),
                "chunk_number": payload.get("chunk_number"),
                "snippet": payload.get("text", "")[:300], # Short preview snippet
                "similarity_score": hit["score"]
            })
        return citations
