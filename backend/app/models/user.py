from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username : str = Field(index=True, nullable=False)
    full_name : str | None = Field(default=None)
    email : str | None = Field(default=None)
    phone : str | None = Field(default=None)


class UserCreate(UserBase):
    hashed_password : str = Field(nullable=False)
    enabled : bool = Field(default=True, nullable=False)
    isadmin : bool = Field(default=False, nullable=False)


class UserDB(UserCreate, table=True):

    __tablename__ = "users"

    id : int | None = Field(default=None, primary_key=True)


class UserPublic(UserBase):
    id : int | None


class UserUpdate(UserBase):
    username : str 
    full_name : str | None 
    email : str | None 
    phone : str | None 
    enabled : bool 
    isadmin : bool 
    hashed_password : str 