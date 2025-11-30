
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import pytest_asyncio
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from main import app
from core.db_helper import db_helper
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def db_session():
    """Единая сессия для FastAPI и тестов"""
    async with db_helper.session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """HTTP клиент, использующий ту же DB session"""

    app.dependency_overrides[db_helper.session_getter] = lambda: db_session

    transport = ASGITransport(app=app)

    async with LifespanManager(app):
        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as ac:
            yield ac

@pytest_asyncio.fixture
async def admin_token(client):
    response = await client.post(
        "/auth/login",
        json={"email": "admin@test.com", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def manager_token(client):
    response = await client.post(
        "/auth/login",
        json={"email": "manager@test.com", "password": "manager123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def user_token(client):
    response = await client.post(
        "/auth/login",
        json={"email": "user@test.com", "password": "user123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]

