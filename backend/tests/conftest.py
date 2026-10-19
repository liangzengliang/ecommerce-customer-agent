"""
pytest 公共 fixture
提供测试用的数据库会话、HTTP 客户端、测试用户等。
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import Base, get_db

# 测试数据库（用独立库，避免污染开发库）
TEST_DATABASE_URL = "mysql+aiomysql://root:YOUR_DB_PASSWORD@YOUR_MYSQL_HOST:3306/customer_service"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    """为整个测试会话提供事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """测试开始前建表，结束后删表"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    """每个测试用例独立的事务会话"""
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
async def client(db_session):
    """提供覆盖了 get_db 的 HTTP 客户端"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(client):
    """注册一个测试用户并返回 token 和用户信息"""
    resp = await client.post("/api/v1/auth/register", json={
        "username": "pytest_user",
        "password": "pytest123456",
    })
    data = resp.json()
    return {
        "user_id": data["user_id"],
        "username": data["username"],
        "token": data["access_token"],
    }