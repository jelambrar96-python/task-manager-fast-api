from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.cors import add_cors_middleware
from app.db.database import create_db_and_tables, fill_task_priority_table, create_super_user
from app.routes.root import root_routers
from app.routes.tasks import tasks_routers
from app.routes.token import token_routes
from app.routes.users import users_routers
# from app.routes.task import task_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    fill_task_priority_table()
    create_super_user()
    yield


app = FastAPI(lifespan=lifespan)

add_cors_middleware(app=app)

app.include_router(root_routers)
app.include_router(tasks_routers)
app.include_router(users_routers)
app.include_router(token_routes)

