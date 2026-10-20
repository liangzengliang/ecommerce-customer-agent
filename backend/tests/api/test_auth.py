"""
认证接口测试
覆盖注册、登录、单账号在线限制、退出清除模型配置等场景。
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
async def test_login_success(client):
    """测试登录成功（OAuth2 表单格式）"""
    username = "login_success_user"
    password = "pass123456"
    reg = await client.post("/api/v1/auth/register", json={
        "username": username,
        "password": password,
    })
    assert reg.status_code == 200
    token = reg.json()["access_token"]

    # 先退出，清除在线标记，再测试登录接口
    await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    resp = await client.post("/api/v1/auth/login", data={
        "username": username,
        "password": password,
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    """测试密码错误"""
    resp = await client.post("/api/v1/auth/login", data={
        "username": test_user["username"],
        "password": "wrong_password",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_chat_without_token(client):
    """测试未带 token 访问受保护接口"""
    resp = await client.post("/api/v1/chat", json={"message": "你好"})
    assert resp.status_code == 401


# ============ 演示版新增功能测试 ============

@pytest.mark.asyncio
async def test_second_login_same_account_conflict(client):
    """单账号单人在线：同一账号重复登录返回 409"""
    username = "online_user"
    password = "pass123456"
    # 注册（注册后自动在线）
    reg = await client.post("/api/v1/auth/register", json={
        "username": username,
        "password": password,
    })
    assert reg.status_code == 200

    # 再次登录同一账号 → 409
    resp = await client.post("/api/v1/auth/login", data={
        "username": username,
        "password": password,
    })
    assert resp.status_code == 409
    assert "已" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_logout_clears_online_then_relogin(client):
    """退出后清除在线标记，可再次登录"""
    username = "relogin_user"
    password = "pass123456"
    reg = await client.post("/api/v1/auth/register", json={
        "username": username,
        "password": password,
    })
    assert reg.status_code == 200
    token = reg.json()["access_token"]

    # 重复登录被拒
    dup = await client.post("/api/v1/auth/login", data={
        "username": username,
        "password": password,
    })
    assert dup.status_code == 409

    # 退出登录
    logout = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout.status_code == 200

    # 退出后可以再次登录
    login = await client.post("/api/v1/auth/login", data={
        "username": username,
        "password": password,
    })
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_logout_deletes_user_model_configs(client):
    """退出登录后自动删除该用户创建的模型配置"""
    username = "mc_user"
    password = "pass123456"
    reg = await client.post("/api/v1/auth/register", json={
        "username": username,
        "password": password,
    })
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 创建模型配置
    create = await client.post("/api/v1/models/create", json={
        "name": "test-llm",
        "provider": "openai",
        "type": "chat",
        "model": "gpt-3.5-turbo",
        "base_url": "https://api.openai.com/v1",
        "api_key": "sk-test",
        "temperature": 0.3,
        "max_tokens": 100,
    }, headers=headers)
    assert create.status_code == 200, create.text
    model_id = create.json()["id"]

    # 确认配置存在
    lst = await client.get("/api/v1/models/list", headers=headers)
    assert lst.status_code == 200
    ids = [m["id"] for m in lst.json()]
    assert model_id in ids

    # 退出登录
    logout = await client.post(
        "/api/v1/auth/logout",
        headers=headers,
    )
    assert logout.status_code == 200

    # 配置已被删除
    lst2 = await client.get("/api/v1/models/list", headers=headers)
    assert lst2.status_code == 200
    ids2 = [m["id"] for m in lst2.json()]
    assert model_id not in ids2
