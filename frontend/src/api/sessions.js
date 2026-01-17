// 세션 관련 API
import apiClient from './index'

export default {
  /**
   * 세션 목록 조회
   * @param {number} clubId - 동호회 ID
   * @param {Object} params - { season_id, event_id }
   * @returns {Promise} 세션 목록
   */
  getSessions(clubId, params = {}) {
    return apiClient.get(`/clubs/${clubId}/sessions`, { params })
  },

  /**
   * 세션 상세 조회
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @returns {Promise} 세션 상세 정보
   */
  getSession(clubId, sessionId) {
    return apiClient.get(`/clubs/${clubId}/sessions/${sessionId}`)
  },

  /**
   * 세션 생성
   * @param {number} clubId - 동호회 ID
   * @param {Object} sessionData - { title, session_date, location, session_type, season_id }
   * @returns {Promise} 생성된 세션 정보
   */
  createSession(clubId, sessionData) {
    return apiClient.post(`/clubs/${clubId}/sessions`, sessionData)
  },

  /**
   * 세션 수정
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @param {Object} sessionData - 수정할 세션 정보
   * @returns {Promise} 수정된 세션 정보
   */
  updateSession(clubId, sessionId, sessionData) {
    return apiClient.put(`/clubs/${clubId}/sessions/${sessionId}`, sessionData)
  },

  /**
   * 세션 삭제
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @returns {Promise}
   */
  deleteSession(clubId, sessionId) {
    return apiClient.delete(`/clubs/${clubId}/sessions/${sessionId}`)
  },

  /**
   * 세션 참가자 목록 조회
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @returns {Promise} 참가자 목록
   */
  getSessionParticipants(clubId, sessionId) {
    return apiClient.get(`/clubs/${clubId}/sessions/${sessionId}/participants`)
  },

  /**
   * 세션 참가자 추가
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @param {number} memberId - 회원 ID
   * @returns {Promise}
   */
  addParticipant(clubId, sessionId, memberId) {
    return apiClient.post(`/clubs/${clubId}/sessions/${sessionId}/participants/${memberId}`)
  },

  /**
   * 세션 참가자 제거
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @param {number} memberId - 회원 ID
   * @returns {Promise}
   */
  removeParticipant(clubId, sessionId, memberId) {
    return apiClient.delete(`/clubs/${clubId}/sessions/${sessionId}/participants/${memberId}`)
  },

  /**
   * 세션 경기 목록 조회
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @returns {Promise} 경기 목록
   */
  getMatches(clubId, sessionId) {
    return apiClient.get(`/clubs/${clubId}/sessions/${sessionId}/matches`)
  },

  /**
   * 세션 경기 자동 생성
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @returns {Promise} 생성된 경기 목록
   */
  generateMatches(clubId, sessionId) {
    return apiClient.post(`/clubs/${clubId}/sessions/${sessionId}/matches/generate`)
  },

  /**
   * 경기 결과 업데이트
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @param {number} matchId - 경기 ID
   * @param {Object} matchData - { team_a_score, team_b_score }
   * @returns {Promise}
   */
  updateMatch(clubId, sessionId, matchId, matchData) {
    return apiClient.put(`/clubs/${clubId}/sessions/${sessionId}/matches/${matchId}`, matchData)
  },

  /**
   * 현재 사용자가 세션에 참가
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @returns {Promise}
   */
  joinSession(clubId, sessionId) {
    return apiClient.post(`/clubs/${clubId}/sessions/${sessionId}/join`)
  },

  /**
   * 현재 사용자가 세션에서 불참
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @returns {Promise}
   */
  leaveSession(clubId, sessionId) {
    return apiClient.delete(`/clubs/${clubId}/sessions/${sessionId}/join`)
  },

  /**
   * 현재 사용자의 세션 참가 여부 확인
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @returns {Promise} { is_participating, is_member, member_id, participant_id }
   */
  getMyParticipation(clubId, sessionId) {
    return apiClient.get(`/clubs/${clubId}/sessions/${sessionId}/my-participation`)
  },

  /**
   * AI 기반 경기 자동 생성 (미리보기)
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @param {Object} options - { mode: 'balanced'|'random', match_duration_minutes, break_duration_minutes }
   * @returns {Promise} 생성된 경기 미리보기
   */
  generateAIMatches(clubId, sessionId, options = {}) {
    return apiClient.post(`/clubs/${clubId}/sessions/${sessionId}/matches/generate-ai`, options)
  },

  /**
   * AI 생성 경기 확정
   * @param {number} clubId - 동호회 ID
   * @param {number} sessionId - 세션 ID
   * @param {Array} matches - 확정할 경기 목록
   * @returns {Promise}
   */
  confirmAIMatches(clubId, sessionId, matches) {
    return apiClient.post(`/clubs/${clubId}/sessions/${sessionId}/matches/confirm-ai`, { matches })
  },
}
