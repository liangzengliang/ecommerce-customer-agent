"""
认证接口
提供注册、登录，返回 JWT。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.demo_limit import check_demo_limit
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    用户注册
    参数：request - 含 username / password / email / phone
          db - 数据库会话
    返回：TokenResponse，含 JWT
    """
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 演示模式：注册用户数上限 10
    if await check_demo_limit(db, User):
        raise HTTPException(status_code=400, detail="演示模式注册用户最多 10 个，已达到上限，无法继续注册。数据将在次日凌晨 12 点自动恢复。")

    user = User(
        username=request.username,
        password_hash=hash_password(request.password),
        email=request.email,
        phone=request.phone,
        user_type="customer",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user_id=user.id, username=user.username)

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    用户登录（OAuth2 密码模式）
    参数：form_data - 含 username / password（form 表单）
          db - 数据库会话
    返回：TokenResponse，含 JWT
    """
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user_id=user.id, username=user.username)