

from sqlmodel import select

from app.models.task import TaskPriority
from app.db.database import SessionDep


def priority_desc(
    desc: str,
    session: SessionDep,
    ) -> int:
    return session.exec(select(TaskPriority).where(TaskPriority.desc==desc)).first()


def priority_id(
    priority_id: id,
    session: SessionDep,
    ) -> str:
    return session.exec(TaskPriority, id=priority_id).first()
