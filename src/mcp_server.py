"""FastMCP server with tools, resources, and prompts."""

import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from src.db.session import async_session_maker
from src.exceptions import MCPError
from src.repositories.property_repository import PropertyRepository
from src.services.content_generator import ContentGeneratorService
from src.services.property_service import PropertyService

# Initialize FastMCP server
mcp = FastMCP("real-estate-mcp")

# Initialize content generator service (stateless, can be singleton)
content_generator = ContentGeneratorService()


@asynccontextmanager
async def property_service_context() -> AsyncGenerator[PropertyService, None]:
    """Context manager that yields a PropertyService with a properly scoped session.

    The session is open for the duration of the `async with` block and
    automatically closed when the block exits. This ensures:
    - No "session closed" errors (session lives as long as caller needs it)
    - Proper connection pool management (connection returned on exit)
    - Clear transaction boundaries (one session = one unit of work)

    Usage:
        async with property_service_context() as service:
            result = await service.search(city="Lisbon")
    """
    async with async_session_maker() as session:
        repository = PropertyRepository(session)
        yield PropertyService(repository)


# =============================================================================
# MCP Tools
# =============================================================================


@mcp.tool(description="Search for properties based on filters like city, price range, and status")
async def search_properties(
    city: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    status: Literal["available", "sold"] | None = None,
) -> str:
    """Search for properties with optional filters.

    Args:
        city: Filter by city name (case-insensitive partial match)
        min_price: Minimum price in EUR
        max_price: Maximum price in EUR
        status: Property status ('available' or 'sold')

    Returns:
        JSON string with list of matching property summaries
    """
    try:
        async with property_service_context() as service:
            results = await service.search(
                city=city,
                min_price=min_price,
                max_price=max_price,
                status=status,
            )
            return json.dumps({"count": len(results), "properties": results}, indent=2)
    except MCPError as e:
        return json.dumps({"error": True, "code": e.error_code, "message": e.message})
    except Exception as e:
        return json.dumps({"error": True, "code": "SEARCH_ERROR", "message": str(e)})


@mcp.tool(description="Get full details for a specific property by its ID")
async def get_property_details(property_id: str) -> str:
    """Retrieve complete property information including internal notes.

    Args:
        property_id: UUID of the property

    Returns:
        JSON string with full property details or error message
    """
    try:
        async with property_service_context() as service:
            result = await service.get_by_id(property_id)
            return json.dumps(result, indent=2)
    except MCPError as e:
        return json.dumps({"error": True, "code": e.error_code, "message": e.message})
    except Exception as e:
        return json.dumps({"error": True, "code": "DETAILS_ERROR", "message": str(e)})


@mcp.tool(
    description="Generate SEO-optimized HTML content for a property listing. "
    "Returns structured HTML with title, meta tags, and content sections."
)
async def generate_listing_content(
    property_id: str,
    target_language: str = "en",
    tone: str | None = None,
) -> str:
    """Generate HTML listing content for a property.

    Args:
        property_id: UUID of the property
        target_language: Target language code (e.g., 'en', 'pt')
        tone: Content tone - 'professional', 'casual', or 'luxury'

    Returns:
        Generated HTML content string or error message
    """
    try:
        async with property_service_context() as service:
            property_data = await service.get_by_id(property_id)

            html_content = await content_generator.generate_listing_html(
                property_data=property_data,
                target_language=target_language,
                tone=tone,
            )
            return html_content
    except MCPError as e:
        return json.dumps({"error": True, "code": e.error_code, "message": e.message})
    except Exception as e:
        return json.dumps({"error": True, "code": "GENERATION_ERROR", "message": str(e)})


# =============================================================================
# MCP Resources
# =============================================================================


@mcp.resource("realestate://listings/today")
async def daily_listings() -> str:
    """Daily digest of new property listings.

    Returns properties created within the last 24 hours.
    """
    try:
        async with property_service_context() as service:
            properties = await service.get_recent(hours=24)

            return json.dumps(
                {
                    "date": datetime.now().isoformat(),
                    "count": len(properties),
                    "listings": properties,
                },
                indent=2,
            )
    except Exception as e:
        return json.dumps({"error": True, "message": str(e)})


# =============================================================================
# MCP Prompts
# =============================================================================


@mcp.prompt(description="Generate a marketing email prompt for a property")
async def marketing_email(property_id: str) -> list:
    """Generate a marketing email prompt for a specific property.

    Args:
        property_id: UUID of the property to market

    Returns:
        List of prompt messages for the AI to generate a marketing email
    """
    try:
        async with property_service_context() as service:
            prop = await service.get_by_id(property_id)

            features_str = ", ".join(prop.get("features", [])) if prop.get("features") else "N/A"

            prompt_text = f"""Write a compelling marketing email for this property:

Property: {prop["title"]}
Location: {prop["city"]}, {prop.get("address", "N/A")}
Price: €{prop["price"]:,.0f}
Type: {prop.get("property_type", "N/A")}
Bedrooms: {prop.get("bedrooms", "N/A")} | Bathrooms: {prop.get("bathrooms", "N/A")}
Area: {prop.get("area_sqm", "N/A")} m²
Features: {features_str}

Description: {prop.get("description", "No description available")}

The email should:
- Have an attention-grabbing subject line
- Highlight the key selling points
- Create urgency without being pushy
- Include a clear call-to-action
- Be professional yet engaging"""

            return [
                {
                    "role": "user",
                    "content": TextContent(type="text", text=prompt_text),
                }
            ]
    except MCPError as e:
        return [
            {
                "role": "user",
                "content": TextContent(
                    type="text",
                    text=f"Error: {e.message}. Please provide a valid property ID.",
                ),
            }
        ]
    except Exception as e:
        return [
            {
                "role": "user",
                "content": TextContent(
                    type="text",
                    text=f"Error retrieving property: {e}. Please check the property ID.",
                ),
            }
        ]
