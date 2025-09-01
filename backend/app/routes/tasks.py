from datetime import datetime, timezone
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select


from app.db.database import SessionDep
from app.db.users import get_current_active_user
from app.db.tasks import priority_desc
from app.models.task import TaskCreate, TaskDB, TaskPublic, TaskUpdate
from app.models.task import TaskCommentCreate # , TaskTaskCommentDB, TaskTaskCommentPublic, TaskUpdate
from app.models.user import UserPublic


tasks_routers = APIRouter(prefix="/tasks", tags=["task"])


@tasks_routers.get("/", response_model=list[TaskPublic])
async def get_tasks(
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=20)] = 20
) -> list[TaskPublic]:
    tasks = session.exec(select(TaskDB).offset(offset).limit(limit)).all()
    return [
        TaskPublic(
            id=t.id,
            title=t.title,
            description=t.description,
            assigned_to=t.assigned_to,
            created_at=t.created_at,
            due_date=t.due_date,
            completed=t.completed,
            updated_at=t.updated_at,
            priority=t.priority.desc if t.priority else None,
        )
        for t in tasks
    ]


@tasks_routers.get("/{task_id}", response_model=TaskPublic)
async def get_task(
    task_id: int,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    task_db = session.get(TaskDB, task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    # return data from taskpublic
    task_db_data = task_db.model_dump()
    task_db_data["priority"] = task_db.priority.desc if task_db.priority else None
    return TaskPublic.model_validate(task_db_data)


@tasks_routers.post("/", response_model=TaskPublic)
async def post_task(
    task: TaskCreate,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
) -> TaskPublic:
    # get data
    priority_id = None
    if task.priority:
        priority = priority_desc(task.priority, session=session)
        if not priority:
            return HTTPException(status_code=404, detail="Priority not found")
        priority_id = priority.id
    # db
    current_time = datetime.now(timezone.utc)
    task_db = TaskDB(
        title=task.title,
        description=task.description,
        assigned_to=task.assigned_to,
        created_at=current_time,
        due_date=task.due_date,
        completed=task.completed,
        created_by=current_user.id,
        updated_at=current_time,
        priority_id=priority_id,
    )
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    # return data from taskpublic
    task_db_data = task_db.model_dump()
    task_db_data["priority"] = task_db.priority.desc if task_db.priority else None
    return TaskPublic.model_validate(task_db_data)


@tasks_routers.delete("/{task_id}")
async def delete_task(
    task_id: int,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)]
):
    task = session.get(TaskDB, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_db_data = task.model_dump()
    task_db_data["priority"] = task.priority.desc if task.priority else None
    session.delete(task)
    session.commit()
    #
    task_data = TaskPublic.model_validate(task_db_data).model_dump()
    return { "success": True, "task": task_data }


# statistic

@tasks_routers.get("/statistics")
async def get_statistics(
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)]
):
    return { "success": True }

# task comments

@tasks_routers.post("/{task_id}/comments")
async def post_comments(
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    return { "success": True }


@tasks_routers.get("/{task_id}/comments")
async def post_comments(
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    return { "success": True }