from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status

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


async def change_trip_request_status(db: AsyncSession, answer: bool, trip_request_id: int, current_user_id: int):
    query = select(TripRequest).where(TripRequest.id == trip_request_id)
    result = await db.execute(query)
    trip_request = result.scalar_one_or_none()

    if not trip_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Не был найден запрос поездки"
        )
    
    query = select(Trip).where(Trip.id == trip_request.trip_id)
    result = await db.execute(query)
    trip = result.scalar_one_or_none()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связанная поездка не найдена"
        )

    if trip.driver_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для изменения статуса данного запроса" 
        )

    trip_request.status = "accepted" if answer else "rejected"
    await db.commit()
    await db.refresh(trip_request)
    
    return trip_request