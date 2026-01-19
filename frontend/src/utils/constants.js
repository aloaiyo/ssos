/**
 * 공통 상수 및 매핑 정의
 * 모든 뷰에서 일관된 색상/라벨을 사용하기 위한 중앙화된 정의
 */

// ===== 시즌 상태 =====
export const SEASON_STATUS = {
  upcoming: { color: 'info', label: '예정' },
  active: { color: 'success', label: '진행 중' },
  completed: { color: 'grey', label: '완료' },
}

export function getSeasonStatusColor(status) {
  return SEASON_STATUS[status]?.color || 'grey'
}

export function getSeasonStatusLabel(status) {
  return SEASON_STATUS[status]?.label || status
}

// ===== 세션 상태 =====
export const SESSION_STATUS = {
  scheduled: { color: 'info', label: '예정' },
  in_progress: { color: 'warning', label: '진행 중' },
  completed: { color: 'success', label: '완료' },
}

export function getSessionStatusColor(status) {
  return SESSION_STATUS[status]?.color || 'grey'
}

export function getSessionStatusLabel(status) {
  return SESSION_STATUS[status]?.label || status
}

// ===== 세션 타입 =====
export const SESSION_TYPE = {
  league: { color: 'primary', label: '리그전' },
  tournament: { color: 'secondary', label: '토너먼트' },
}

export function getSessionTypeColor(type) {
  return SESSION_TYPE[type]?.color || 'grey'
}

export function getSessionTypeLabel(type) {
  return SESSION_TYPE[type]?.label || type
}

// ===== 경기 상태 =====
export const MATCH_STATUS = {
  scheduled: { color: 'info', label: '예정' },
  in_progress: { color: 'warning', label: '진행 중' },
  completed: { color: 'success', label: '완료' },
}

export function getMatchStatusColor(status) {
  return MATCH_STATUS[status]?.color || 'grey'
}

export function getMatchStatusLabel(status) {
  return MATCH_STATUS[status]?.label || status
}

// ===== 경기 타입 =====
export const MATCH_TYPE = {
  mens_doubles: { color: 'blue', label: '남복', icon: 'mdi-gender-male' },
  womens_doubles: { color: 'pink', label: '여복', icon: 'mdi-gender-female' },
  mixed_doubles: { color: 'purple', label: '혼복', icon: 'mdi-gender-male-female' },
  singles: { color: 'orange', label: '단식', icon: 'mdi-account' },
}

export function getMatchTypeColor(type) {
  return MATCH_TYPE[type]?.color || 'grey'
}

export function getMatchTypeLabel(type) {
  return MATCH_TYPE[type]?.label || type
}

export function getMatchTypeIcon(type) {
  return MATCH_TYPE[type]?.icon || 'mdi-tennis'
}

// ===== 회원 역할 =====
export const MEMBER_ROLE = {
  manager: { color: 'primary', label: '매니저' },
  member: { color: 'success', label: '회원' },
  guest: { color: 'grey', label: '게스트' },
}

export function getMemberRoleColor(role) {
  return MEMBER_ROLE[role]?.color || 'grey'
}

export function getMemberRoleLabel(role) {
  return MEMBER_ROLE[role]?.label || role
}

// ===== 회원 상태 =====
export const MEMBER_STATUS = {
  pending: { color: 'warning', label: '승인 대기' },
  active: { color: 'success', label: '활성' },
  inactive: { color: 'grey', label: '비활성' },
  left: { color: 'error', label: '탈퇴' },
  banned: { color: 'error', label: '강퇴' },
}

export function getMemberStatusColor(status) {
  return MEMBER_STATUS[status]?.color || 'grey'
}

export function getMemberStatusLabel(status) {
  return MEMBER_STATUS[status]?.label || status
}

// ===== 성별 =====
export const GENDER = {
  male: { color: 'blue', label: '남성', icon: 'mdi-gender-male' },
  female: { color: 'pink', label: '여성', icon: 'mdi-gender-female' },
}

export function getGenderColor(gender) {
  return GENDER[gender]?.color || 'grey'
}

export function getGenderLabel(gender) {
  return GENDER[gender]?.label || gender
}

export function getGenderIcon(gender) {
  return GENDER[gender]?.icon || 'mdi-account'
}

// ===== 참가자 카테고리 =====
export const PARTICIPANT_CATEGORY = {
  member: { color: 'success', label: '정회원' },
  guest: { color: 'warning', label: '게스트' },
  associate: { color: 'info', label: '준회원' },
}

export function getParticipantCategoryColor(category) {
  return PARTICIPANT_CATEGORY[category]?.color || 'grey'
}

export function getParticipantCategoryLabel(category) {
  return PARTICIPANT_CATEGORY[category]?.label || category
}

// ===== 요일 =====
export const DAY_OF_WEEK = ['일', '월', '화', '수', '목', '금', '토']

export function getDayOfWeekLabel(dayIndex) {
  return DAY_OF_WEEK[dayIndex] || ''
}

// ===== 공지사항 타입 =====
export const ANNOUNCEMENT_TYPE = {
  general: { color: 'info', label: '일반' },
  important: { color: 'error', label: '중요' },
  event: { color: 'success', label: '이벤트' },
}

export function getAnnouncementTypeColor(type) {
  return ANNOUNCEMENT_TYPE[type]?.color || 'grey'
}

export function getAnnouncementTypeLabel(type) {
  return ANNOUNCEMENT_TYPE[type]?.label || type
}

// ===== 승률 계산 =====
export function calculateWinRate(wins, totalGames) {
  if (!totalGames || totalGames === 0) return 0
  return Math.round((wins / totalGames) * 100)
}

// ===== 순위 표시 =====
export function formatRank(rank) {
  if (!rank) return '-'
  return `${rank}위`
}
