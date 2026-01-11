// 매치 관련 API
import apiClient from './index'

export default {
  /**
   * 경기 목록 조회
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @returns {Promise} 경기 목록
   */
  getMatches(clubId, sessionId) {
    return apiClient.get(`/clubs/${clubId}/sessions/${sessionId}/matches`)
  },

  /**
   * 경기 상세 조회
   * @param {number} clubId - 동호회 ID
   * @param {number} matchId - 경기 ID
   * @returns {Promise} 경기 상세 정보
   */
  getMatch(clubId, matchId) {
    return apiClient.get(`/clubs/${clubId}/matches/${matchId}`)
  },

  /**
   * 경기 수정 (점수 업데이트 등)
   * @param {number} clubId - 동호회 ID
   * @param {number} matchId - 경기 ID
   * @param {Object} matchData - 수정할 경기 정보
   * @returns {Promise} 수정된 경기 정보
   */
  updateMatch(clubId, matchId, matchData) {
    return apiClient.put(`/clubs/${clubId}/matches/${matchId}`, matchData)
  },

  /**
   * 경기 삭제
   * @param {number} clubId - 동호회 ID
   * @param {number} matchId - 경기 ID
   * @returns {Promise}
   */
  deleteMatch(clubId, matchId) {
    return apiClient.delete(`/clubs/${clubId}/matches/${matchId}`)
  },

  /**
   * 경기 결과 기록
   * @param {number} clubId - 동호회 ID
   * @param {number} matchId - 경기 ID
   * @param {Object} resultData - 결과 데이터
   * @returns {Promise}
   */
  recordResult(clubId, matchId, resultData) {
    return apiClient.post(`/clubs/${clubId}/matches/${matchId}/result`, resultData)
  },
}
