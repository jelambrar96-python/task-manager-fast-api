from typing import Annotated, List
from pydantic import ValidationError

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import select


from app.db.database import SessionDep
from app.db.users import get_current_active_admin_user, get_current_active_user
from app.models.user import UserCreate, UserDB, UserPublic, UserUpdate
from app.core.security import get_password_hash


users_routers = APIRouter(prefix="/users", tags=["users"])


@users_routers.get("/", response_model=List[UserPublic])
def read_users(
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_admin_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = session.exec(select(UserDB).offset(offset).limit(limit)).all()
    return users


@users_routers.post("/", response_model=UserPublic)
def post_user(
    user: UserCreate,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_admin_user)],
):
    try:
        hashed_pw = get_password_hash(user.password)
        db_user = UserDB.model_validate(user, update={"hashed_password": hashed_pw})
        # db_user = UserDB(
        #     username=user.username,
        #     full_name=user.full_name,
        #     email=user.email,
        #     phone=user.phone,
        #     enabled=user.enabled,
        #     isadmin=user.isadmin,
        #     hashed_password=hashed_pw,
        # )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except ValidationError:
        raise HTTPException(status_code=404, detail="User invalid")
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Username, email or phone already exists")
    return UserPublic.model_validate(db_user)


@users_routers.get("/{user_id}", response_model=UserPublic)
def read_user(
    user_id: int,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    user = session.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User no found")
    return user


@users_routers.put("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    useru: UserUpdate,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_admin_user)],
):
    user_db = session.get(UserDB, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = useru.model_dump(exclude_unset=True)
    # Hash password if provided
    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@users_routers.get("/me/", response_model=UserPublic)
def get_me(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    return current_user


@users_routers.patch("/me/", response_model=UserPublic)
def update_me(
    useru: UserUpdate,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    if useru.id != current_user.id:
        raise HTTPException(status_code=401, detail="Invalid change this user")
    user_id = current_user.id
    user_db = session.get(UserDB, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    # Hash password if provided
    user_data = useru.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


