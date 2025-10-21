import time
from datetime import datetime, timezone
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..db.models import LogEntry


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests to MongoDB"""

    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()

        # Extract user from token if present
        user = None
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                user = await get_current_user_from_token(token)
        except:
            # If token extraction fails, continue without user
            pass

        # Process the request
        response = await call_next(request)

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000

        # Get client IP
        client_ip = request.client.host if request.client else None
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()

        # Create log entry (with better error handling)
        try:
            log_entry = LogEntry(
                timestamp=datetime.now(timezone.utc),
                user=user,
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
                error_message=None if response.status_code < 400 else f"HTTP {response.status_code}"
            )

            # Save to MongoDB asynchronously (fire and forget to not slow down response)
            await log_entry.insert()

        except Exception as e:
            # Don't let logging failures affect the API response
            print(f"Failed to log request: {e}")
            # Continue without logging to prevent breaking the API

        return response


async def get_current_user_from_token(token: str) -> Optional[str]:
    """Extract current user from JWT token"""
    try:
        from jose import jwt
        from pwc.settings import settings

        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        return username
    except:
        return None