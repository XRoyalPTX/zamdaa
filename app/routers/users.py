from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, UserResponse
from app.database import get_db
from app.crud import create_user


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user_data)
