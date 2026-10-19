/**
 * 项目管理类型定义
 */

/** 项目状态 */
export type ProjectStatus = 'planning' | 'active' | 'paused' | 'completed' | 'archived'
/** 优先级 */
export type ProjectPriority = 'low' | 'medium' | 'high' | 'urgent'
/** 成员角色 */
export type ProjectMemberRole = 'owner' | 'admin' | 'member' | 'viewer'
/** 任务状态 */
export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done'
/** 风险等级 */
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'
/** 风险状态 */
export type RiskStatus = 'open' | 'mitigating' | 'closed'
/** 变更类型 */
export type ChangeType = 'scope' | 'schedule' | 'cost' | 'quality' | 'resource' | 'other'
/** 变更状态 */
export type ChangeStatus = 'proposed' | 'approved' | 'rejected' | 'implemented'

/** 项目 */
export interface Project {
  id: number
  name: string
  code?: string | null
  description?: string | null
  status: ProjectStatus
  priority: ProjectPriority
  owner_id?: number | null
  start_date?: string | null
  due_date?: string | null
  progress: number
  created_by?: number | null
  created_at?: string | null
  updated_at?: string | null
}

/** 项目成员 */
export interface ProjectMember {
  id: number
  project_id: number
  user_id: number
  role: ProjectMemberRole
  username?: string | null
  joined_at?: string | null
}

/** 项目任务 */
export interface ProjectTask {
  id: number
  project_id: number
  wbs_code?: string | null
  parent_id?: number | null
  title: string
  description?: string | null
  status: TaskStatus
  priority: ProjectPriority
  assignee_id?: number | null
  start_date?: string | null
  due_date?: string | null
  progress: number
  sort_order: number
  created_at?: string | null
  updated_at?: string | null
}

/** 项目风险 */
export interface ProjectRisk {
  id: number
  project_id: number
  title: string
  description?: string | null
  level: RiskLevel
  status: RiskStatus
  owner_id?: number | null
  mitigation?: string | null
  due_date?: string | null
  created_at?: string | null
  updated_at?: string | null
}

/** 项目会议 */
export interface ProjectMeeting {
  id: number
  project_id: number
  title: string
  meeting_date?: string | null
  location?: string | null
  attendees?: string | null
  agenda?: string | null
  minutes?: string | null
  created_at?: string | null
  updated_at?: string | null
}

/** 项目文档 */
export interface ProjectDocument {
  id: number
  project_id: number
  title: string
  doc_type: string
  url?: string | null
  content?: string | null
  version: string
  uploaded_by?: number | null
  created_at?: string | null
  updated_at?: string | null
}

/** 项目变更 */
export interface ProjectChange {
  id: number
  project_id: number
  title: string
  description?: string | null
  change_type: ChangeType
  status: ChangeStatus
  requester_id?: number | null
  impact?: string | null
  created_at?: string | null
  updated_at?: string | null
}

/** 项目评论 */
export interface ProjectComment {
  id: number
  project_id: number
  user_id: number
  content: string
  username?: string | null
  created_at?: string | null
}

/** 项目统计 */
export interface ProjectStats {
  project_id: number
  task_total: number
  task_done: number
  risk_open: number
  meeting_total: number
  document_total: number
  change_open: number
  member_total: number
  comment_total: number
}