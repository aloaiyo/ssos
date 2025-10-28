// 날짜 유틸리티
import dayjs from 'dayjs'
import 'dayjs/locale/ko'
import relativeTime from 'dayjs/plugin/relativeTime'
import customParseFormat from 'dayjs/plugin/customParseFormat'

dayjs.locale('ko')
dayjs.extend(relativeTime)
dayjs.extend(customParseFormat)

/**
 * 날짜를 포맷팅
 * @param {string|Date} date - 날짜
 * @param {string} format - 포맷 (기본: YYYY-MM-DD)
 * @returns {string} 포맷팅된 날짜
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return ''
  return dayjs(date).format(format)
}

/**
 * 날짜와 시간을 포맷팅
 * @param {string|Date} date - 날짜
 * @param {string} format - 포맷 (기본: YYYY-MM-DD HH:mm)
 * @returns {string} 포맷팅된 날짜 시간
 */
export function formatDateTime(date, format = 'YYYY-MM-DD HH:mm') {
  if (!date) return ''
  return dayjs(date).format(format)
}

/**
 * 시간을 포맷팅
 * @param {string|Date} date - 날짜
 * @param {string} format - 포맷 (기본: HH:mm)
 * @returns {string} 포맷팅된 시간
 */
export function formatTime(date, format = 'HH:mm') {
  if (!date) return ''
  return dayjs(date).format(format)
}

/**
 * 상대 시간 표시 (예: 3일 전)
 * @param {string|Date} date - 날짜
 * @returns {string} 상대 시간
 */
export function fromNow(date) {
  if (!date) return ''
  return dayjs(date).fromNow()
}

/**
 * 날짜 차이 계산
 * @param {string|Date} date1 - 시작 날짜
 * @param {string|Date} date2 - 종료 날짜
 * @param {string} unit - 단위 (day, hour, minute 등)
 * @returns {number} 차이
 */
export function diffDate(date1, date2, unit = 'day') {
  return dayjs(date2).diff(dayjs(date1), unit)
}

/**
 * 날짜 유효성 검사
 * @param {string} date - 날짜 문자열
 * @returns {boolean} 유효 여부
 */
export function isValidDate(date) {
  return dayjs(date).isValid()
}

/**
 * 오늘 날짜
 * @returns {string} YYYY-MM-DD 형식
 */
export function today() {
  return dayjs().format('YYYY-MM-DD')
}

/**
 * 현재 시간
 * @returns {string} HH:mm 형식
 */
export function now() {
  return dayjs().format('HH:mm')
}

/**
 * 날짜 비교
 * @param {string|Date} date1
 * @param {string|Date} date2
 * @returns {boolean} date1이 date2보다 이전이면 true
 */
export function isBefore(date1, date2) {
  return dayjs(date1).isBefore(dayjs(date2))
}

/**
 * 날짜 비교
 * @param {string|Date} date1
 * @param {string|Date} date2
 * @returns {boolean} date1이 date2보다 이후면 true
 */
export function isAfter(date1, date2) {
  return dayjs(date1).isAfter(dayjs(date2))
}

export default dayjs
