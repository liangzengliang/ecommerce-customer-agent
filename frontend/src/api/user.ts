// /**
//  * 用户相关接口
//  */
// import api from './index'
//
// /** 登录参数 */
// export interface LoginParams {
//   username: string
//   password: string
// }
//
// /** 注册参数 */
// export interface RegisterParams {
//   username: string
//   password: string
//   email: string
//   phone?: string
// }
//
// /** 登录响应 */
// export interface LoginResponse {
//   access_token: string
//   token_type: string
//   user_id: number
//   username: string
// }
//
// /** 登录（后端用 OAuth2PasswordRequestForm，必须发 form 格式） */
// export function login(params: LoginParams) {
//   const formData = new URLSearchParams()
//   formData.append('username', params.username)
//   formData.append('password', params.password)
//   return api.post<any, LoginResponse>('/auth/login', formData, {
//     headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
//   })
// }
//
// /** 注册（后端用 Pydantic JSON 模型，发 JSON） */
// export function register(params: RegisterParams) {
//   return api.post<any, LoginResponse>('/auth/register', params)
// }

/**
 * 用户相关接口
 */
import api from './index'

/** 登录参数 */
export interface LoginParams {
  username: string
  password: string
}

/** 登录响应 */
export interface LoginResponse {
  access_token: string
  token_type: string
  user_id: number
  username: string
}

/**
 * 登录
 * 后端使用 OAuth2PasswordRequestForm，需要 form-urlencoded 格式：
 *   username=xxx&password=xxx
 * 且 Content-Type 必须是 application/x-www-form-urlencoded
 */
export function login(params: LoginParams) {
  const form = new URLSearchParams()
  form.append('username', params.username)
  form.append('password', params.password)

  return api.post<any, LoginResponse>('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

/**
 * 注册
 * 后端接收 JSON 格式
 */
export function register(params: LoginParams) {
  return api.post<any, LoginResponse>('/auth/register', params)
}