
from datetime import datetime

from sqlmodel import Field, ForeignKey, SQLModel

from models.user import UserDB
from sqlmodel import Session, select


class TaskPriority(SQLModel, table=True):

    __tablename__ = "task_priority"

    id : int = Field(primary_key=True)
    desc : str = Field(nullable=False)


class TaskStatus(SQLModel, table=True):

    __tablename__ = "task_status"

    id : int = Field(primary_key=True)
    desc : str = Field(nullable=False)



class TaskBase(SQLModel):
    title : str = Field(nullable=None)
    description : str | None = Field(default=None)
    priority : int | None =    Field(foreign_key="task_priority.id", nullable=True)
    created_by : int =  Field(foreign_key="users.id", nullable=False)
    assigned_to : int | None = Field(foreign_key="users.id", nullable=True)
    created_at : datetime = Field(nullable=False, index=True)
    updated_at : datetime = Field(default=None)
    due_date : datetime = Field(index=True)
    completed : bool = Field(default=False, nullable=False)


class TaskDB(TaskBase, table=True):

    __tablename__ = "tasks"

    id : int | None = Field(default=None, primary_key=True)


class TaskPublic(TaskBase):
    pass