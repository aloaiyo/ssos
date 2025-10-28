// 동호회 관련 API
import apiClient from './index'

export default {
  /**
   * 동호회 목록 조회
   * @param {Object} params - { skip, limit }
   * @returns {Promise} 동호회 목록
   */
  getClubs(params = {}) {
    return apiClient.get('/clubs/', { params })
  },

  /**
   * 동호회 상세 조회
   * @param {number} clubId - 동호회 ID
   * @returns {Promise} 동호회 상세 정보
   */
  getClub(clubId) {
    return apiClient.get(`/clubs/${clubId}`)
  },

  /**
   * 동호회 생성
   * @param {Object} clubData - { name, description, location }
   * @returns {Promise} 생성된 동호회 정보
   */
  createClub(clubData) {
    return apiClient.post('/clubs/', clubData)
  },

  /**
   * 동호회 수정
   * @param {number} clubId - 동호회 ID
   * @param {Object} clubData - 수정할 동호회 정보
   * @returns {Promise} 수정된 동호회 정보
   */
  updateClub(clubId, clubData) {
    return apiClient.put(`/clubs/${clubId}`, clubData)
  },

  /**
   * 동호회 삭제
   * @param {number} clubId - 동호회 ID
   * @returns {Promise}
   */
  deleteClub(clubId) {
    return apiClient.delete(`/clubs/${clubId}`)
  },

  /**
   * 동호회 회원 목록 조회
   * @param {number} clubId - 동호회 ID
   * @returns {Promise} 회원 목록
   */
  getClubMembers(clubId) {
    return apiClient.get(`/clubs/${clubId}/members`)
  },
}
