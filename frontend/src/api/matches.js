// 매치 관련 API (Phase 2에서 사용 예정)
import apiClient from './index'

export default {
  // Phase 2에서 구현 예정
  generateMatches(sessionId, config) {
    return apiClient.post(`/sessions/${sessionId}/generate-matches`, config)
  },

  getMatches(sessionId) {
    return apiClient.get(`/sessions/${sessionId}/matches`)
  },

  getMatch(matchId) {
    return apiClient.get(`/matches/${matchId}`)
  },

  updateMatch(matchId, matchData) {
    return apiClient.put(`/matches/${matchId}`, matchData)
  },

  deleteMatch(matchId) {
    return apiClient.delete(`/matches/${matchId}`)
  },

  recordResult(matchId, resultData) {
    return apiClient.post(`/matches/${matchId}/result`, resultData)
  },
}
