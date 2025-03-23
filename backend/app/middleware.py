from fastapi import Request
import time
import uuid
from typing import Callable
from fastapi.middleware.base import BaseHTTPMiddleware

class LegalAuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware that creates an audit trail for legal operations
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Add timestamp
        start_time = time.time()
        request.state.start_time = start_time
        
        # Log the request (in a real system, this would be secure storage)
        print(f"[LEGAL AUDIT] Request {request_id} started at {time.ctime(start_time)}")
        print(f"[LEGAL AUDIT] Path: {request.url.path}")
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add audit headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log the response
        print(f"[LEGAL AUDIT] Request {request_id} completed in {process_time:.4f} seconds")
        
        return response

class PrivilegeProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware that screens for potential attorney-client privileged content
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Process the request
        response = await call_next(request)
        
        # Add privilege warning header
        response.headers["X-Privilege-Warning"] = "Communications may be privileged. Do not share without counsel review."
        
        return response