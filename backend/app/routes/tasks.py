from datetime import datetime, timezone
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, delete


from app.db.database import SessionDep
from app.db.users import get_current_active_user
from app.db.tasks import priority_desc
from app.models.task import TaskCreate, TaskDB, TaskPublic, TaskUpdate
from app.models.task import TaskCommentCreate, TaskCommentPublic, TaskCommentDB #, TaskCommentPublic, TaskUpdate
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
    # remove comments of this task
    taskcomments = session.exec(
        delete(TaskCommentDB).where(TaskCommentDB.task_id == task_id))
    # coment
    session.commit()
    #
    task_data = TaskPublic.model_validate(task_db_data).model_dump()
    return { "success": True, "task": task_data }


@tasks_routers.put("/{task_id}", response_model=TaskPublic)
async def update_task(
    task: TaskUpdate,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)]
):
    task_db = session.exec(select(TaskDB).where(TaskDB.id == task.id)).first()
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = task.model_dump(exclude_unset=True)
    task_data["updated_at"] = datetime.now(timezone.utc)
    if "priority" in task_data:
        priority = priority_desc(task_data["priority"], session=session)
        if not priority:
            return HTTPException(status_code=404, detail="Priority not found")
        task_data["priority_id"] = priority.id
    
    task_db.sqlmodel_update(task_data)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)

    task_db_data = task_db.model_dump()
    task_db_data["priority"] = task_db.priority.desc if task_db.priority else None
    return TaskPublic.model_validate(task_db_data)

# task comments

@tasks_routers.post("/{task_id}/comments", response_model=TaskCommentPublic)
async def post_comments(
    task_id: int,
    taskComment: TaskCommentCreate,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    task_db = session.exec(select(TaskDB).where(TaskDB.id == task_id)).first()
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    if not taskComment.description:
        raise HTTPException(status_code=400, detail="Invalid task comment")        
    current_time = datetime.now(timezone.utc)
    taskcomment_db = TaskCommentDB.model_validate(
        taskComment,
        update={
            "task_id": task_id,
            "description": taskComment.description,
            "created_by": current_user.id,
            "created_at": current_time,
            "updated_at": current_time,
        }
    )
    session.add(taskcomment_db)
    session.commit()
    session.refresh(taskcomment_db)
    return TaskCommentPublic.model_validate(taskcomment_db)


@tasks_routers.get("/{task_id}/comments/", response_class=List[TaskCommentPublic])
async def get_taskcomments(
    task_id: int,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    task_db = session.exec(select(TaskDB).where(TaskDB.id == task_id)).first()
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    taskcommments = session.exec(
        select(TaskCommentDB)
            .where(TaskCommentDB.task_id == task_id)
            .order_by(TaskCommentDB.created_at))
    return [ TaskCommentPublic.model_validate(item) for item in taskcommments ]


@tasks_routers.get("/{task_id}/comments/{comment_id}", response_model=TaskCommentPublic)
async def get_single_taskcomment(
    task_id : int, 
    comment_id: int,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    task_db = session.exec(select(TaskDB).where(TaskDB.id == task_id)).first()
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    taskcommment = session.exec(
        select(TaskCommentDB)
            .where(TaskCommentDB.task_id == task_id and TaskCommentDB.id == comment_id)
        ).first()
    if not taskcommment:
        raise HTTPException(status_code=404, detail="Task Commentary not found")
    return TaskCommentPublic.model_validate(taskcommment)


@tasks_routers.delete("/{task_id}/comments/{comment_id}")
async def delete_comment(
    task_id: int,
    comment_id: int,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    task_db = session.exec(select(TaskDB).where(TaskDB.id == task_id)).first()
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    taskcommment = session.exec(
    select(TaskCommentDB)
        .where(TaskCommentDB.task_id == task_id and TaskCommentDB.id == comment_id)
    ).first()
    if not taskcommment:
        raise HTTPException(status_code=404, detail="Task Commentary not found")
    taskcomment_data = taskcommment.model_dump()
    session.delete(taskcommment)
    session.commit()
    taskcomment_public = TaskCommentPublic.model_validate(taskcomment_data).model_dump()
    return { "success": True, "task": taskcomment_public }


@tasks_routers.put("/{task_id}/comments/{comment_id}", response_model=TaskCommentPublic)
async def update_comment(
    task_id: int,
    comment_id: int,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    task_db = session.exec(select(TaskDB).where(TaskDB.id == task_id)).first()
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    taskcommment = session.exec(
    select(TaskCommentDB)
        .where(TaskCommentDB.task_id == task_id and TaskCommentDB.id == comment_id)
    ).first()
    if not taskcommment:
        raise HTTPException(status_code=404, detail="Task Commentary not found")
    taskcomment_data = taskcommment.model_dump(exclude_unset=True)
    taskcommment.sqlmodel_update(taskcomment_data)
    session.add(taskcommment)
    session.commit()
    session.refresh(taskcommment)
    return TaskCommentPublic.model_validate(taskcommment)

# statistic

@tasks_routers.get("/statistics")
async def get_statistics(
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)]
):
    return { "success": True }
