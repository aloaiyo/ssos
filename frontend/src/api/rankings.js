// 랭킹 관련 API (Phase 2에서 사용 예정)
import apiClient from './index'

export default {
  // Phase 2에서 구현 예정
  getRankings(clubId, params = {}) {
    return apiClient.get(`/clubs/${clubId}/rankings`, { params })
  },

  getMemberRanking(clubId, memberId) {
    return apiClient.get(`/clubs/${clubId}/rankings/${memberId}`)
  },

  updateRankings(clubId) {
    return apiClient.post(`/clubs/${clubId}/rankings/update`)
  },
}
