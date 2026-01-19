/**
 * 인증 관련 API (HTTP-only 쿠키 기반)
 */
import apiClient from './index'

// Cognito 환경변수
const COGNITO_DOMAIN = import.meta.env.VITE_COGNITO_DOMAIN
const COGNITO_CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID
const COGNITO_REDIRECT_URI = import.meta.env.VITE_COGNITO_REDIRECT_URI
const COGNITO_SIGN_OUT_URI = import.meta.env.VITE_COGNITO_SIGN_OUT_URI

/**
 * 구글 로그인 URL 생성 (Cognito Hosted UI)
 * @returns {string} 구글 로그인 URL
 */
export function getGoogleLoginUrl() {
  const params = new URLSearchParams({
    client_id: COGNITO_CLIENT_ID,
    response_type: 'code',
    scope: 'openid email profile',
    redirect_uri: COGNITO_REDIRECT_URI,
    identity_provider: 'Google',
  })
  return `${COGNITO_DOMAIN}/oauth2/authorize?${params.toString()}`
}

/**
 * Cognito 로그아웃 URL 생성
 * @returns {string} 로그아웃 URL
 */
export function getCognitoLogoutUrl() {
  const params = new URLSearchParams({
    client_id: COGNITO_CLIENT_ID,
    logout_uri: COGNITO_SIGN_OUT_URI,
  })
  return `${COGNITO_DOMAIN}/logout?${params.toString()}`
}

export default {
  /**
   * 회원가입 (이메일 인증번호 발송)
   * @param {string} email - 이메일
   * @param {string} password - 비밀번호
   * @param {string} name - 이름
   * @returns {Promise} 인증번호 발송 결과
   */
  async register(email, password, name) {
    const response = await apiClient.post('/auth/register', {
      email,
      password,
      name,
    })
    return response
  },

  /**
   * 이메일 인증번호 확인
   * @param {string} email - 이메일
   * @param {string} code - 인증번호 (6자리)
   * @returns {Promise} 로그인 결과 (쿠키 자동 설정)
   */
  async verifyEmail(email, code) {
    const response = await apiClient.post('/auth/verify-email', {
      email,
      code,
    })
    return response
  },

  /**
   * 인증번호 재발송
   * @param {string} email - 이메일
   * @returns {Promise}
   */
  async resendCode(email) {
    const response = await apiClient.post('/auth/resend-code', {
      email,
    })
    return response
  },

  /**
   * 이메일/비밀번호 로그인
   * @param {string} email - 이메일
   * @param {string} password - 비밀번호
   * @returns {Promise} 로그인 결과 (쿠키 자동 설정)
   */
  async login(email, password) {
    const response = await apiClient.post('/auth/login', {
      email,
      password,
    })
    return response
  },

  /**
   * 로그아웃 (쿠키 삭제)
   * @returns {Promise}
   */
  async logout() {
    const response = await apiClient.post('/auth/logout')
    return response
  },

  /**
   * 토큰 갱신 (쿠키 자동 사용)
   * @returns {Promise}
   */
  async refresh() {
    const response = await apiClient.post('/auth/refresh')
    return response
  },

  /**
   * 인증 상태 확인
   * @returns {Promise} { authenticated: boolean }
   */
  async checkAuth() {
    const response = await apiClient.get('/auth/check')
    return response
  },

  /**
   * 현재 사용자 정보 조회
   * @returns {Promise} 사용자 정보
   */
  async getCurrentUser() {
    const response = await apiClient.get('/auth/me')
    return response
  },

  /**
   * 사용자 프로필 수정
   * @param {Object} userData - { name?, gender?, birth_date? }
   * @returns {Promise} 수정된 사용자 정보
   */
  async updateProfile(userData) {
    const response = await apiClient.put('/auth/me', userData)
    return response
  },

  /**
   * OAuth 콜백 처리 (Authorization Code → 로컬 JWT)
   * @param {string} code - Authorization Code
   * @returns {Promise} 로그인 결과
   */
  async handleCallback(code) {
    const response = await apiClient.post('/auth/callback', { code })
    return response
  },

  /**
   * 내 클럽 멤버십 목록 조회
   * @returns {Promise} 클럽 멤버십 목록
   */
  async getMyMemberships() {
    const response = await apiClient.get('/auth/me/memberships')
    return response
  },

  /**
   * 특정 클럽에서의 내 멤버십 조회
   * @param {number} clubId - 동호회 ID
   * @returns {Promise} 클럽 멤버십 정보
   */
  async getMyMembershipInClub(clubId) {
    const response = await apiClient.get(`/auth/me/memberships/${clubId}`)
    return response
  },

  /**
   * 특정 클럽에서의 내 프로필 수정 (닉네임, 성별)
   * @param {number} clubId - 동호회 ID
   * @param {Object} data - { nickname?, gender? }
   * @returns {Promise} 수정된 클럽 멤버십 정보
   */
  async updateMyMembershipInClub(clubId, data) {
    const response = await apiClient.put(`/auth/me/memberships/${clubId}`, data)
    return response
  },
}
