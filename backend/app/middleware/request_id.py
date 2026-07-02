import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from app.core.logging import request_id_ctx_var


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that generates a unique Request ID for each incoming HTTP request,
    sets it in the context variables, and returns it in the response headers.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check if client sent request ID, otherwise generate one
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Set the token in request state and logging contextvar
        request.state.request_id = request_id
        token = request_id_ctx_var.set(request_id)
        
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Clean up token contextvar
            request_id_ctx_var.reset(token)
