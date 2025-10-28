// 인증 관련 API
import apiClient from './index'

export default {
  /**
   * 로그인
   * @param {Object} credentials - { username, password }
   * @returns {Promise} access_token 포함된 응답
   */
  login(credentials) {
    // OAuth2 형식의 form data로 전송
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    return apiClient.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
  },

  /**
   * 회원가입
   * @param {Object} userData - { username, email, password, full_name }
   * @returns {Promise} 생성된 사용자 정보
   */
  register(userData) {
    return apiClient.post('/auth/register', userData)
  },

  /**
   * 현재 사용자 정보 조회
   * @returns {Promise} 사용자 정보
   */
  getCurrentUser() {
    return apiClient.get('/auth/me')
  },

  /**
   * 사용자 정보 수정
   * @param {Object} userData - 수정할 사용자 정보
   * @returns {Promise} 수정된 사용자 정보
   */
  updateProfile(userData) {
    return apiClient.put('/auth/me', userData)
  },

  /**
   * 비밀번호 변경
   * @param {Object} passwords - { current_password, new_password }
   * @returns {Promise}
   */
  changePassword(passwords) {
    return apiClient.post('/auth/change-password', passwords)
  },
}
