from sqlalchemy.ext.asyncio import AsyncSession

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