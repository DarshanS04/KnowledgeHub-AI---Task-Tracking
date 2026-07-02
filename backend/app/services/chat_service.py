import uuid
import logging
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import NotFoundException, AppException
from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository

logger = logging.getLogger(__name__)


class ChatService:
    """
    Service class managing conversation threads, logging messages, and formatting chat history.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.conv_repo = ConversationRepository(session)
        self.msg_repo = MessageRepository(session)

    async def get_or_create_conversation(
        self,
        user_id: uuid.UUID,
        conversation_id: Optional[uuid.UUID] = None,
        title: Optional[str] = None
    ) -> Conversation:
        """
        Retrieves an existing conversation or initializes a new one.
        """
        if conversation_id:
            conv = await self.conv_repo.get(conversation_id)
            if not conv:
                raise NotFoundException(message="Conversation not found.")
            if conv.user_id != user_id:
                raise AppException(status_code=403, message="Access forbidden to this conversation.")
            return conv

        # Create new conversation
        conv_title = title or "New Conversation"
        conv = await self.conv_repo.create({
            "user_id": user_id,
            "title": conv_title
        })
        await self.session.commit()
        return conv

    async def get_user_conversations(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Conversation], int]:
        """Gets paginated conversation list for a user."""
        skip = (page - 1) * size
        return await self.conv_repo.get_by_user(user_id, skip, size)

    async def get_conversation_history(
        self,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID
    ) -> List[Message]:
        """Gets all messages in a specific conversation."""
        # Validate conversation ownership
        await self.get_or_create_conversation(user_id, conversation_id)
        return await self.msg_repo.get_by_conversation(conversation_id)

    async def delete_conversation(self, user_id: uuid.UUID, conversation_id: uuid.UUID) -> None:
        """Deletes a conversation and its messages."""
        conv = await self.conv_repo.get(conversation_id)
        if not conv:
            raise NotFoundException(message="Conversation not found.")
        if conv.user_id != user_id:
            raise AppException(status_code=403, message="Access forbidden to this conversation.")

        await self.conv_repo.remove(conversation_id)
        await self.session.commit()

    async def rename_conversation(
        self,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        new_title: str
    ) -> Conversation:
        """Renames a conversation thread."""
        conv = await self.conv_repo.get(conversation_id)
        if not conv:
            raise NotFoundException(message="Conversation not found.")
        if conv.user_id != user_id:
            raise AppException(status_code=403, message="Access forbidden to this conversation.")

        updated_conv = await self.conv_repo.update(conv, {"title": new_title})
        await self.session.commit()
        return updated_conv

    async def log_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        citations: Optional[List[Dict[str, Any]]] = None,
        response_time: Optional[float] = None
    ) -> Message:
        """Log message entry in DB."""
        # Simple word count as token count fallback
        token_count = len(content.split())
        
        msg = await self.msg_repo.create({
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "citations": citations,
            "token_count": token_count,
            "response_time": response_time
        })
        
        # Update conversation timestamp
        conv = await self.conv_repo.get(conversation_id)
        if conv:
            await self.conv_repo.update(conv, {}) # triggers updated_at update
            
        await self.session.commit()
        return msg

    async def get_llm_context_history(self, conversation_id: uuid.UUID) -> List[Dict[str, str]]:
        """Gets recent context history formatted for LLM input."""
        msgs = await self.msg_repo.get_recent_context(conversation_id, limit=10)
        return [{"role": m.role, "content": m.content} for m in msgs]
