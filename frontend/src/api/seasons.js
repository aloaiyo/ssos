// 시즌 관련 API
import apiClient from './index'

export default {
  /**
   * 시즌 목록 조회
   * @param {number} clubId - 동호회 ID
   * @param {Object} params - { status }
   * @returns {Promise} 시즌 목록
   */
  getSeasons(clubId, params = {}) {
    return apiClient.get(`/clubs/${clubId}/seasons`, { params })
  },

  /**
   * 시즌 상세 조회
   * @param {number} clubId - 동호회 ID
   * @param {number} seasonId - 시즌 ID
   * @returns {Promise} 시즌 상세 정보 (세션 목록 포함)
   */
  getSeason(clubId, seasonId) {
    return apiClient.get(`/clubs/${clubId}/seasons/${seasonId}`)
  },

  /**
   * 시즌 생성
   * @param {number} clubId - 동호회 ID
   * @param {Object} seasonData - { name, description, start_date, end_date }
   * @returns {Promise} 생성된 시즌 정보
   */
  createSeason(clubId, seasonData) {
    return apiClient.post(`/clubs/${clubId}/seasons`, seasonData)
  },

  /**
   * 시즌 수정
   * @param {number} clubId - 동호회 ID
   * @param {number} seasonId - 시즌 ID
   * @param {Object} seasonData - 수정할 시즌 정보
   * @returns {Promise} 수정된 시즌 정보
   */
  updateSeason(clubId, seasonId, seasonData) {
    return apiClient.put(`/clubs/${clubId}/seasons/${seasonId}`, seasonData)
  },

  /**
   * 시즌 삭제
   * @param {number} clubId - 동호회 ID
   * @param {number} seasonId - 시즌 ID
   * @returns {Promise}
   */
  deleteSeason(clubId, seasonId) {
    return apiClient.delete(`/clubs/${clubId}/seasons/${seasonId}`)
  },

  /**
   * 시즌 랭킹 조회
   * @param {number} clubId - 동호회 ID
   * @param {number} seasonId - 시즌 ID
   * @returns {Promise} 시즌 랭킹 목록
   */
  getSeasonRankings(clubId, seasonId) {
    return apiClient.get(`/clubs/${clubId}/seasons/${seasonId}/rankings`)
  },

  /**
   * 시즌 랭킹 계산
   * @param {number} clubId - 동호회 ID
   * @param {number} seasonId - 시즌 ID
   * @returns {Promise}
   */
  calculateSeasonRankings(clubId, seasonId) {
    return apiClient.post(`/clubs/${clubId}/seasons/${seasonId}/rankings/calculate`)
  },
}
