import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs details about each incoming HTTP request,
    including the method, path, status code, and latency in milliseconds.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            # Format time
            process_time_str = f"{process_time:.2f}ms"
            
            logger.info(
                f"{request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Latency: {process_time_str}"
            )
            
            # Add processing time header
            response.headers["X-Response-Time"] = process_time_str
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Request Failed: {request.method} {request.url.path} "
                f"Error: {str(e)} "
                f"Latency: {process_time:.2f}ms"
            )
            raise e
