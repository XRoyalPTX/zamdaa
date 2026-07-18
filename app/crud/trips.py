from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
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
    final_query = (
        select(Trip)
        .options(
            joinedload(Trip.driver),
            joinedload(Trip.from_location),
            joinedload(Trip.to_location)
        )
        .where(Trip.id == db_trip.id)
    )
    
    final_result = await db.execute(final_query)
    return final_result.scalar_one()


async def get_trips(db: AsyncSession, from_location_id: int | None = None, to_location_id: int | None = None):
    query = (
        select(Trip)
        .options(
            joinedload(Trip.driver),
            joinedload(Trip.from_location),
            joinedload(Trip.to_location)
        )
    )

    if from_location_id is not None:
        query = query.where(Trip.from_location_id == from_location_id)

    if to_location_id is not None:
        query = query.where(Trip.to_location_id == to_location_id)

    result = await db.execute(query)

    return result.scalars().all()


async def create_trip_request(db: AsyncSession, trip_request_schema: TripRequestCreate, requester_id: int):
    current_trip = await db.get(Trip, trip_request_schema.trip_id)
    if not current_trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Данная поездка не найдена"
        )
    
    if current_trip.driver_id == requester_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя отправлять заявку свою же поездку"
        )
    
    query = select(TripRequest).where(
        TripRequest.trip_id == trip_request_schema.trip_id,
        TripRequest.requester_id == requester_id,
        TripRequest.status != "cancelled"
    )
    result = await db.execute(query)
    existing_request = result.scalar_one_or_none()

    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У Вас уже есть заявка на данную поездку"
        )
    
    if current_trip.seats < trip_request_schema.seats_requested:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недостаточно свободных мест. Доступно: {current_trip.seats}"
        )

    trip_request_dict = trip_request_schema.model_dump()

    trip_request_dict["requester_id"] = requester_id
    trip_request_dict["status"] = "pending"

    db_trip_request = TripRequest(**trip_request_dict)
    db.add(db_trip_request)
    await db.commit()
    final_query = (
        select(TripRequest)
        .options(
            joinedload(TripRequest.requester),
            joinedload(TripRequest.trip).joinedload(Trip.driver),
            joinedload(TripRequest.trip).joinedload(Trip.from_location),
            joinedload(TripRequest.trip).joinedload(Trip.to_location)
        )
        .where(TripRequest.id == db_trip_request.id) 
    )
    
    final_result = await db.execute(final_query)
    return final_result.scalar_one()


async def change_trip_request_status(db: AsyncSession, answer: bool, trip_request_id: int, current_user_id: int):
    query = select(TripRequest).where(TripRequest.id == trip_request_id)
    result = await db.execute(query)
    trip_request = result.scalar_one_or_none()

    if not trip_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Не найдена заявка на поездку"
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
            detail="У вас нет прав для изменения статуса данной заявки" 
        )
    
    if trip_request.status not in ["pending", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно изменять статус только у заявок, ожидающих подтверждения"
        )

    if answer:
        if trip.seats < trip_request.seats_requested:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="К сожалению, места закончились"
            )
        trip.seats -= trip_request.seats_requested
        trip_request.status = "accepted"
        query = select(TripRequest).where(
            TripRequest.trip_id == trip.id,
            TripRequest.status == "pending",
            TripRequest.seats_requested > trip.seats
        )
        result = await db.execute(query)
        all_requests = result.scalars().all()

        for r in all_requests:
            r.status = "rejected"
    else:
        trip_request.status = "rejected"

    await db.commit()
    final_query = (
        select(TripRequest)
        .options(
            joinedload(TripRequest.requester),
            joinedload(TripRequest.trip).joinedload(Trip.driver),
            joinedload(TripRequest.trip).joinedload(Trip.from_location),
            joinedload(TripRequest.trip).joinedload(Trip.to_location)
        )
        .where(TripRequest.id == trip_request.id) 
    )
    
    final_result = await db.execute(final_query)
    return final_result.scalar_one()


async def cancel_trip_request(db: AsyncSession, trip_request_id: int, current_user_id: int):
    trip_request = await db.get(TripRequest, trip_request_id)
    if not trip_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Не найдена заявка на поездку"
        )
    
    trip = await db.get(Trip, trip_request.trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связанная поездка не найдена"
        )
    
    if trip_request.requester_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для изменения статуса данной заявки"
        )
    
    if trip_request.status == "cancelled" or trip_request.status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заявка уже отменена или отклонена"
        )
    
    if trip_request.status == "accepted":
        trip.seats += trip_request.seats_requested
    
    trip_request.status = "cancelled"

    await db.commit()
    final_query = (
        select(TripRequest)
        .options(
            joinedload(TripRequest.requester),
            joinedload(TripRequest.trip).joinedload(Trip.driver),
            joinedload(TripRequest.trip).joinedload(Trip.from_location),
            joinedload(TripRequest.trip).joinedload(Trip.to_location)
        )
        .where(TripRequest.id == trip_request.id) 
    )
    
    final_result = await db.execute(final_query)
    return final_result.scalar_one()