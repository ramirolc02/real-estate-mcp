"""Pydantic schemas for property validation."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class PropertyBase(BaseModel):
    """Base schema for property data."""

    title: str = Field(..., max_length=255, description="Property title")
    description: str | None = Field(None, description="Detailed description")
    city: str = Field(..., max_length=100, description="City location")
    address: str | None = Field(None, max_length=255, description="Full address")
    price: Decimal = Field(..., gt=0, description="Price in EUR")
    status: Literal["available", "sold"] = Field(
        default="available", description="Property status"
    )
    property_type: str | None = Field(None, max_length=50, description="Type of property")
    bedrooms: int | None = Field(None, ge=0, description="Number of bedrooms")
    bathrooms: int | None = Field(None, ge=0, description="Number of bathrooms")
    area_sqm: Decimal | None = Field(None, gt=0, description="Area in square meters")
    features: list[str] = Field(default_factory=list, description="List of features")
    internal_notes: str | None = Field(None, description="Internal notes (not for public)")


class PropertyCreate(PropertyBase):
    """Schema for creating a new property."""

    pass


class PropertyResponse(PropertyBase):
    """Schema for property response (includes ID and timestamps)."""

    id: str = Field(..., description="Unique property ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class PropertySummary(BaseModel):
    """Summary schema for search results."""

    id: str = Field(..., description="Unique property ID")
    title: str = Field(..., description="Property title")
    city: str = Field(..., description="City location")
    price: float = Field(..., description="Price in EUR")
    status: str = Field(..., description="Property status")
    property_type: str | None = Field(None, description="Type of property")
    bedrooms: int | None = Field(None, description="Number of bedrooms")
    bathrooms: int | None = Field(None, description="Number of bathrooms")
    area_sqm: float | None = Field(None, description="Area in square meters")

    model_config = {"from_attributes": True}


class PropertySearchFilters(BaseModel):
    """Schema for search filters."""

    city: str | None = Field(None, description="Filter by city name")
    min_price: float | None = Field(None, ge=0, description="Minimum price in EUR")
    max_price: float | None = Field(None, ge=0, description="Maximum price in EUR")
    status: Literal["available", "sold"] | None = Field(None, description="Property status")
