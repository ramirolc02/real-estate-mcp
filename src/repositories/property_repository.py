"""Repository for property data access operations."""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.property import Property


class PropertyRepository:
    """Async repository for property CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, property_id: str | UUID) -> Property | None:
        """Get a property by its ID."""
        if isinstance(property_id, str):
            try:
                property_id = UUID(property_id)
            except ValueError:
                return None

        result = await self.session.execute(select(Property).where(Property.id == property_id))
        return result.scalar_one_or_none()

    async def search(
        self,
        city: str | None = None,
        min_price: float | Decimal | None = None,
        max_price: float | Decimal | None = None,
        status: str | None = None,
    ) -> list[Property]:
        """Search properties with optional filters."""
        query = select(Property)

        if city:
            # Case-insensitive city search
            query = query.where(Property.city.ilike(f"%{city}%"))

        if min_price is not None:
            query = query.where(Property.price >= Decimal(str(min_price)))

        if max_price is not None:
            query = query.where(Property.price <= Decimal(str(max_price)))

        if status:
            query = query.where(Property.status == status)

        # Order by price ascending
        query = query.order_by(Property.price.asc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_recent(self, hours: int = 24) -> list[Property]:
        """Get properties created within the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        query = (
            select(Property)
            .where(Property.created_at >= cutoff)
            .order_by(Property.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_all(self) -> list[Property]:
        """Get all properties."""
        result = await self.session.execute(select(Property).order_by(Property.created_at.desc()))
        return list(result.scalars().all())

    async def create(self, property_data: dict) -> Property:
        """Create a new property."""
        property_obj = Property(**property_data)
        self.session.add(property_obj)
        await self.session.flush()
        await self.session.refresh(property_obj)
        return property_obj

    async def update(self, property_id: str | UUID, property_data: dict) -> Property | None:
        """Update an existing property."""
        property_obj = await self.get_by_id(property_id)
        if not property_obj:
            return None

        for key, value in property_data.items():
            if hasattr(property_obj, key):
                setattr(property_obj, key, value)

        await self.session.flush()
        await self.session.refresh(property_obj)
        return property_obj

    async def delete(self, property_id: str | UUID) -> bool:
        """Delete a property by ID."""
        property_obj = await self.get_by_id(property_id)
        if not property_obj:
            return False

        await self.session.delete(property_obj)
        await self.session.flush()
        return True
