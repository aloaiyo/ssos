// 이벤트 관련 API (Phase 2에서 사용 예정)
import apiClient from './index'

export default {
  // Phase 2에서 구현 예정
  getEvents(clubId, params = {}) {
    return apiClient.get(`/clubs/${clubId}/events`, { params })
  },

  getEvent(clubId, eventId) {
    return apiClient.get(`/clubs/${clubId}/events/${eventId}`)
  },

  createEvent(clubId, eventData) {
    return apiClient.post(`/clubs/${clubId}/events`, eventData)
  },

  updateEvent(clubId, eventId, eventData) {
    return apiClient.put(`/clubs/${clubId}/events/${eventId}`, eventData)
  },

  deleteEvent(clubId, eventId) {
    return apiClient.delete(`/clubs/${clubId}/events/${eventId}`)
  },
}
