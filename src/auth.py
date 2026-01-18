"""Bearer token authentication middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.config import settings


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to verify Bearer token authentication.

    Protects all routes except health check endpoints.
    """

    # Paths that don't require authentication
    PUBLIC_PATHS = {"/health", "/", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next) -> Response:
        """Check for valid Bearer token on protected routes."""
        # Skip auth for CORS preflight requests (OPTIONS method)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip auth for public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        # Get Authorization header
        auth_header = request.headers.get("Authorization", "")

        # Validate Bearer token format
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {
                    "error": True,
                    "code": "MISSING_TOKEN",
                    "message": "Authorization header must include Bearer token",
                },
                status_code=401,
            )

        # Extract and validate token
        token = auth_header.replace("Bearer ", "", 1)
        if token != settings.api_token:
            return JSONResponse(
                {
                    "error": True,
                    "code": "INVALID_TOKEN",
                    "message": "Invalid or expired authentication token",
                },
                status_code=401,
            )

        # Token is valid, proceed with request
        return await call_next(request)
