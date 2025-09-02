import pytest
from sqlalchemy import inspect
from app.models import users, dataset
from app.db import Base, engine
# import importlib 
# importlib.reload(importlib.import_module("app.models"))
# importlib.reload(importlib.import_module("app.db"))

@pytest.fixture(scope="module")
def inspector():
    return inspect(engine)

def test_users_tables_created(inspector):
    expected_tables = [table.__tablename__ for table in Base.__subclasses__() if table.__module__ == 'backend.models.user']
    for table_name in expected_tables:
        assert inspector.has_table(table_name), f"Table '{table_name}' not created in users models"

def test_dataset_tables_created(inspector):
    expected_tables = [table.__tablename__ for table in Base.__subclasses__() if table.__module__ == 'backend.models.dataset']
    for table_name in expected_tables:
        assert inspector.has_table(table_name), f"Table '{table_name}' not created in dataset models"
