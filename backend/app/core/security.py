from datetime import datetime, timezone, timedelta
from typing import Annotated

import jwt

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.core.config import HASH_ALGORITHM, SECRET_KEY, TOKEN_EXPIRED_TIME_MINUTES
from app.models.token import TokenData
from app.models.user import UserPublic


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        token_delta_time = int(TOKEN_EXPIRED_TIME_MINUTES) if TOKEN_EXPIRED_TIME_MINUTES else 80
        expire = datetime.now(timezone.utc) + timedelta(minutes=token_delta_time)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=HASH_ALGORITHM)
    return encoded_jwt
