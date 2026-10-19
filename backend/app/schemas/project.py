"""
项目管理 Pydantic Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


# ============ 项目 ============
class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    status: str = "planning"
    priority: str = "medium"
    owner_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    progress: int = 0


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    owner_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    progress: Optional[int] = Field(None, ge=0, le=100)


class ProjectResponse(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    status: str
    priority: str
    owner_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    progress: int
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ 成员 ============
class ProjectMemberCreate(BaseModel):
    user_id: int
    role: str = "member"


class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: str
    username: Optional[str] = None
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ 任务 ============
class ProjectTaskCreate(BaseModel):
    wbs_code: Optional[str] = Field(None, max_length=50)
    parent_id: Optional[int] = None
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    assignee_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    progress: int = 0
    sort_order: int = 0


class ProjectTaskUpdate(BaseModel):
    wbs_code: Optional[str] = None
    parent_id: Optional[int] = None
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    sort_order: Optional[int] = None


class ProjectTaskResponse(BaseModel):
    id: int
    project_id: int
    wbs_code: Optional[str] = None
    parent_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assignee_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    progress: int
    sort_order: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ 风险 ============
class ProjectRiskCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    level: str = "medium"
    status: str = "open"
    owner_id: Optional[int] = None
    mitigation: Optional[str] = None
    due_date: Optional[date] = None


class ProjectRiskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    level: Optional[str] = None
    status: Optional[str] = None
    owner_id: Optional[int] = None
    mitigation: Optional[str] = None
    due_date: Optional[date] = None


class ProjectRiskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    level: str
    status: str
    owner_id: Optional[int] = None
    mitigation: Optional[str] = None
    due_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ 会议 ============
class ProjectMeetingCreate(BaseModel):
    title: str = Field(..., max_length=200)
    meeting_date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    attendees: Optional[str] = None
    agenda: Optional[str] = None
    minutes: Optional[str] = None


class ProjectMeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    meeting_date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    attendees: Optional[str] = None
    agenda: Optional[str] = None
    minutes: Optional[str] = None


class ProjectMeetingResponse(BaseModel):
    id: int
    project_id: int
    title: str
    meeting_date: Optional[datetime] = None
    location: Optional[str] = None
    attendees: Optional[str] = None
    agenda: Optional[str] = None
    minutes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ 文档 ============
class ProjectDocumentCreate(BaseModel):
    title: str = Field(..., max_length=200)
    doc_type: str = "other"
    url: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    version: str = "v1.0"


class ProjectDocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    doc_type: Optional[str] = None
    url: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    version: Optional[str] = None


class ProjectDocumentResponse(BaseModel):
    id: int
    project_id: int
    title: str
    doc_type: str
    url: Optional[str] = None
    content: Optional[str] = None
    version: str
    uploaded_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ 变更 ============
class ProjectChangeCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    change_type: str = "scope"
    status: str = "proposed"
    requester_id: Optional[int] = None
    impact: Optional[str] = None


class ProjectChangeUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    change_type: Optional[str] = None
    status: Optional[str] = None
    requester_id: Optional[int] = None
    impact: Optional[str] = None


class ProjectChangeResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    change_type: str
    status: str
    requester_id: Optional[int] = None
    impact: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ 评论 ============
class ProjectCommentCreate(BaseModel):
    content: str = Field(..., max_length=5000)


class ProjectCommentResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    content: str
    username: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True