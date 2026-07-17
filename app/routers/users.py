from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, UserResponse, UserPublicResponse
from app.database import get_db
from app.crud import create_user, get_user_by_phone_number, get_user_by_id
from app.security import verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from app.api import get_current_user
from app.models import User


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    return await create_user(db, user_data)


@router.post("/login")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_phone_number(db, phone_number=form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )
    
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )
    
    token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/{user_id}", response_model=UserPublicResponse)
async def stranger_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    needed_user = await get_user_by_id(db=db, id=user_id)

    if not needed_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return needed_user