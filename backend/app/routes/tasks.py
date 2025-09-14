from datetime import datetime, timezone
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, delete


from app.core.rate_limiter import get_rate_limiter
from app.db.database import SessionDep
from app.db.users import get_current_active_user
from app.db.tasks import priority_desc, get_current_task, get_current_task_comment
from app.models.task import TaskCreate, TaskDB, TaskPublic, TaskUpdate
from app.models.task import TaskCommentCreate, TaskCommentPublic, TaskCommentDB, TaskCommentUpdate
from app.models.user import UserPublic


tasks_routers = APIRouter(prefix="/tasks", tags=["task"], dependencies=[Depends(get_rate_limiter)])

# -------------------------------------------------------------------------------------------------
# task 
# -------------------------------------------------------------------------------------------------

@tasks_routers.get("/", response_model=List[TaskPublic])
async def get_tasks(
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=20)] = 20,
    created_by: Optional[int] = None,
    assigned_to: Optional[int] = None,
    completed : Optional[bool] = None
) -> List[TaskPublic]:
    query = select(TaskDB)

    if created_by is not None:
        query = query.where(TaskDB.created_by == created_by)

    if assigned_to is not None:
        query = query.where(TaskDB.assigned_to == assigned_to)

    if completed is not None:
        query = query.where(TaskDB.completed == completed)

    query = query.offset(offset).limit(limit)
    tasks = session.exec(query).all()

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
    task: Annotated[TaskDB, Depends(get_current_task)],
    task_id: int,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    
    task_db_data = task.model_dump()
    task_db_data["priority"] = task.priority.desc if task.priority else None
    return TaskPublic.model_validate(task_db_data)


@tasks_routers.post("/", response_model=TaskPublic)
async def post_task(
    task: TaskCreate,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
) -> TaskPublic:
    # get data
    priority = await priority_desc(task.priority, session=session)
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
        priority_id=priority.id,
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
    task: Annotated[TaskDB, Depends(get_current_task)],
    task_id: int,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)]
):
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
    task_db: Annotated[TaskDB, Depends(get_current_task)],
    task: TaskUpdate,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)]
):
    task_data = task.model_dump(exclude_unset=True)
    task_data["updated_at"] = datetime.now(timezone.utc)
    if "priority" in task_data:
        priority = await priority_desc(task_data["priority"], session=session)
        task_data["priority_id"] = priority.id
    
    task_db.sqlmodel_update(task_data)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)

    task_db_data = task_db.model_dump()
    task_db_data["priority"] = task_db.priority.desc if task_db.priority else None
    return TaskPublic.model_validate(task_db_data)

# -------------------------------------------------------------------------------------------------
# task comments
# -------------------------------------------------------------------------------------------------

@tasks_routers.post("/{task_id}/comments", response_model=TaskCommentPublic)
async def post_comments(
    task: Annotated[TaskDB, Depends(get_current_task)],
    taskComment: TaskCommentCreate,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    if not taskComment.description:
        raise HTTPException(status_code=400, detail="Invalid task comment")        
    current_time = datetime.now(timezone.utc)
    taskcomment_db = TaskCommentDB.model_validate(
        taskComment,
        update={
            "task_id": task.id,
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


@tasks_routers.get("/{task_id}/comments/", response_model=List[TaskCommentPublic])
async def get_taskcomments(
    task: Annotated[TaskDB, Depends(get_current_task)],
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    taskcommments = session.exec(
        select(TaskCommentDB)
            .where(TaskCommentDB.task_id == task.id)
            .order_by(TaskCommentDB.created_at))
    return [ TaskCommentPublic.model_validate(item) for item in taskcommments ]


@tasks_routers.get("/{task_id}/comments/{task_comment_id}", response_model=TaskCommentPublic)
async def get_single_taskcomment(
    task_comment: Annotated[TaskCommentDB, Depends(get_current_task_comment)],
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    return TaskCommentPublic.model_validate(task_comment)


@tasks_routers.delete("/{task_id}/comments/{task_comment_id}")
async def delete_comment(
    task_comment: Annotated[TaskCommentDB, Depends(get_current_task_comment)],
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    taskcomment_data = task_comment.model_dump()
    session.delete(task_comment)
    session.commit()
    taskcomment_public = TaskCommentPublic.model_validate(taskcomment_data).model_dump()
    return { "success": True, "task": taskcomment_public }


@tasks_routers.put("/{task_id}/comments/{task_comment_id}", response_model=TaskCommentPublic)
async def update_comment(
    task_comment: Annotated[TaskCommentDB, Depends(get_current_task_comment)],
    taskcomment_update: TaskCommentUpdate,
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    taskcomment_data = taskcomment_update.model_dump(exclude_unset=True)
    task_comment.sqlmodel_update(taskcomment_data)
    session.add(task_comment)
    session.commit()
    session.refresh(task_comment)
    return TaskCommentPublic.model_validate(task_comment)

# -------------------------------------------------------------------------------------------------
# statistic
# -------------------------------------------------------------------------------------------------

@tasks_routers.get("/statistics")
async def get_statistics(
    session: SessionDep,
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
    created_by: Optional[int] = None,
    assigned_to: Optional[int] = None,
    completed : Optional[bool] = None,
    created_at_start: Optional[datetime] = None,  # inclusive
    created_at_end: Optional[datetime] = None,    # exclusive
    due_date_at_start: Optional[datetime] = None,
    due_date_at_end: Optional[datetime] = None,
):
    
    def create_stats_query():
        query = select(TaskDB)
        if created_by is not None:
            query = query.where(TaskDB.created_by == created_by)
        if assigned_to is not None:
            query = query.where(TaskDB.assigned_to == assigned_to)
        if created_at_start is not None:
            query = query.where(TaskDB.created_at >= created_at_start)
        if created_at_end is not None:
            query = query.where(TaskDB.created_at < created_at_end)
        if due_date_at_start is not None:
            query = query.where(TaskDB.due_date >= due_date_at_start)
        if due_date_at_end is not None:
            query = query.where(TaskDB.due_date < due_date_at_end)
        return query

    num_task_completed = all(session.exec(create_stats_query().where(TaskDB.completed == True)).all())
    num_task_no_completed = all(session.exec(create_stats_query().where(TaskDB.completed == False)).all())
    num_task_total = num_task_completed + num_task_no_completed
    return { 
        "detail": { 
            "completed": num_task_completed,
            "no_completed": num_task_no_completed,
            "total": num_task_total
        },
    }
