from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
from app.crud import get_user_by_id


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
    ):
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось валидировать учетные данные",
            headers={"WWW-Authenticate": "Bearer"}
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")

            if user_id is None:
                raise exception
        except jwt.PyJWTError:
            raise exception
        
        try:
            id = int(user_id)
        except ValueError:
            raise exception

        user = await get_user_by_id(db, id=id)
        if user is None:
            raise exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь заблокирован или не активирован"
            )
        
        return user