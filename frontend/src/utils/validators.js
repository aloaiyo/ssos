// 유효성 검사 유틸리티

/**
 * 이메일 유효성 검사
 * @param {string} email
 * @returns {boolean|string} 유효하면 true, 아니면 에러 메시지
 */
export function validateEmail(email) {
  if (!email) return '이메일을 입력해주세요.'
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email) || '올바른 이메일 형식이 아닙니다.'
}

/**
 * 비밀번호 유효성 검사
 * @param {string} password
 * @returns {boolean|string} 유효하면 true, 아니면 에러 메시지
 */
export function validatePassword(password) {
  if (!password) return '비밀번호를 입력해주세요.'
  if (password.length < 8) return '비밀번호는 최소 8자 이상이어야 합니다.'
  if (!/[A-Za-z]/.test(password)) return '비밀번호에 영문자가 포함되어야 합니다.'
  if (!/[0-9]/.test(password)) return '비밀번호에 숫자가 포함되어야 합니다.'
  return true
}

/**
 * 필수 입력 검사
 * @param {any} value
 * @returns {boolean|string} 유효하면 true, 아니면 에러 메시지
 */
export function required(value) {
  if (value === null || value === undefined || value === '') {
    return '필수 입력 항목입니다.'
  }
  return true
}

/**
 * 최소 길이 검사
 * @param {number} min - 최소 길이
 * @returns {Function} 검사 함수
 */
export function minLength(min) {
  return (value) => {
    if (!value) return true
    if (value.length < min) {
      return `최소 ${min}자 이상 입력해주세요.`
    }
    return true
  }
}

/**
 * 최대 길이 검사
 * @param {number} max - 최대 길이
 * @returns {Function} 검사 함수
 */
export function maxLength(max) {
  return (value) => {
    if (!value) return true
    if (value.length > max) {
      return `최대 ${max}자까지 입력 가능합니다.`
    }
    return true
  }
}

/**
 * 숫자 범위 검사
 * @param {number} min - 최소값
 * @param {number} max - 최대값
 * @returns {Function} 검사 함수
 */
export function range(min, max) {
  return (value) => {
    if (value === null || value === undefined) return true
    const num = Number(value)
    if (isNaN(num)) return '숫자를 입력해주세요.'
    if (num < min || num > max) {
      return `${min}에서 ${max} 사이의 값을 입력해주세요.`
    }
    return true
  }
}

/**
 * 사용자명 유효성 검사
 * @param {string} username
 * @returns {boolean|string} 유효하면 true, 아니면 에러 메시지
 */
export function validateUsername(username) {
  if (!username) return '사용자명을 입력해주세요.'
  if (username.length < 3) return '사용자명은 최소 3자 이상이어야 합니다.'
  if (username.length > 20) return '사용자명은 최대 20자까지 가능합니다.'
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    return '사용자명은 영문자, 숫자, 밑줄(_)만 사용 가능합니다.'
  }
  return true
}

/**
 * 전화번호 유효성 검사
 * @param {string} phone
 * @returns {boolean|string} 유효하면 true, 아니면 에러 메시지
 */
export function validatePhone(phone) {
  if (!phone) return true // 선택 사항
  const phoneRegex = /^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$/
  return phoneRegex.test(phone) || '올바른 전화번호 형식이 아닙니다.'
}

/**
 * URL 유효성 검사
 * @param {string} url
 * @returns {boolean|string} 유효하면 true, 아니면 에러 메시지
 */
export function validateUrl(url) {
  if (!url) return true // 선택 사항
  try {
    new URL(url)
    return true
  } catch {
    return '올바른 URL 형식이 아닙니다.'
  }
}

/**
 * 비밀번호 확인 검사
 * @param {string} password - 원래 비밀번호
 * @returns {Function} 검사 함수
 */
export function confirmPassword(password) {
  return (value) => {
    if (!value) return '비밀번호 확인을 입력해주세요.'
    if (value !== password) return '비밀번호가 일치하지 않습니다.'
    return true
  }
}
