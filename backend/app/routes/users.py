from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select


from app.db.database import SessionDep
from app.db.users import get_current_active_admin_user, get_current_active_user
from app.models.user import UserCreate, UserDB, UserPublic, UserUpdate


users_routers = APIRouter(prefix="/users", tags=["task"])


@users_routers.get("/", response_model=list[UserPublic])
def read_heroes(
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_admin_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = session.exec(select(UserDB).offset(offset).limit(limit)).all()
    return users


@users_routers.post("/", response_model=UserPublic)
def post_user(
    hero: UserCreate,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_admin_user)],
):
    db_user = UserDB.model_validate(hero)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@users_routers.get("/{user_id}", response_model=UserPublic)
def read_user(
    user_id: int,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_admin_user)],
):
    user = session.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User no found")
    return user


@users_routers.patch("/{user_id}", response_model=UserPublic)
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
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@users_routers.get("/me", response_model=UserPublic)
def get_me(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    return current_user


@users_routers.patch("/me", response_model=UserPublic)
def update_me(
    useru: UserUpdate,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    user_id = current_user.id
    user_db = session.get(UserDB, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = useru.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

