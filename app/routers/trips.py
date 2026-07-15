from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.schemas import TripCreate, TripResponse, TripRequestCreate, TripRequestResponse
from app.database import get_db
from app.crud import create_trip, create_trip_request, get_trips, change_trip_request_status
from typing import List
from app.api import get_current_user


router = APIRouter(prefix="/trips", tags=["Trips"])

@router.post("/", response_model=TripResponse)
async def add_trip(trip_data: TripCreate, db: AsyncSession = Depends(get_db), driver: User = Depends(get_current_user)):
    return await create_trip(db=db, trip_schema=trip_data, driver_id=driver.id)


@router.get("/", response_model=List[TripResponse])
async def read_trips(from_location_id: int | None = None, to_location_id: int | None = None, db: AsyncSession = Depends(get_db)):
    return await get_trips(db=db, from_location_id=from_location_id, to_location_id=to_location_id)


@router.post("/requests", response_model=TripRequestResponse)
async def add_trip_request(trip_request_data: TripRequestCreate, db: AsyncSession = Depends(get_db), requester: User = Depends(get_current_user)):
    return await create_trip_request(db=db, trip_request_schema=trip_request_data, requester_id=int(requester.id))


@router.patch("/requests/{trip_request_id}/status", response_model=TripRequestResponse)
async def update_trip_request_status(answer: bool, trip_request_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await change_trip_request_status(db=db, answer=answer, trip_request_id=trip_request_id, current_user_id=current_user.id)