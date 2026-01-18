"""Unit tests for MCP tools and services."""

import pytest

from src.exceptions import InvalidFilterError, PropertyNotFoundError
from src.repositories.property_repository import PropertyRepository
from src.services.content_generator import ContentGeneratorService
from src.services.property_service import PropertyService


class TestPropertyRepository:
    """Tests for PropertyRepository."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, test_session, sample_property):
        """Test getting a property by valid ID."""
        repo = PropertyRepository(test_session)
        result = await repo.get_by_id(str(sample_property.id))

        assert result is not None
        assert result.id == sample_property.id
        assert result.title == "Test Property"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, test_session):
        """Test getting a property by invalid ID."""
        repo = PropertyRepository(test_session)
        result = await repo.get_by_id("00000000-0000-0000-0000-000000000000")

        assert result is None

    @pytest.mark.asyncio
    async def test_search_by_city(self, test_session, sample_property):
        """Test searching properties by city."""
        repo = PropertyRepository(test_session)
        results = await repo.search(city="Lisbon")

        assert len(results) >= 1
        assert any(p.city == "Lisbon" for p in results)

    @pytest.mark.asyncio
    async def test_search_by_price_range(self, test_session, sample_property):
        """Test searching properties by price range."""
        repo = PropertyRepository(test_session)
        results = await repo.search(min_price=400000, max_price=600000)

        assert len(results) >= 1
        for prop in results:
            assert 400000 <= float(prop.price) <= 600000


class TestPropertyService:
    """Tests for PropertyService."""

    @pytest.mark.asyncio
    async def test_search_with_valid_filters(self, test_session, sample_property):
        """Test search with valid filters."""
        repo = PropertyRepository(test_session)
        service = PropertyService(repo)

        results = await service.search(city="Lisbon", status="available")

        assert isinstance(results, list)
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_search_invalid_price_range(self, test_session):
        """Test search with invalid price range raises error."""
        repo = PropertyRepository(test_session)
        service = PropertyService(repo)

        with pytest.raises(InvalidFilterError):
            await service.search(min_price=1000000, max_price=500000)

    @pytest.mark.asyncio
    async def test_search_negative_price(self, test_session):
        """Test search with negative price raises error."""
        repo = PropertyRepository(test_session)
        service = PropertyService(repo)

        with pytest.raises(InvalidFilterError):
            await service.search(min_price=-100)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found_raises(self, test_session):
        """Test get_by_id raises PropertyNotFoundError for invalid ID."""
        repo = PropertyRepository(test_session)
        service = PropertyService(repo)

        with pytest.raises(PropertyNotFoundError):
            await service.get_by_id("00000000-0000-0000-0000-000000000000")


class TestContentGeneratorService:
    """Tests for ContentGeneratorService."""

    def test_mock_description_professional(self):
        """Test mock description generation for professional tone."""
        service = ContentGeneratorService()
        prop = {
            "property_type": "apartment",
            "city": "Lisbon",
            "bedrooms": 3,
            "features": ["balcony", "parking", "elevator"],
        }

        result = service._mock_description(prop, "professional", "en")

        assert "apartment" in result
        assert "Lisbon" in result
        assert "3" in result

    def test_mock_description_casual(self):
        """Test mock description generation for casual tone."""
        service = ContentGeneratorService()
        prop = {
            "property_type": "villa",
            "city": "Porto",
            "bedrooms": 5,
            "features": ["garden", "pool"],
        }

        result = service._mock_description(prop, "casual", "en")

        assert "amazing" in result.lower() or "check out" in result.lower()
        assert "Porto" in result

    def test_mock_description_portuguese(self):
        """Test mock description generation in Portuguese."""
        service = ContentGeneratorService()
        prop = {
            "property_type": "apartamento",
            "city": "Lisboa",
            "bedrooms": 2,
            "features": ["varanda"],
        }

        result = service._mock_description(prop, "professional", "pt")

        assert "excepcional" in result.lower() or "Lisboa" in result
