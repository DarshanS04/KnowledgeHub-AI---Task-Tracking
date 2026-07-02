import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that records metrics for every API call, including execution duration,
    request path, response status, and exceptions raised.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        path = request.url.path
        if request.query_params:
            path += f"?{request.query_params}"

        logger.info(f"Incoming request: {request.method} {path}")
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            logger.info(
                f"Completed request: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {process_time:.2f}ms"
            )
            return response
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Failed request: {request.method} {request.url.path} - "
                f"Error: {str(e)} - "
                f"Duration: {process_time:.2f}ms"
            )
            raise
