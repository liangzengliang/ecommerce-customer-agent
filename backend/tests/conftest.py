"""
pytest 公共 fixture（演示模式 SQLite 版，无需 MySQL/Redis 即可运行测试）
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import Base, get_db
from app.core.sqlite_compat import create_all_sqlite

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_demo.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    await create_all_sqlite(test_engine)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(client):
    """复用测试用户：先清除在线标记，再登录；若不存在则注册"""
    from app.core.redis_client import get_redis
    redis = get_redis()
    await redis.delete("online:pytest_user")

    login = await client.post("/api/v1/auth/login", data={
        "username": "pytest_user",
        "password": "pytest123456",
    })
    if login.status_code == 200:
        data = login.json()
    else:
        reg = await client.post("/api/v1/auth/register", json={
            "username": "pytest_user",
            "password": "pytest123456",
        })
        data = reg.json()
    return {
        "user_id": data["user_id"],
        "username": data["username"],
        "token": data["access_token"],
    }
