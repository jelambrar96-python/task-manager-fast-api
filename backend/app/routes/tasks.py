from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select


from db.database import SessionDep
from db.users import get_current_active_user
from models.task import TaskDB
from models.user import UserPublic


tasks_routers = APIRouter(prefix="/tasks", tags=["task"])


@tasks_routers.get("/")
def get_tasks(
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=20)] = 20
) -> list[TaskDB]:
    tasks = session.exec(select(TaskDB).offset(offset).limit(limit)).all()
    return tasks


@tasks_routers.post("/")
def post_task(
    task: TaskDB,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
) -> TaskDB:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@tasks_routers.delete("/{task_id}")
def delete_task(
    task_id: int,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)]
):
    task = session.get(TaskDB, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return { "success": True }


@tasks_routers.get("/statistics")
def get_statistics(
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)]
):
    return { "success": True }


@tasks_routers.post("/{task_id}/comments")
def post_comments(
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    return { "success": True }