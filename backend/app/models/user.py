from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username : str = Field(index=True, nullable=False, unique=True)
    full_name : str | None = Field(default=None)
    email : str | None = Field(default=None, unique=True)
    phone : str | None = Field(default=None, unique=True)
    enabled : bool = Field(default=True, nullable=False)
    isadmin : bool = Field(default=False, nullable=False)


class UserCreate(UserBase):
    password : str = Field(nullable=False)


class UserDB(UserBase, table=True):

    __tablename__ = "users"

    id : int | None = Field(default=None, primary_key=True)
    hashed_password : str = Field(nullable=False)


class UserPublic(UserBase):
    id : int | None


class UserUpdate(UserBase):
    username: str | None = None
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    enabled: bool | None = None
    isadmin: bool | None = None
    password: str | None = None
