# tests/test_auth.py

import os
import pytest
from httpx import AsyncClient
from fastapi import status

from app.core.config import SUPERUSER_PASSWORD, SUPERUSER_USERNAME
# from app.main import app  # importa tu app principal de FastAPI


@pytest.mark.asyncio
async def test_superuser_can_login():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.post(
            "/token/",
            data={
                "username": SUPERUSER_USERNAME,
                "password": SUPERUSER_PASSWORD,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Verificar estructura del token
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_superuser_can_access_protected_route():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 1. Login
        token_response = await ac.post(
            "/token/",
            data={
                "username": SUPERUSER_USERNAME,
                "password": SUPERUSER_PASSWORD,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        access_token = token_response.json()["access_token"]

        # 2. Usar el token en un endpoint protegido
        response = await ac.get(
            "/users/me/",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == SUPERUSER_USERNAME


@pytest.mark.asyncio
async def test_superuser_can_create_user():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 1. Login superuser
        login_response = await ac.post(
            "/token/",
            data={
                "username": SUPERUSER_USERNAME,
                "password": SUPERUSER_PASSWORD,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 2. Create new user
        new_user = {
            "username": "alice",
            "email": "alice@example.com",
            "full_name": "Alice Wonderland",
            "password": "alicepassword"
        }

        create_response = await ac.post(
            "/users/",
            json=new_user,
            headers={"Authorization": f"Bearer {token}"},
        )

    # 3. Verificar
    assert create_response.status_code in [200, 400]
    data = create_response.json()

    if create_response.status_code == 200:
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["enabled"] is True

    if create_response.status_code == 200:
        assert data["result"] == "Username, email or phone already exists"



@pytest.mark.asyncio
async def test_update_user():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 1. Login superuser
        login_response = await ac.post(
            "/token/",
            data={
                "username": SUPERUSER_USERNAME,
                "password": SUPERUSER_PASSWORD,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Crear un usuario nuevo
        new_user = {
            "username": "bob",
            "email": "bob@example.com",
            "full_name": "Bob Builder",
            "phone": "123456",
            "enabled": True,
            "isadmin": False,
            "password": "bobpassword",
        }
        create_response = await ac.post("/users/", json=new_user, headers=headers)
        assert create_response.status_code in [200]
        created_user = create_response.json()
        user_id = created_user["id"]

        # obtener el usuario guardado
        read_response = await ac.get(f"/users/{user_id}", headers=headers)
        assert read_response.status_code in [200]
        readed_user = create_response.json()
        assert readed_user["id"] == user_id
        assert readed_user["full_name"] == "Bob Builder"
        assert readed_user["email"] == "bob@example.com"
        assert readed_user["enabled"] is True

        # 3. Actualizar el usuario
        update_payload = {
            "full_name": "Bob The Builder",
            "email": "bob.builder@example.com",
            "enabled": False,
        }
        update_response = await ac.patch(
            f"/users/{user_id}", json=update_payload, headers=headers)
        
        updated_user = update_response.json()
        print(updated_user)
        assert update_response.status_code == 200

        assert updated_user["id"] == user_id
        assert updated_user["full_name"] == "Bob The Builder"
        assert updated_user["email"] == "bob.builder@example.com"
        assert updated_user["enabled"] is False

        # 4. Confirmar que "password" no está en la respuesta
        assert "password" not in updated_user
        assert "hashed_password" not in updated_user


@pytest.mark.asyncio
async def test_non_admin_cannot_access_user_list():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 1. Login superuser
        login_response = await ac.post(
            "/token/",
            data={"username": SUPERUSER_USERNAME, "password": SUPERUSER_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_response.status_code == 200
        super_token = login_response.json()["access_token"]
        super_headers = {"Authorization": f"Bearer {super_token}"}

        # 2. Crear un usuario SIN permisos admin
        new_user = {
            "username": "charlie",
            "email": "charlie@example.com",
            "full_name": "Charlie Normal",
            "phone": "999999",
            "enabled": True,
            "isadmin": False,   # no es admin
            "password": "charliepassword",
        }
        create_response = await ac.post("/users/", json=new_user, headers=super_headers)
        assert create_response.status_code == 200

        # 3. Login del usuario normal
        login_user_response = await ac.post(
            "/token/",
            data={"username": "charlie", "password": "charliepassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_user_response.status_code == 200
        user_token = login_user_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # 4. Usuario normal intenta acceder a la lista de usuarios
        response = await ac.get("/users/", headers=user_headers)

        # 5. Debe fallar por falta de permisos
        assert response.status_code == 403 or response.status_code == 401
        body = response.json()
        assert "detail" in body
        assert "Not enough permissions" in body["detail"] or "forbidden" in body["detail"].lower()


