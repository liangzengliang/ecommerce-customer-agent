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


@pytest.mark.asyncio
async def test_model_config_isolated_between_users(client):
    """模型配置列表隔离：用户 A 的配置对用户 B 不可见"""
    # 用户 A
    reg_a = await client.post("/api/v1/auth/register", json={
        "username": "iso_user_a",
        "password": "pass123456",
    })
    assert reg_a.status_code == 200
    token_a = reg_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 用户 A 创建模型配置
    create = await client.post("/api/v1/models/create", json={
        "name": "secret-llm",
        "provider": "openai",
        "type": "chat",
        "model": "gpt-3.5-turbo",
        "base_url": "https://api.openai.com/v1",
        "api_key": "sk-secret",
        "temperature": 0.3,
        "max_tokens": 100,
    }, headers=headers_a)
    assert create.status_code == 200, create.text
    model_id = create.json()["id"]

    # 用户 B
    reg_b = await client.post("/api/v1/auth/register", json={
        "username": "iso_user_b",
        "password": "pass123456",
    })
    assert reg_b.status_code == 200
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 用户 B 的列表不包含 A 的配置
    lst_b = await client.get("/api/v1/models/list", headers=headers_b)
    assert lst_b.status_code == 200
    ids_b = [m["id"] for m in lst_b.json()]
    assert model_id not in ids_b

    # 用户 A 自己的列表包含该配置
    lst_a = await client.get("/api/v1/models/list", headers=headers_a)
    assert lst_a.status_code == 200
    ids_a = [m["id"] for m in lst_a.json()]
    assert model_id in ids_a



@pytest.mark.asyncio
async def test_relogin_resets_model_configs(client):
    """重新登录时自动清除该账号遗留的模型配置（防止他人复用 API Key）"""
    username = "relogin_reset_user"
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
        "name": "leaked-llm",
        "provider": "openai",
        "type": "chat",
        "model": "gpt-3.5-turbo",
        "base_url": "https://api.openai.com/v1",
        "api_key": "sk-leaked",
        "temperature": 0.3,
        "max_tokens": 100,
    }, headers=headers)
    assert create.status_code == 200, create.text
    model_id = create.json()["id"]

    # 先退出（清除在线标记），再重新登录（模拟退出后再次登录）
    logout = await client.post("/api/v1/auth/logout", headers=headers)
    assert logout.status_code == 200

    login2 = await client.post("/api/v1/auth/login", data={
        "username": username,
        "password": password,
    })
    assert login2.status_code == 200
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 旧模型配置已被清除
    lst = await client.get("/api/v1/models/list", headers=headers2)
    assert lst.status_code == 200
    ids = [m["id"] for m in lst.json()]
    assert model_id not in ids
