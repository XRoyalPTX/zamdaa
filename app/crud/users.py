from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import User
from app.schemas import UserCreate
from app.security import hash_password, verify_password


async def create_user(db: AsyncSession, user_schema: UserCreate):
    user_dict = user_schema.model_dump()

    password = user_dict["password"]
    user_dict["password"] = hash_password(password)

    db_user = User(**user_dict)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_phone_number(db: AsyncSession, phone_number: str):
    query = select(User).where(User.phone_number == phone_number)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, id: int):
    query = select(User).where(User.id == id)
    result = await db.execute(query)
    return result.scalar_one_or_none()