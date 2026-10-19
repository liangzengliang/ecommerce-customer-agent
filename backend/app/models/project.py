"""
项目管理模块 ORM 模型
涵盖：项目、成员、任务、风险、会议、文档、变更、评论。
"""

from sqlalchemy import (
    Column, BigInteger, String, Enum, Integer, Boolean, DATETIME, TIMESTAMP,
    Date, TEXT, ForeignKey, text,
)
from app.core.database import Base


class Project(Base):
    """项目表"""

    __tablename__ = "projects"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True)
    description = Column(TEXT)
    status = Column(
        Enum("planning", "active", "paused", "completed", "archived"),
        default="planning",
    )
    priority = Column(Enum("low", "medium", "high", "urgent"), default="medium")
    owner_id = Column(BigInteger, ForeignKey("users.id"))
    start_date = Column(Date)
    due_date = Column(Date)
    progress = Column(Integer, default=0)
    created_by = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class ProjectMember(Base):
    """项目成员表"""

    __tablename__ = "project_members"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    role = Column(Enum("owner", "admin", "member", "viewer"), default="member")
    joined_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class ProjectTask(Base):
    """项目任务表"""

    __tablename__ = "project_tasks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    wbs_code = Column(String(50))
    parent_id = Column(BigInteger, ForeignKey("project_tasks.id", ondelete="CASCADE"))
    title = Column(String(200), nullable=False)
    description = Column(TEXT)
    status = Column(Enum("todo", "in_progress", "review", "done"), default="todo")
    priority = Column(Enum("low", "medium", "high", "urgent"), default="medium")
    assignee_id = Column(BigInteger, ForeignKey("users.id"))
    start_date = Column(Date)
    due_date = Column(Date)
    progress = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class ProjectRisk(Base):
    """项目风险表"""

    __tablename__ = "project_risks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(TEXT)
    level = Column(Enum("low", "medium", "high", "critical"), default="medium")
    status = Column(Enum("open", "mitigating", "closed"), default="open")
    owner_id = Column(BigInteger, ForeignKey("users.id"))
    mitigation = Column(TEXT)
    due_date = Column(Date)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class ProjectMeeting(Base):
    """项目会议表"""

    __tablename__ = "project_meetings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    meeting_date = Column(DATETIME)
    location = Column(String(200))
    attendees = Column(TEXT)
    agenda = Column(TEXT)
    minutes = Column(TEXT)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class ProjectDocument(Base):
    """项目文档表"""

    __tablename__ = "project_documents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    doc_type = Column(String(50), default="other")
    url = Column(String(500))
    content = Column(TEXT)
    version = Column(String(20), default="v1.0")
    uploaded_by = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class ProjectChange(Base):
    """项目变更表"""

    __tablename__ = "project_changes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(TEXT)
    change_type = Column(Enum("scope", "schedule", "cost", "quality", "resource", "other"), default="scope")
    status = Column(Enum("proposed", "approved", "rejected", "implemented"), default="proposed")
    requester_id = Column(BigInteger, ForeignKey("users.id"))
    impact = Column(TEXT)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class ProjectComment(Base):
    """项目动态/评论表"""

    __tablename__ = "project_comments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))