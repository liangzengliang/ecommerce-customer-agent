"""
用户模型，对应 users 表。
存储普通用户、客服、管理员的基础信息。
"""

from sqlalchemy import Column, BigInteger, String, Enum, Boolean, SmallInteger, TIMESTAMP, text
from app.core.database import Base


class User(Base):
    """用户表 ORM 模型"""

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)      # 用户ID
    username = Column(String(50), nullable=False, unique=True)         # 用户名，唯一
    password_hash = Column(String(255), nullable=False)                # 密码哈希
    email = Column(String(100), unique=True)                           # 邮箱，唯一
    phone = Column(String(20), unique=True)                            # 手机号，唯一
    user_type = Column(Enum("customer", "agent", "admin"), default="customer")  # 用户类型
    avatar_url = Column(String(500))                                   # 头像URL
    is_active = Column(Boolean, default=True)                          # 是否激活
    status = Column(SmallInteger, default=1)                           # 状态：1正常 0禁用
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))                    # 创建时间
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))  # 更新时间