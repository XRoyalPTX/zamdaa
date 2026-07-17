from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import LocationCreate, LocationResponse
from app.database import get_db
from app.crud import create_location, get_locations
from app.models import User
from app.api import check_is_staff
from typing import List


router = APIRouter(prefix="/locations", tags=["Locations"])

@router.post("/", response_model=LocationResponse)
async def add_location(
    location_data: LocationCreate, 
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(check_is_staff)
):
    return await create_location(db, location_data)


@router.get("/", response_model=List[LocationResponse])
async def read_locations(db: AsyncSession = Depends(get_db)):
    return await get_locations(db)