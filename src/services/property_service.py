"""Property service for business logic."""

from src.exceptions import InvalidFilterError, PropertyNotFoundError
from src.repositories.property_repository import PropertyRepository


class PropertyService:
    """Service layer for property operations."""

    def __init__(self, repository: PropertyRepository):
        self.repository = repository

    async def search(
        self,
        city: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        status: str | None = None,
    ) -> list[dict]:
        """Search properties with optional filters.

        Returns a list of property summaries.
        """
        # Validate filters
        if min_price is not None and min_price < 0:
            raise InvalidFilterError("min_price cannot be negative")
        if max_price is not None and max_price < 0:
            raise InvalidFilterError("max_price cannot be negative")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise InvalidFilterError("min_price cannot be greater than max_price")
        if status is not None and status not in ("available", "sold"):
            raise InvalidFilterError("status must be 'available' or 'sold'")

        properties = await self.repository.search(
            city=city,
            min_price=min_price,
            max_price=max_price,
            status=status,
        )

        return [prop.to_summary() for prop in properties]

    async def get_by_id(self, property_id: str) -> dict:
        """Get full property details by ID.

        Raises PropertyNotFoundError if not found.
        """
        property_obj = await self.repository.get_by_id(property_id)
        if not property_obj:
            raise PropertyNotFoundError(property_id)

        return property_obj.to_dict()

    async def get_recent(self, hours: int = 24) -> list[dict]:
        """Get properties created within the last N hours."""
        properties = await self.repository.get_recent(hours=hours)
        return [prop.to_dict() for prop in properties]

    async def get_all(self) -> list[dict]:
        """Get all properties."""
        properties = await self.repository.get_all()
        return [prop.to_dict() for prop in properties]
