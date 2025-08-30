from enum import Enum
from pydantic import BaseModel


class TokenType(str, Enum):
    pass


class Token(BaseModel):
    access_token: str
    token_type : TokenType


class TokenData(BaseModel):
    username: str | None = None

