// 세션 관련 API (Phase 2에서 사용 예정)
import apiClient from './index'

export default {
  // Phase 2에서 구현 예정
  getSessions(eventId, params = {}) {
    return apiClient.get(`/events/${eventId}/sessions`, { params })
  },

  getSession(sessionId) {
    return apiClient.get(`/sessions/${sessionId}`)
  },

  createSession(eventId, sessionData) {
    return apiClient.post(`/events/${eventId}/sessions`, sessionData)
  },

  updateSession(sessionId, sessionData) {
    return apiClient.put(`/sessions/${sessionId}`, sessionData)
  },

  deleteSession(sessionId) {
    return apiClient.delete(`/sessions/${sessionId}`)
  },

  getSessionParticipants(sessionId) {
    return apiClient.get(`/sessions/${sessionId}/participants`)
  },

  addParticipant(sessionId, memberId) {
    return apiClient.post(`/sessions/${sessionId}/participants/${memberId}`)
  },

  removeParticipant(sessionId, memberId) {
    return apiClient.delete(`/sessions/${sessionId}/participants/${memberId}`)
  },
}
