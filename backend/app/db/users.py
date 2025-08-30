from typing import Annotated

import jwt

from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlmodel import select

from core.config import HASH_ALGORITHM, SECRET_KEY
from core.security import verify_password, oauth2_scheme
from db.database import get_session
from models.token import TokenData
from models.user import UserPublic, UserDB



def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[HASH_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
):
    if not current_user.enabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_admin_user(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    if not current_user.isadmin:
        raise HTTPException(status_code=401, detail="No permited")
    return current_user


async def get_user_by_username(username):
    s = next(get_session())
    exists = s.exec(
        select(UserDB)
        .where(UserDB.username == username)
    ).first()
    if not exists:
        return None
    return exists
