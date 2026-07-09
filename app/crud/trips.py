from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import Trip, TripRequest
from app.schemas import TripCreate, TripRequestCreate

async def create_trip(db: AsyncSession, trip_schema: TripCreate, driver_id: int):
    trip_dict = trip_schema.model_dump()

    trip_dict["driver_id"] = driver_id

    db_trip = Trip(**trip_dict)
    db.add(db_trip)
    await db.commit()
    await db.refresh(db_trip)
    return db_trip


async def get_trips(db: AsyncSession, from_location_id: int | None = None, to_location_id: int | None = None):
    query = select(Trip)

    if from_location_id is not None:
        query = query.where(Trip.from_location_id == from_location_id)

    if to_location_id is not None:
        query = query.where(Trip.to_location_id == to_location_id)

    result = await db.execute(query)

    return result.scalars().all()


async def create_trip_request(db: AsyncSession, trip_request_schema: TripRequestCreate, requester_id: int):
    trip_request_dict = trip_request_schema.model_dump()

    trip_request_dict["requester_id"] = requester_id
    trip_request_dict["status"] = "pending"

    db_trip_request = TripRequest(**trip_request_dict)
    db.add(db_trip_request)
    await db.commit()
    await db.refresh(db_trip_request)
    return db_trip_request


async def change_trip_request_status(db: AsyncSession, answer: bool, trip_request_id: int):
    if answer:
        query = update(TripRequest).where(TripRequest.id == trip_request_id).values(status="accepted").returning(TripRequest)
    else:
        query = update(TripRequest).where(TripRequest.id == trip_request_id).values(status="rejected").returning(TripRequest)
    result = await db.execute(query)
    await db.commit()
    return result.scalar_one()