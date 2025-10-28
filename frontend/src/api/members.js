// 회원 관련 API
import apiClient from './index'

export default {
  /**
   * 회원 목록 조회
   * @param {number} clubId - 동호회 ID
   * @param {Object} params - { skip, limit }
   * @returns {Promise} 회원 목록
   */
  getMembers(clubId, params = {}) {
    return apiClient.get(`/clubs/${clubId}/members`, { params })
  },

  /**
   * 회원 상세 조회
   * @param {number} clubId - 동호회 ID
   * @param {number} memberId - 회원 ID
   * @returns {Promise} 회원 상세 정보
   */
  getMember(clubId, memberId) {
    return apiClient.get(`/clubs/${clubId}/members/${memberId}`)
  },

  /**
   * 회원 생성
   * @param {number} clubId - 동호회 ID
   * @param {Object} memberData - { user_id, gender, preferred_type }
   * @returns {Promise} 생성된 회원 정보
   */
  createMember(clubId, memberData) {
    return apiClient.post(`/clubs/${clubId}/members`, memberData)
  },

  /**
   * 회원 수정
   * @param {number} clubId - 동호회 ID
   * @param {number} memberId - 회원 ID
   * @param {Object} memberData - 수정할 회원 정보
   * @returns {Promise} 수정된 회원 정보
   */
  updateMember(clubId, memberId, memberData) {
    return apiClient.put(`/clubs/${clubId}/members/${memberId}`, memberData)
  },

  /**
   * 회원 삭제
   * @param {number} clubId - 동호회 ID
   * @param {number} memberId - 회원 ID
   * @returns {Promise}
   */
  deleteMember(clubId, memberId) {
    return apiClient.delete(`/clubs/${clubId}/members/${memberId}`)
  },

  /**
   * 회원 통계 조회
   * @param {number} clubId - 동호회 ID
   * @param {number} memberId - 회원 ID
   * @returns {Promise} 회원 통계 정보
   */
  getMemberStats(clubId, memberId) {
    return apiClient.get(`/clubs/${clubId}/members/${memberId}/stats`)
  },
}
