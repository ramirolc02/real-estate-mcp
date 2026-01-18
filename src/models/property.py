"""SQLAlchemy ORM model for properties."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, JSON, Index, String, Text, TypeDecorator, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Cross-database compatible type for JSONB
JSONBType = JSONB().with_variant(JSON(), "sqlite")


class UUIDType(TypeDecorator):
    """Platform-independent UUID type.

    Uses PostgreSQL's UUID type, otherwise uses String(36) and handles
    UUID <-> String conversion automatically.
    """

    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        # Convert UUID to string for non-PostgreSQL databases
        if isinstance(value, uuid.UUID):
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        # Convert string back to UUID for non-PostgreSQL databases
        if isinstance(value, str):
            return uuid.UUID(value)
        return value


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class Property(Base):
    """Property listing model."""

    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="available")
    property_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bedrooms: Mapped[int | None] = mapped_column(nullable=True)
    bathrooms: Mapped[int | None] = mapped_column(nullable=True)
    area_sqm: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    features: Mapped[list] = mapped_column(JSONBType, default=list)
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Indexes for efficient queries
    __table_args__ = (
        Index("idx_properties_city", "city"),
        Index("idx_properties_price", "price"),
        Index("idx_properties_status", "status"),
        Index("idx_properties_title_address", "title", "address", unique=True),
    )

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "city": self.city,
            "address": self.address,
            "price": float(self.price),
            "status": self.status,
            "property_type": self.property_type,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "area_sqm": float(self.area_sqm) if self.area_sqm else None,
            "features": self.features,
            "internal_notes": self.internal_notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_summary(self) -> dict:
        """Convert model to summary dictionary (for search results)."""
        return {
            "id": str(self.id),
            "title": self.title,
            "city": self.city,
            "price": float(self.price),
            "status": self.status,
            "property_type": self.property_type,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "area_sqm": float(self.area_sqm) if self.area_sqm else None,
        }
