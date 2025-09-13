
import os
import time
import json

from datetime import datetime, timedelta, timezone

import pytest

from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient


from app.core.config import SUPERUSER_PASSWORD, SUPERUSER_USERNAME
from app.main import app

# load_dotenv()


@pytest.mark.asyncio
async def test_superuser_task_comments_flow():
    client = TestClient(app)
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
    auth_header = {"Authorization": f"Bearer {access_token}"}

    # 2. Crear una nueva tarea
    due_date = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    task_payload = {
        "title": "Task with comments",
        "description": "Testing task comments",
        "due_date": due_date,
        "completed": False,
        "priority": "High",
    }
    task_response = client.post("/tasks/", headers=auth_header, json=task_payload)
    assert task_response.status_code == 200
    task_data = task_response.json()
    task_id = task_data["id"]

    # 3. Agregar dos comentarios
    comment_payload1 = {"description": "First comment"}
    comment_payload2 = {"description": "Second comment"}
    comment1_response = client.post(f"/tasks/{task_id}/comments", headers=auth_header, json=comment_payload1)
    comment2_response = client.post(f"/tasks/{task_id}/comments", headers=auth_header, json=comment_payload2)

    assert comment1_response.status_code == 200
    assert comment2_response.status_code == 200

    comment1 = comment1_response.json()
    comment2 = comment2_response.json()
    
    print("comment1_response")
    print(json.dumps(comment1))

    print("comment2_response")
    print(json.dumps(comment2))       

    assert comment1["description"] == "First comment"
    assert comment2["description"] == "Second comment"

    # 4. Obtener un comentario específico (comment1)
    single_comment_response = client.get(f"/tasks/{task_id}/comments/{comment1['id']}", headers=auth_header)
    assert single_comment_response.status_code == 200
    single_comment = single_comment_response.json()
    print("single_comment")
    print(json.dumps(single_comment))
    assert single_comment["description"] == "First comment"

    # 5. Eliminar comment1
    delete_response = client.delete(f"/tasks/{task_id}/comments/{comment1['id']}", headers=auth_header)
    assert delete_response.status_code == 200
    delete_data = delete_response.json()
    print("delete_data")
    print(json.dumps(delete_data))
    assert delete_data["success"] is True

    # 6. Confirmar que comment1 ya no existe
    get_deleted_response = client.get(f"/tasks/{task_id}/comments/{comment1['id']}", headers=auth_header)        
    assert get_deleted_response.status_code == 404  # not found
    
    # 7. Editar el comentario que no fue eliminado (comment2)
    update_payload = {"description": "Updated second comment"}
    update_response = client.put(f"/tasks/{task_id}/comments/{comment2['id']}", headers=auth_header, json=update_payload)
    assert update_response.status_code == 200
    updated_comment = update_response.json()
    print("updated_comment")
    print(json.dumps(updated_comment))
    assert updated_comment["description"] == "Updated second comment"

    # 8. Confirmar que se modificaron los datos
    confirm_response = client.get(f"/tasks/{task_id}/comments/{comment2['id']}", headers=auth_header)
    assert confirm_response.status_code == 200
    confirmed_comment = confirm_response.json()
    print("confirmed_comment")
    print(json.dumps(confirmed_comment))
    assert confirmed_comment["description"] == "Updated second comment"
