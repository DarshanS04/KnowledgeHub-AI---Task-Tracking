import json
import time
import uuid
import logging
from typing import AsyncGenerator, Optional
from fastapi import APIRouter, Depends, status, Query, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import DataResponse, PaginatedResponse, PaginatedMetadata
from app.schemas.chat import (
    ChatRequest,
    MessageResponse,
    ConversationResponse,
    ConversationCreate
)
from app.services.chat_service import ChatService
from app.services.rag_service import RagService

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
)
async def chat_interaction(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Handles user chat interactions. If stream=True, returns an SSE stream,
    otherwise returns a single synchronous response payload.
    """
    chat_service = ChatService(db)
    rag_service = RagService()

    # Get or create active conversation
    conversation = await chat_service.get_or_create_conversation(
        user_id=current_user.id,
        conversation_id=payload.conversation_id
    )

    # 1. Log the user's message to DB immediately
    await chat_service.log_message(
        conversation_id=conversation.id,
        role="user",
        content=payload.message
    )

    # 2. Get recent chat log context
    history = await chat_service.get_llm_context_history(conversation.id)

    if not payload.stream:
        # Synchronous execution
        start_time = time.time()
        answer, citations = await rag_service.answer_query(
            query=payload.message,
            user_id=current_user.id,
            chat_history=history
        )
        duration = time.time() - start_time
        
        # Log assistant response to DB
        assistant_msg = await chat_service.log_message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            citations=citations,
            response_time=duration
        )
        
        return DataResponse(
            data={
                "conversation_id": conversation.id,
                "message": MessageResponse.model_validate(assistant_msg)
            }
        )

    # Streaming execution
    async def sse_generator() -> AsyncGenerator[str, None]:
        start_time = time.time()
        accumulated_text = ""
        citations_sent = []

        try:
            # Yield conversation ID info on startup
            yield f"data: {json.dumps({'event': 'meta', 'conversation_id': str(conversation.id)})}\n\n"

            async for event_data in rag_service.answer_query_stream(
                query=payload.message,
                user_id=current_user.id,
                chat_history=history
            ):
                event_type = event_data["event"]
                data = event_data["data"]

                if event_type == "citations":
                    citations_sent = data
                    yield f"data: {json.dumps({'event': 'citations', 'data': data})}\n\n"
                elif event_type == "token":
                    accumulated_text += data
                    yield f"data: {json.dumps({'event': 'token', 'data': data})}\n\n"

            # Log final streamed reply to DB
            duration = time.time() - start_time
            await chat_service.log_message(
                conversation_id=conversation.id,
                role="assistant",
                content=accumulated_text,
                citations=citations_sent,
                response_time=duration
            )

        except Exception as e:
            logger.exception("Error in SSE chat streaming generator:")
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no", # Disable buffering for Nginx proxying
        }
    )


@router.get(
    "/history",
    response_model=PaginatedResponse[ConversationResponse],
    status_code=status.HTTP_200_OK,
)
async def list_conversations(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists recent conversation threads for the current user."""
    chat_service = ChatService(db)
    conversations, total = await chat_service.get_user_conversations(current_user.id, page, size)
    
    pages = (total + size - 1) // size
    return PaginatedResponse(
        data=[ConversationResponse.model_validate(c) for c in conversations],
        meta=PaginatedMetadata(
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    )


@router.get(
    "/history/{conversation_id}",
    response_model=DataResponse[list[MessageResponse]],
    status_code=status.HTTP_200_OK,
)
async def get_conversation_messages(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves all message logs for a specific conversation ID."""
    chat_service = ChatService(db)
    messages = await chat_service.get_conversation_history(current_user.id, conversation_id)
    return DataResponse(data=[MessageResponse.model_validate(m) for m in messages])


@router.delete(
    "/{conversation_id}",
    response_model=DataResponse[str],
    status_code=status.HTTP_200_OK,
)
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes conversation thread history."""
    chat_service = ChatService(db)
    await chat_service.delete_conversation(current_user.id, conversation_id)
    return DataResponse(data="Conversation deleted successfully.")


@router.put(
    "/{conversation_id}",
    response_model=DataResponse[ConversationResponse],
    status_code=status.HTTP_200_OK,
)
async def rename_conversation(
    conversation_id: uuid.UUID,
    title: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Renames a conversation thread title."""
    chat_service = ChatService(db)
    updated = await chat_service.rename_conversation(current_user.id, conversation_id, title)
    return DataResponse(data=ConversationResponse.model_validate(updated))
