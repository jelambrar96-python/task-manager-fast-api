from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.database import create_db_and_tables, fill_task_priority_table, create_super_user
from routes.root import root_routers
from routes.tasks import tasks_routers
from routes.users import users_routers
# from app.routes.task import task_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    fill_task_priority_table()
    create_super_user()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(root_routers)
app.include_router(tasks_routers)
app.include_router(users_routers)
# app.include_router(task_routers)

