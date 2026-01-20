"""FastAPI application with FastMCP server integration."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from src.auth import BearerAuthMiddleware
from src.config import settings
from src.db.session import close_db, init_db
from src.mcp_server import mcp


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    await init_db()
    print(f"{settings.app_name} started")
    print(f"Database connected: {settings.database_url}")

    yield

    await close_db()
    print("Server shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="MCP Server for Real Estate AI Agents - Enables property search, "
    "details retrieval, and content generation via Model Context Protocol.",
    version="0.1.0",
    lifespan=lifespan,
)

# =============================================================================
# Middleware Configuration
# =============================================================================

# Add authentication middleware
app.add_middleware(BearerAuthMiddleware)

# Add CORS middleware for MCP Inspector and remote connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for MCP clients
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "mcp-protocol-version",
        "mcp-session-id",
    ],
    expose_headers=["mcp-session-id"],  # MCP protocol header
)

# Handle proxy headers (Railway, Heroku, etc.)
# This ensures correct client IP and protocol detection behind reverse proxies
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])


# =============================================================================
# Health & Info Endpoints
# =============================================================================


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with server info."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "mcp_endpoint": "/mcp/sse",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker/Kubernetes probes."""
    return JSONResponse(
        content={"status": "healthy", "service": settings.app_name},
        status_code=200,
    )


# =============================================================================
# Mount MCP Server
# =============================================================================

# Mount the FastMCP SSE app at /mcp
app.mount("/mcp", mcp.sse_app())


# =============================================================================
# Development Server
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
