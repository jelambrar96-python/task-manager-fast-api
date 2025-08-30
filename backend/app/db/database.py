from uuid import UUID
from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine, Field, select, Session, SQLModel

from core.config import DATABASE_URL, SUPERUSER_PASSWORD, SUPERUSER_USERNAME
from core.security import get_password_hash
from models.task import TaskDB, TaskPriority
from models.user import UserDB

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL)

db_config = { "autocommit": False, "autoflush": False}


def get_session():
    with Session(engine, **db_config) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def fill_task_priority_table():
    TASK_PRIORITIES = [
        TaskPriority(id=0, desc="Low"),
        TaskPriority(id=1, desc="Medium"),
        TaskPriority(id=2, desc="High"),
    ]
    s = next(get_session())
    for priority in TASK_PRIORITIES:
        exists = s.exec(select(TaskPriority).where(TaskPriority.id == priority.id)).first()
        if not exists:
            s.add(priority)
    s.commit()


def create_super_user():
    hashed_password = get_password_hash(SUPERUSER_PASSWORD)
    super_user = UserDB()
    super_user.username = SUPERUSER_USERNAME
    super_user.hashed_password = hashed_password
    super_user.isadmin=True
    s = next(get_session())
    exists = s.exec(
        select(UserDB)
        .where(UserDB.username == super_user.username)
    ).first()
    if not exists:
        s.add(super_user)
    s.commit()




SessionDep = Annotated[Session, Depends(get_session)]

