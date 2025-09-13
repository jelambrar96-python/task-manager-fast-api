import os
import json

from datetime import datetime, timedelta, timezone

import pytest

from httpx import AsyncClient
from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import SUPERUSER_PASSWORD, SUPERUSER_USERNAME
from app.main import app
# from app.main import app  # importa tu app principal de FastAPI


@pytest.mark.asyncio
async def test_superuser_can_access_protected_route_and_create_task():
    client = TestClient(app=app)
    # 1. Login superuser
    token_response = client.post(
        "/token/",
        data={
            "username": SUPERUSER_USERNAME,
            "password": SUPERUSER_PASSWORD,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_response.status_code == status.HTTP_200_OK
    access_token = token_response.json()["access_token"]

    # 2. Usar el token en un endpoint protegido (/users/me)
    response = client.get(
        "/users/me/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == SUPERUSER_USERNAME

    # 3. Crear una nueva tarea
    due_date = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    task_payload = {
        "title": "Test Task",
        "description": "Tarea creada en test",
        "due_date": due_date,
        "completed": False,
        "priority": "High",
    }

    create_task_response = client.post(
        "/tasks/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=task_payload,
    )

    # 4. Validar la creación de la tarea
    task_data = create_task_response.json()
    print(json.dumps(task_data, indent=2))
    assert create_task_response.status_code == 200
    assert task_data["title"] == "Test Task"
    assert task_data["priority"] == "High"
    assert task_data["completed"] is False


@pytest.mark.asyncio
async def test_superuser_can_create_and_delete_task():
    client = TestClient(app=app)

    # 1. Login superuser
    token_response = client.post(
        "/token/",
        data={
            "username": SUPERUSER_USERNAME,
            "password": SUPERUSER_PASSWORD,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_response.status_code == status.HTTP_200_OK
    access_token = token_response.json()["access_token"]

    # 2. Crear una nueva tarea
    due_date = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    task_payload = {
        "title": "Task To Delete",
        "description": "Esta tarea será eliminada en el test",
        "due_date": due_date,
        "completed": False,
        "priority": "High",
    }

    create_task_response = client.post(
        "/tasks/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=task_payload,
    )
    assert create_task_response.status_code == status.HTTP_200_OK

    task_data = create_task_response.json()
    task_id = task_data["id"]

    # 3. Eliminar la tarea recién creada
    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == status.HTTP_200_OK

    deleted_task = delete_response.json()
    assert deleted_task["task"]["id"] == task_id
    assert deleted_task["task"]["title"] == "Task To Delete"

    # 4. Verificar que la tarea ya no existe (GET debe dar 404)
    get_response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_task():
    client = TestClient(app=app)

    # 1. Login superuser
    token_response = client.post(
        "/token/",
        data={
            "username": SUPERUSER_USERNAME,
            "password": SUPERUSER_PASSWORD,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_response.status_code == status.HTTP_200_OK
    access_token = token_response.json()["access_token"]

    # 2. Crear tarea inicial
    due_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    task_payload = {
        "title": "Initial Task",
        "description": "Descripción inicial",
        "due_date": due_date,
        "completed": False,
        "priority": "High",
    }

    create_response = client.post(
        "/tasks/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=task_payload,
    )
    assert create_response.status_code == 200
    task_data = create_response.json()
    task_id = task_data["id"]

    # 3. Actualizar tarea
    updated_payload = {
        "id": task_id,  # importante para el select en tu código
        "title": "Updated Task",
        "description": "Descripción actualizada",
        "completed": True,
        "priority": "Low",
    }

    update_response = client.put(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json=updated_payload,
    )

    # 4. Validaciones
    assert update_response.status_code == 200
    updated_task = update_response.json()
    print(json.dumps(updated_task, indent=2))

    assert updated_task["id"] == task_id
    assert updated_task["title"] == "Updated Task"
    assert updated_task["description"] == "Descripción actualizada"
    assert updated_task["completed"] is True
    assert updated_task["priority"] == "Low"