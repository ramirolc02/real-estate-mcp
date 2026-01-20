"""Bearer token authentication middleware.

Note: This middleware is implemented as "pure ASGI" (not BaseHTTPMiddleware).
Starlette's BaseHTTPMiddleware is known to interact poorly with streaming/SSE
responses and cancellation, which can surface as noisy internal errors when a
client disconnects mid-request (https://github.com/Kludex/starlette/discussions/2094).
"""

from __future__ import annotations

import logging

import anyio
from starlette.exceptions import HTTPException 
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from src.config import settings

logger = logging.getLogger(__name__).setLevel(logging.DEBUG)


class BearerAuthMiddleware:
    """Middleware to verify Bearer token authentication.

    Protects all routes except health check endpoints.
    """

    # Paths that don't require authentication
    PUBLIC_PATHS = {"/health", "/", "/docs", "/openapi.json", "/redoc"}

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = (scope.get("method") or "").upper()
        path = scope.get("path") or ""

        # Skip auth for CORS preflight requests (OPTIONS method)
        # and for public endpoints.
        if method == "OPTIONS" or path in self.PUBLIC_PATHS:
            try:
                await self.app(scope, receive, send)
            except (HTTPException, anyio.get_cancelled_exc_class()):
                return
            return

        # Read Authorization header without consuming the request body.
        headers = {k.lower(): v for (k, v) in (scope.get("headers") or [])}
        auth_header = headers.get(b"authorization", b"").decode("latin-1")

        # Validate Bearer token format
        if not auth_header.startswith("Bearer "):
            response = JSONResponse(
                {
                    "error": True,
                    "code": "MISSING_TOKEN",
                    "message": "Authorization header must include Bearer token",
                },
                status_code=401,
            )
            try:
                await response(scope, receive, send)
            except (HTTPException, anyio.get_cancelled_exc_class()):
                return
            return

        # Extract and validate token
        token = auth_header.replace("Bearer ", "", 1)
        if token != settings.api_token:
            response = JSONResponse(
                {
                    "error": True,
                    "code": "INVALID_TOKEN",
                    "message": "Invalid or expired authentication token",
                },
                status_code=401,
            )
            try:
                await response(scope, receive, send)
            except (HTTPException, anyio.get_cancelled_exc_class()):
                return
            return

        try:
            await self.app(scope, receive, send)
        except (HTTPException, anyio.get_cancelled_exc_class()):
            return
