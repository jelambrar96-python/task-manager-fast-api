from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import select

from app.models.task import TaskPriority, TaskDB, TaskCommentDB
from app.db.database import SessionDep, get_session


async def priority_desc(
    desc: str,
    session: Annotated[SessionDep, Depends(get_session)]
    ) -> TaskPriority:
    priority = session.exec(
            select(TaskPriority).where(TaskPriority.desc==desc)).first()
    if not priority:
        return HTTPException(status_code=404, detail="Priority not found")
    return priority


async def priority_id(
    priority_id: id,
    session: Annotated[SessionDep, Depends(get_session)]
    ) -> TaskPriority:
    priority =  session.exec(
            select(TaskPriority).where(TaskPriority.id==priority_id)).first()
    if not priority:
        return HTTPException(status_code=404, detail="Priority not found")
    return priority


async def get_current_task(
    task_id: int,
    session: Annotated[SessionDep, Depends(get_session)]
    ):
    task = session.exec(select(TaskDB).where(TaskDB.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


async def get_current_task_comment(
    task_id: int,
    task_comment_id: int,
    task: Annotated[TaskDB, Depends(get_current_task)],
    session: Annotated[SessionDep, Depends(get_session)]
    ):
    task_comment = session.exec(
        select(TaskCommentDB)
            .where(TaskCommentDB.task_id == task_id)
            .where(TaskCommentDB.id == task_comment_id)).first()
    if not task_comment:
        raise HTTPException(status_code=404, detail="Task Comentary not found")
    return task_comment
         
    
