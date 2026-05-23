from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_db
from app.models.user import User


async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


async def require_internal_secret(x_internal_secret: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if x_internal_secret != settings.internal_ingest_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid internal secret")


async def get_current_user_id(authorization: str | None = Header(default=None)) -> UUID:
    settings = get_settings()
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        subject = payload.get("sub")
        if not subject:
            raise ValueError("missing subject")
        return UUID(subject)
    except (JWTError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token") from exc


async def get_current_user_id_dep(user_id: UUID = Depends(get_current_user_id)) -> UUID:
    return user_id
