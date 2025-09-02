
from datetime import datetime, timezone

from sqlmodel import Field, ForeignKey, SQLModel, Relationship
from sqlmodel import Session, select

from app.models.user import UserDB


# dim tables

class TaskPriority(SQLModel, table=True):

    __tablename__ = "task_priority"

    id : int = Field(primary_key=True)
    desc : str = Field(nullable=False, unique=True)

    tasks: list["TaskDB"] = Relationship(back_populates="priority")


class TaskStatus(SQLModel, table=True):

    __tablename__ = "task_status"

    id : int = Field(primary_key=True)
    desc : str = Field(nullable=False)

# task

class TaskBase(SQLModel):
    title : str | None = None
    description : str | None = None
    assigned_to : int | None = None
    created_at : datetime = datetime.now(timezone.utc)
    due_date : datetime = None
    completed : bool = False


class TaskDB(TaskBase, table=True):

    __tablename__ = "tasks"

    id : int | None = Field(default=None, primary_key=True)
    title : str = Field(nullable=None)
    description : str | None = Field(default=None)
    created_at : datetime = Field(nullable=False, index=True)
    due_date : datetime = Field(index=True)
    priority_id : int | None = Field(foreign_key="task_priority.id", nullable=True)
    created_by : int =  Field(foreign_key="users.id", nullable=False)
    assigned_to : int | None = Field(foreign_key="users.id", nullable=True)
    updated_at : datetime = Field(default=None)
    completed : bool = Field(default=False, nullable=False)

    priority: "TaskPriority" = Relationship(back_populates="tasks")



class TaskPublic(TaskBase):
    id : int | None
    updated_at : datetime = Field(default=None)
    priority : str | None


class TaskCreate(TaskBase):
    priority : str | None
    pass


class TaskUpdate(TaskBase):
    id : int | None
    title : str | None = None
    description : str | None = None
    priority : str | None = None
    created_by : int | None = None
    assigned_to : int | None = None
    due_date : datetime | None = None
    completed : bool | None = None


# task comments

class TaskCommentBase(SQLModel):
    task_id : int = None
    description : str = None
    created_by : int = None


class TaskCommentDB(TaskCommentBase, table=True):
    
    __tablename__ = "comments"

    id : int | None = Field(default=None, primary_key=True)
    task_id : int =  Field(foreign_key="tasks.id", nullable=False, index=True)
    description : str = Field(nullable=False)
    created_by : int =  Field(foreign_key="users.id", nullable=False)
    created_at : datetime = Field(nullable=False, index=True)
    updated_at : datetime = Field(nullable=False, index=True)


class TaskCommentCreate(TaskCommentBase):
    description : str = None


class TaskCommentUpdate(TaskCommentBase):
    description : str


class TaskCommentPublic(TaskCommentBase):
    id : int
    updated_at : datetime = None
    created_at : datetime = None
