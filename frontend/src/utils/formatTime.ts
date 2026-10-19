/**
 * 时间格式化工具
 */
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

/** 格式化为 YYYY-MM-DD HH:mm:ss */
export function formatDateTime(value: string | Date): string {
  return dayjs(value).format('YYYY-MM-DD HH:mm:ss')
}

/** 格式化为 HH:mm */
export function formatTime(value: string | Date): string {
  return dayjs(value).format('HH:mm')
}

/** 相对时间：如 "3 分钟前" */
export function fromNow(value: string | Date): string {
  return dayjs(value).fromNow()
}