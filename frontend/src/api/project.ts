/**
 * 项目管理接口
 */
import api from './index'
import type {
  Project, ProjectMember, ProjectTask, ProjectRisk,
  ProjectMeeting, ProjectDocument, ProjectChange, ProjectComment,
  ProjectStats, ProjectMemberRole, ProjectStatus,
} from '@/types/project'

// ============ 项目 ============
export function listProjects(params?: {
  status?: ProjectStatus | ''
  keyword?: string
}) {
  return api.get<any, Project[]>('/project/list', { params })
}

export function getProject(id: number) {
  return api.get<any, Project>(`/project/${id}`)
}

export function createProject(data: Partial<Project>) {
  return api.post<any, Project>('/project/create', data)
}

export function updateProject(id: number, data: Partial<Project>) {
  return api.put<any, Project>(`/project/${id}`, data)
}

export function deleteProject(id: number) {
  return api.delete(`/project/${id}`)
}

export function getProjectStats(id: number) {
  return api.get<any, ProjectStats>(`/project/${id}/stats`)
}

// ============ 成员 ============
export function listMembers(projectId: number) {
  return api.get<any, ProjectMember[]>(`/project/${projectId}/members`)
}

export function addMember(projectId: number, data: { user_id: number; role: ProjectMemberRole }) {
  return api.post<any, ProjectMember>(`/project/${projectId}/members`, data)
}

export function updateMemberRole(projectId: number, memberId: number, role: ProjectMemberRole) {
  return api.put<any, ProjectMember>(`/project/${projectId}/members/${memberId}`, { role })
}

export function removeMember(projectId: number, memberId: number) {
  return api.delete(`/project/${projectId}/members/${memberId}`)
}

// ============ 任务 ============
export function listTasks(projectId: number) {
  return api.get<any, ProjectTask[]>(`/project/${projectId}/tasks`)
}

export function createTask(projectId: number, data: Partial<ProjectTask>) {
  return api.post<any, ProjectTask>(`/project/${projectId}/tasks`, data)
}

export function updateTask(projectId: number, taskId: number, data: Partial<ProjectTask>) {
  return api.put<any, ProjectTask>(`/project/${projectId}/tasks/${taskId}`, data)
}

export function deleteTask(projectId: number, taskId: number) {
  return api.delete(`/project/${projectId}/tasks/${taskId}`)
}

// ============ 风险 ============
export function listRisks(projectId: number) {
  return api.get<any, ProjectRisk[]>(`/project/${projectId}/risks`)
}

export function createRisk(projectId: number, data: Partial<ProjectRisk>) {
  return api.post<any, ProjectRisk>(`/project/${projectId}/risks`, data)
}

export function updateRisk(projectId: number, riskId: number, data: Partial<ProjectRisk>) {
  return api.put<any, ProjectRisk>(`/project/${projectId}/risks/${riskId}`, data)
}

export function deleteRisk(projectId: number, riskId: number) {
  return api.delete(`/project/${projectId}/risks/${riskId}`)
}

// ============ 会议 ============
export function listMeetings(projectId: number) {
  return api.get<any, ProjectMeeting[]>(`/project/${projectId}/meetings`)
}

export function createMeeting(projectId: number, data: Partial<ProjectMeeting>) {
  return api.post<any, ProjectMeeting>(`/project/${projectId}/meetings`, data)
}

export function updateMeeting(projectId: number, meetingId: number, data: Partial<ProjectMeeting>) {
  return api.put<any, ProjectMeeting>(`/project/${projectId}/meetings/${meetingId}`, data)
}

export function deleteMeeting(projectId: number, meetingId: number) {
  return api.delete(`/project/${projectId}/meetings/${meetingId}`)
}

// ============ 文档 ============
export function listDocuments(projectId: number) {
  return api.get<any, ProjectDocument[]>(`/project/${projectId}/documents`)
}

export function createDocument(projectId: number, data: Partial<ProjectDocument>) {
  return api.post<any, ProjectDocument>(`/project/${projectId}/documents`, data)
}

export function updateDocument(projectId: number, docId: number, data: Partial<ProjectDocument>) {
  return api.put<any, ProjectDocument>(`/project/${projectId}/documents/${docId}`, data)
}

export function deleteDocument(projectId: number, docId: number) {
  return api.delete(`/project/${projectId}/documents/${docId}`)
}

// ============ 变更 ============
export function listChanges(projectId: number) {
  return api.get<any, ProjectChange[]>(`/project/${projectId}/changes`)
}

export function createChange(projectId: number, data: Partial<ProjectChange>) {
  return api.post<any, ProjectChange>(`/project/${projectId}/changes`, data)
}

export function updateChange(projectId: number, changeId: number, data: Partial<ProjectChange>) {
  return api.put<any, ProjectChange>(`/project/${projectId}/changes/${changeId}`, data)
}

export function deleteChange(projectId: number, changeId: number) {
  return api.delete(`/project/${projectId}/changes/${changeId}`)
}

// ============ 评论 ============
export function listComments(projectId: number) {
  return api.get<any, ProjectComment[]>(`/project/${projectId}/comments`)
}

export function createComment(projectId: number, content: string) {
  return api.post<any, ProjectComment>(`/project/${projectId}/comments`, { content })
}

export function deleteComment(projectId: number, commentId: number) {
  return api.delete(`/project/${projectId}/comments/${commentId}`)
}