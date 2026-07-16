from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Location
from app.schemas import LocationCreate


async def create_location(db: AsyncSession, location_schema: LocationCreate):
    location_dict = location_schema.model_dump()

    db_location = Location(**location_dict)
    db.add(db_location)
    await db.commit()
    await db.refresh(db_location)
    return db_location


async def get_locations(db: AsyncSession):
    query = select(Location)
    result = await db.execute(query)

    return result.scalars().all()