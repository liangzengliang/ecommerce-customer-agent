"""
项目管理接口
提供项目、成员、任务、风险、会议、文档、变更、评论的 CRUD。
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.demo_limit import check_demo_limit
from app.models.user import User
from app.models.project import (
    Project, ProjectMember, ProjectTask, ProjectRisk,
    ProjectMeeting, ProjectDocument, ProjectChange, ProjectComment,
)
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectMemberCreate, ProjectMemberResponse,
    ProjectTaskCreate, ProjectTaskUpdate, ProjectTaskResponse,
    ProjectRiskCreate, ProjectRiskUpdate, ProjectRiskResponse,
    ProjectMeetingCreate, ProjectMeetingUpdate, ProjectMeetingResponse,
    ProjectDocumentCreate, ProjectDocumentUpdate, ProjectDocumentResponse,
    ProjectChangeCreate, ProjectChangeUpdate, ProjectChangeResponse,
    ProjectCommentCreate, ProjectCommentResponse,
)

router = APIRouter()


# ============ 工具函数 ============
async def _get_project_or_404(db: AsyncSession, project_id: int) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


async def _check_member(db: AsyncSession, project_id: int, user_id: int) -> bool:
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def _require_member(db: AsyncSession, project_id: int, user: User):
    """普通成员及以上可读写"""
    if user.user_type == "admin":
        return
    if not await _check_member(db, project_id, user.id):
        raise HTTPException(status_code=403, detail="您不是该项目成员")


async def _require_owner(db: AsyncSession, project_id: int, user: User):
    """项目负责人/管理员可管理成员"""
    if user.user_type == "admin":
        return
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id,
            ProjectMember.role.in_(["owner", "admin"]),
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="需要项目负责人权限")


# ============ 项目 CRUD ============
@router.get("/list", response_model=List[ProjectResponse])
async def list_projects(
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """项目列表：管理员看全部，普通用户看自己参与的"""
    stmt = select(Project).order_by(Project.updated_at.desc())
    if user.user_type != "admin":
        member_ids = select(ProjectMember.project_id).where(ProjectMember.user_id == user.id)
        stmt = stmt.where(Project.id.in_(member_ids))
    if status:
        stmt = stmt.where(Project.status == status)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(Project.name.like(like) | Project.code.like(like))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/create", response_model=ProjectResponse)
async def create_project(
    body: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建项目，创建者自动成为 owner"""
    # 演示模式：数据上限校验
    if await check_demo_limit(db, Project):
        raise HTTPException(status_code=400, detail="演示模式每类数据最多 10 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。")

    project = Project(
        **body.model_dump(exclude={"owner_id"}),
        created_by=user.id,
        owner_id=body.owner_id or user.id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # 创建者自动加入成员表（owner）
    member = ProjectMember(project_id=project.id, user_id=user.id, role="owner")
    db.add(member)
    await db.commit()

    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    body: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_owner(db, project_id, user)

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_owner(db, project_id, user)
    await db.execute(delete(Project).where(Project.id == project_id))
    await db.commit()
    return {"success": True, "message": "项目已删除"}


# ============ 项目统计 ============
@router.get("/{project_id}/stats")
async def project_stats(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)

    async def _count(model):
        return (await db.execute(
            select(func.count(model.id)).where(model.project_id == project_id)
        )).scalar() or 0

    return {
        "project_id": project_id,
        "task_total": await _count(ProjectTask),
        "task_done": (await db.execute(
            select(func.count(ProjectTask.id)).where(
                ProjectTask.project_id == project_id,
                ProjectTask.status == "done",
            )
        )).scalar() or 0,
        "risk_open": (await db.execute(
            select(func.count(ProjectRisk.id)).where(
                ProjectRisk.project_id == project_id,
                ProjectRisk.status == "open",
            )
        )).scalar() or 0,
        "meeting_total": await _count(ProjectMeeting),
        "document_total": await _count(ProjectDocument),
        "change_open": (await db.execute(
            select(func.count(ProjectChange.id)).where(
                ProjectChange.project_id == project_id,
                ProjectChange.status == "proposed",
            )
        )).scalar() or 0,
        "member_total": await _count(ProjectMember),
        "comment_total": await _count(ProjectComment),
    }


# ============ 成员管理 ============
@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def list_members(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectMember).where(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.id)
    )
    members = result.scalars().all()
    items = []
    for m in members:
        u = (await db.execute(select(User).where(User.id == m.user_id))).scalar_one_or_none()
        items.append({
            "id": m.id,
            "project_id": m.project_id,
            "user_id": m.user_id,
            "role": m.role,
            "username": u.username if u else f"用户{m.user_id}",
            "joined_at": m.joined_at,
        })
    return items


@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
async def add_member(
    project_id: int,
    body: ProjectMemberCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_owner(db, project_id, user)

    # 检查用户存在
    u = (await db.execute(select(User).where(User.id == body.user_id))).scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 避免重复
    dup = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == body.user_id,
        )
    )
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该用户已是项目成员")

    # 演示模式：数据上限校验
    if await check_demo_limit(db, ProjectMember):
        raise HTTPException(status_code=400, detail="演示模式每类数据最多 10 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。")

    member = ProjectMember(project_id=project_id, user_id=body.user_id, role=body.role)
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return ProjectMemberResponse(
        id=member.id,
        project_id=member.project_id,
        user_id=member.user_id,
        role=member.role,
        username=u.username,
        joined_at=member.joined_at,
    )


@router.put("/{project_id}/members/{member_id}", response_model=ProjectMemberResponse)
async def update_member_role(
    project_id: int,
    member_id: int,
    body: ProjectMemberCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_owner(db, project_id, user)
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.id == member_id,
            ProjectMember.project_id == project_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    member.role = body.role
    await db.commit()
    await db.refresh(member)
    u = (await db.execute(select(User).where(User.id == member.user_id))).scalar_one_or_none()
    return ProjectMemberResponse(
        id=member.id,
        project_id=member.project_id,
        user_id=member.user_id,
        role=member.role,
        username=u.username if u else None,
        joined_at=member.joined_at,
    )


@router.delete("/{project_id}/members/{member_id}")
async def remove_member(
    project_id: int,
    member_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_owner(db, project_id, user)
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.id == member_id,
            ProjectMember.project_id == project_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    await db.delete(member)
    await db.commit()
    return {"success": True, "message": "成员已移除"}


# ============ 任务 ============
@router.get("/{project_id}/tasks", response_model=List[ProjectTaskResponse])
async def list_tasks(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectTask).where(ProjectTask.project_id == project_id)
        .order_by(ProjectTask.sort_order, ProjectTask.id)
    )
    return result.scalars().all()


@router.post("/{project_id}/tasks", response_model=ProjectTaskResponse)
async def create_task(
    project_id: int,
    body: ProjectTaskCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    # 演示模式：数据上限校验
    if await check_demo_limit(db, ProjectTask):
        raise HTTPException(status_code=400, detail="演示模式每类数据最多 10 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。")

    task = ProjectTask(**body.model_dump(), project_id=project_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.put("/{project_id}/tasks/{task_id}", response_model=ProjectTaskResponse)
async def update_task(
    project_id: int,
    task_id: int,
    body: ProjectTaskUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectTask).where(
            ProjectTask.id == task_id,
            ProjectTask.project_id == project_id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{project_id}/tasks/{task_id}")
async def delete_task(
    project_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectTask).where(
            ProjectTask.id == task_id,
            ProjectTask.project_id == project_id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    await db.delete(task)
    await db.commit()
    return {"success": True, "message": "任务已删除"}


# ============ 风险 ============
@router.get("/{project_id}/risks", response_model=List[ProjectRiskResponse])
async def list_risks(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectRisk).where(ProjectRisk.project_id == project_id)
        .order_by(ProjectRisk.id.desc())
    )
    return result.scalars().all()


@router.post("/{project_id}/risks", response_model=ProjectRiskResponse)
async def create_risk(
    project_id: int,
    body: ProjectRiskCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    # 演示模式：数据上限校验
    if await check_demo_limit(db, ProjectRisk):
        raise HTTPException(status_code=400, detail="演示模式每类数据最多 10 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。")

    risk = ProjectRisk(**body.model_dump(), project_id=project_id)
    db.add(risk)
    await db.commit()
    await db.refresh(risk)
    return risk


@router.put("/{project_id}/risks/{risk_id}", response_model=ProjectRiskResponse)
async def update_risk(
    project_id: int,
    risk_id: int,
    body: ProjectRiskUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectRisk).where(
            ProjectRisk.id == risk_id,
            ProjectRisk.project_id == project_id,
        )
    )
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="风险不存在")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(risk, field, value)
    await db.commit()
    await db.refresh(risk)
    return risk


@router.delete("/{project_id}/risks/{risk_id}")
async def delete_risk(
    project_id: int,
    risk_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectRisk).where(
            ProjectRisk.id == risk_id,
            ProjectRisk.project_id == project_id,
        )
    )
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="风险不存在")
    await db.delete(risk)
    await db.commit()
    return {"success": True, "message": "风险已删除"}


# ============ 会议 ============
@router.get("/{project_id}/meetings", response_model=List[ProjectMeetingResponse])
async def list_meetings(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectMeeting).where(ProjectMeeting.project_id == project_id)
        .order_by(ProjectMeeting.meeting_date.desc(), ProjectMeeting.id.desc())
    )
    return result.scalars().all()


@router.post("/{project_id}/meetings", response_model=ProjectMeetingResponse)
async def create_meeting(
    project_id: int,
    body: ProjectMeetingCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    # 演示模式：数据上限校验
    if await check_demo_limit(db, ProjectMeeting):
        raise HTTPException(status_code=400, detail="演示模式每类数据最多 10 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。")

    meeting = ProjectMeeting(**body.model_dump(), project_id=project_id)
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    return meeting


@router.put("/{project_id}/meetings/{meeting_id}", response_model=ProjectMeetingResponse)
async def update_meeting(
    project_id: int,
    meeting_id: int,
    body: ProjectMeetingUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectMeeting).where(
            ProjectMeeting.id == meeting_id,
            ProjectMeeting.project_id == project_id,
        )
    )
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(meeting, field, value)
    await db.commit()
    await db.refresh(meeting)
    return meeting


@router.delete("/{project_id}/meetings/{meeting_id}")
async def delete_meeting(
    project_id: int,
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectMeeting).where(
            ProjectMeeting.id == meeting_id,
            ProjectMeeting.project_id == project_id,
        )
    )
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    await db.delete(meeting)
    await db.commit()
    return {"success": True, "message": "会议已删除"}


# ============ 文档 ============
@router.get("/{project_id}/documents", response_model=List[ProjectDocumentResponse])
async def list_documents(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectDocument).where(ProjectDocument.project_id == project_id)
        .order_by(ProjectDocument.id.desc())
    )
    return result.scalars().all()


@router.post("/{project_id}/documents", response_model=ProjectDocumentResponse)
async def create_document(
    project_id: int,
    body: ProjectDocumentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    # 演示模式：数据上限校验
    if await check_demo_limit(db, ProjectDocument):
        raise HTTPException(status_code=400, detail="演示模式每类数据最多 10 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。")

    doc = ProjectDocument(**body.model_dump(), project_id=project_id, uploaded_by=user.id)
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.put("/{project_id}/documents/{doc_id}", response_model=ProjectDocumentResponse)
async def update_document(
    project_id: int,
    doc_id: int,
    body: ProjectDocumentUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectDocument).where(
            ProjectDocument.id == doc_id,
            ProjectDocument.project_id == project_id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.delete("/{project_id}/documents/{doc_id}")
async def delete_document(
    project_id: int,
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectDocument).where(
            ProjectDocument.id == doc_id,
            ProjectDocument.project_id == project_id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    await db.delete(doc)
    await db.commit()
    return {"success": True, "message": "文档已删除"}


# ============ 变更 ============
@router.get("/{project_id}/changes", response_model=List[ProjectChangeResponse])
async def list_changes(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectChange).where(ProjectChange.project_id == project_id)
        .order_by(ProjectChange.id.desc())
    )
    return result.scalars().all()


@router.post("/{project_id}/changes", response_model=ProjectChangeResponse)
async def create_change(
    project_id: int,
    body: ProjectChangeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    # 演示模式：数据上限校验
    if await check_demo_limit(db, ProjectChange):
        raise HTTPException(status_code=400, detail="演示模式每类数据最多 10 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。")

    change = ProjectChange(**body.model_dump(), project_id=project_id, requester_id=user.id)
    db.add(change)
    await db.commit()
    await db.refresh(change)
    return change


@router.put("/{project_id}/changes/{change_id}", response_model=ProjectChangeResponse)
async def update_change(
    project_id: int,
    change_id: int,
    body: ProjectChangeUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectChange).where(
            ProjectChange.id == change_id,
            ProjectChange.project_id == project_id,
        )
    )
    change = result.scalar_one_or_none()
    if not change:
        raise HTTPException(status_code=404, detail="变更不存在")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(change, field, value)
    await db.commit()
    await db.refresh(change)
    return change


@router.delete("/{project_id}/changes/{change_id}")
async def delete_change(
    project_id: int,
    change_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectChange).where(
            ProjectChange.id == change_id,
            ProjectChange.project_id == project_id,
        )
    )
    change = result.scalar_one_or_none()
    if not change:
        raise HTTPException(status_code=404, detail="变更不存在")
    await db.delete(change)
    await db.commit()
    return {"success": True, "message": "变更已删除"}


# ============ 评论 ============
@router.get("/{project_id}/comments", response_model=List[ProjectCommentResponse])
async def list_comments(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectComment).where(ProjectComment.project_id == project_id)
        .order_by(ProjectComment.id.desc())
        .limit(200)
    )
    comments = result.scalars().all()
    items = []
    for c in comments:
        u = (await db.execute(select(User).where(User.id == c.user_id))).scalar_one_or_none()
        items.append({
            "id": c.id,
            "project_id": c.project_id,
            "user_id": c.user_id,
            "content": c.content,
            "username": u.username if u else f"用户{c.user_id}",
            "created_at": c.created_at,
        })
    return items


@router.post("/{project_id}/comments", response_model=ProjectCommentResponse)
async def create_comment(
    project_id: int,
    body: ProjectCommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    # 演示模式：数据上限校验
    if await check_demo_limit(db, ProjectComment):
        raise HTTPException(status_code=400, detail="演示模式每类数据最多 10 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。")

    comment = ProjectComment(**body.model_dump(), project_id=project_id, user_id=user.id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    u = (await db.execute(select(User).where(User.id == user.id))).scalar_one_or_none()
    return ProjectCommentResponse(
        id=comment.id,
        project_id=comment.project_id,
        user_id=comment.user_id,
        content=comment.content,
        username=u.username if u else None,
        created_at=comment.created_at,
    )


@router.delete("/{project_id}/comments/{comment_id}")
async def delete_comment(
    project_id: int,
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_project_or_404(db, project_id)
    await _require_member(db, project_id, user)
    result = await db.execute(
        select(ProjectComment).where(
            ProjectComment.id == comment_id,
            ProjectComment.project_id == project_id,
        )
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    await db.delete(comment)
    await db.commit()
    return {"success": True, "message": "评论已删除"}