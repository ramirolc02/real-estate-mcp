"""Custom exceptions for MCP-friendly error handling."""


class MCPError(Exception):
    """Base exception for MCP tool errors."""

    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class PropertyNotFoundError(MCPError):
    """Raised when a property ID doesn't exist."""

    def __init__(self, property_id: str):
        super().__init__(
            message=f"Property with ID '{property_id}' not found. Please verify the ID and try again.",
            error_code="PROPERTY_NOT_FOUND",
        )


class InvalidFilterError(MCPError):
    """Raised when search filters are invalid."""

    def __init__(self, detail: str):
        super().__init__(
            message=f"Invalid search filter: {detail}",
            error_code="INVALID_FILTER",
        )


class ContentGenerationError(MCPError):
    """Raised when content generation fails."""

    def __init__(self, detail: str):
        super().__init__(
            message=f"Content generation failed: {detail}",
            error_code="CONTENT_GENERATION_ERROR",
        )
