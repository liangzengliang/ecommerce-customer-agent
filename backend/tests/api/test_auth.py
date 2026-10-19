"""
认证接口测试
覆盖注册、登录、鉴权失败等场景。
"""

import pytest

@pytest.mark.asyncio
async def test_register_success(client):
    """测试注册成功"""
    resp = await client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "password": "newpass123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["username"] == "newuser"

@pytest.mark.asyncio
async def test_register_duplicate(client, test_user):
    """测试用户名重复注册失败"""
    resp = await client.post("/api/v1/auth/register", json={
        "username": test_user["username"],
        "password": "anypass123",
    })
    assert resp.status_code == 400
    assert "已存在" in resp.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(client, test_user):
    """测试登录成功"""
    resp = await client.post("/api/v1/auth/login", json={
        "username": test_user["username"],
        "password": "pytest123456",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()

@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    """测试密码错误"""
    resp = await client.post("/api/v1/auth/login", json={
        "username": test_user["username"],
        "password": "wrong_password",
    })
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_chat_without_token(client):
    """测试未带 token 访问受保护接口"""
    resp = await client.post("/api/v1/chat", json={"message": "你好"})
    assert resp.status_code == 401