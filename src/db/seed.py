"""Idempotent database seeding script."""

import asyncio
import uuid
from datetime import datetime, timedelta

from sqlalchemy.dialects.postgresql import insert

from src.db.session import async_session_maker, init_db
from src.models.property import Property

# Sample seed data - 8 properties across different cities, prices, and statuses
SEED_DATA = [
    {
        "id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
        "title": "Modern T3 Apartment in Lisbon",
        "description": "Stunning 3-bedroom apartment with panoramic river views in the heart of Lisbon. Recently renovated with high-end finishes.",
        "city": "Lisbon",
        "address": "Av. da Liberdade 120, 1250-096 Lisboa",
        "price": 650000,
        "status": "available",
        "property_type": "apartment",
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqm": 120.5,
        "features": ["balcony", "parking", "elevator", "river_view", "air_conditioning"],
        "internal_notes": "Owner motivated to sell. Open to negotiation up to 10%.",
    },
    {
        "id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
        "title": "Charming Villa in Porto",
        "description": "Historic villa with beautiful garden in central Porto. Original features preserved with modern amenities.",
        "city": "Porto",
        "address": "Rua das Flores 45, 4050-262 Porto",
        "price": 890000,
        "status": "available",
        "property_type": "villa",
        "bedrooms": 5,
        "bathrooms": 3,
        "area_sqm": 280.0,
        "features": ["garden", "garage", "fireplace", "renovated", "wine_cellar"],
        "internal_notes": "Heritage property. Requires special permits for modifications.",
    },
    {
        "id": uuid.UUID("33333333-3333-3333-3333-333333333333"),
        "title": "Cozy Studio in Alfama",
        "description": "Perfect investment opportunity in Lisbon's historic Alfama district. Ideal for short-term rentals.",
        "city": "Lisbon",
        "address": "Rua de São Miguel 15, 1100-544 Lisboa",
        "price": 195000,
        "status": "available",
        "property_type": "studio",
        "bedrooms": 0,
        "bathrooms": 1,
        "area_sqm": 35.0,
        "features": ["furnished", "city_view", "historic_building"],
        "internal_notes": "Tenant-occupied until March. High rental yield potential.",
    },
    {
        "id": uuid.UUID("44444444-4444-4444-4444-444444444444"),
        "title": "Luxury Penthouse in Foz",
        "description": "Exclusive penthouse with ocean views and private rooftop terrace in Porto's premium Foz district.",
        "city": "Porto",
        "address": "Av. do Brasil 200, 4150-153 Porto",
        "price": 1250000,
        "status": "available",
        "property_type": "penthouse",
        "bedrooms": 4,
        "bathrooms": 4,
        "area_sqm": 220.0,
        "features": ["ocean_view", "rooftop_terrace", "jacuzzi", "smart_home", "2_parking_spaces"],
        "internal_notes": "Premium client only. Requires proof of funds before viewing.",
    },
    {
        "id": uuid.UUID("55555555-5555-5555-5555-555555555555"),
        "title": "Family Home in Cascais",
        "description": "Spacious family home with pool in quiet Cascais neighborhood. Walking distance to beach.",
        "city": "Cascais",
        "address": "Rua da Palmeira 88, 2750-642 Cascais",
        "price": 980000,
        "status": "sold",
        "property_type": "house",
        "bedrooms": 4,
        "bathrooms": 3,
        "area_sqm": 195.0,
        "features": ["pool", "garden", "garage", "beach_nearby", "quiet_neighborhood"],
        "internal_notes": "Sold in January 2026. Final price: 950000 EUR.",
    },
    {
        "id": uuid.UUID("66666666-6666-6666-6666-666666666666"),
        "title": "Investment T1 in Baixa",
        "description": "Well-located 1-bedroom apartment in Porto's Baixa. Perfect for young professionals or investors.",
        "city": "Porto",
        "address": "Rua de Santa Catarina 350, 4000-442 Porto",
        "price": 285000,
        "status": "available",
        "property_type": "apartment",
        "bedrooms": 1,
        "bathrooms": 1,
        "area_sqm": 55.0,
        "features": ["central_location", "renovated", "elevator"],
        "internal_notes": "Great rental potential. Similar units rent for 1200 EUR/month.",
    },
    {
        "id": uuid.UUID("77777777-7777-7777-7777-777777777777"),
        "title": "Seaside Apartment in Estoril",
        "description": "Bright 2-bedroom apartment steps from Estoril beach. Includes parking and storage.",
        "city": "Estoril",
        "address": "Av. Marginal 500, 2765-272 Estoril",
        "price": 520000,
        "status": "available",
        "property_type": "apartment",
        "bedrooms": 2,
        "bathrooms": 1,
        "area_sqm": 85.0,
        "features": ["sea_view", "parking", "storage", "beach_front"],
        "internal_notes": "Owner relocating abroad. Quick sale preferred.",
        # Make this one recent for testing the daily listings resource
        "created_at": datetime.now() - timedelta(hours=12),
    },
    {
        "id": uuid.UUID("88888888-8888-8888-8888-888888888888"),
        "title": "Traditional Townhouse in Sintra",
        "description": "Unique 19th-century townhouse in UNESCO World Heritage Sintra. Needs renovation but full of charm.",
        "city": "Sintra",
        "address": "Rua Consiglieri Pedroso 12, 2710-550 Sintra",
        "price": 425000,
        "status": "sold",
        "property_type": "townhouse",
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqm": 150.0,
        "features": ["historic", "garden", "mountain_view", "needs_renovation"],
        "internal_notes": "Sold December 2025. Buyer plans full restoration.",
    },
]


async def seed_database() -> None:
    """Idempotent seeding - safe to run multiple times."""
    # Initialize tables first
    await init_db()

    async with async_session_maker() as session:
        inserted_count = 0
        for prop_data in SEED_DATA:
            # Use ON CONFLICT DO NOTHING for idempotent inserts
            stmt = (
                insert(Property).values(**prop_data).on_conflict_do_nothing(index_elements=["id"])
            )
            result = await session.execute(stmt)
            if result.rowcount > 0:
                inserted_count += 1

        await session.commit()
        print(
            f"Seeded {inserted_count} new properties (skipped {len(SEED_DATA) - inserted_count} existing)"
        )


def main() -> None:
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()
