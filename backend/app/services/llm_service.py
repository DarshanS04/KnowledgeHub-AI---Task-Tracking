import logging
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """
    Abstract Base Class for LLM interaction, allowing easy swap of Gemini
    with Ollama or other providers.
    """
    @abstractmethod
    async def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def generate_stream(self, prompt: str, system_instruction: Optional[str] = None) -> AsyncIterator[str]:
        pass


class GeminiProvider(LLMProvider):
    """
    Google Gemini API implementation using the official google-genai SDK.
    """
    def __init__(self):
        # The new SDK automatically picks up GEMINI_API_KEY env var
        # or we can pass it explicitly.
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL_NAME

    async def generate(self, prompt: str, system_instruction: str = None) -> str:
        """Generates a text response synchronously (blocks until done)."""
        try:
            config = None
            if system_instruction:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2, # Lower temperature for factual accuracy in RAG
                )
            
            # Using run_in_executor to avoid blocking FastAPI's async loop for SDK call
            import asyncio
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
                config=config
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise RuntimeError(f"LLM generation failed: {str(e)}")

    async def generate_stream(self, prompt: str, system_instruction: str = None) -> AsyncIterator[str]:
        """Generates a streaming text response (Server-Sent Events friendly)."""
        try:
            config = None
            if system_instruction:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                )

            # Retrieve stream iterator via thread pool
            import asyncio
            stream = await asyncio.to_thread(
                self.client.models.generate_content_stream,
                model=self.model,
                contents=prompt,
                config=config
            )

            # Async generator yielding text chunks
            for chunk in stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini streaming API call failed: {e}")
            raise RuntimeError(f"LLM stream generation failed: {str(e)}")
