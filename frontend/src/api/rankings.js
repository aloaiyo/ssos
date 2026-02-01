// 랭킹 관련 API
import apiClient from './index'

export default {
  // 클럽 전체 랭킹 조회
  getRankings(clubId, params = {}) {
    return apiClient.get(`/clubs/${clubId}/rankings`, { params })
  },

  // 회원 개별 랭킹 조회
  getMemberRanking(clubId, memberId) {
    return apiClient.get(`/clubs/${clubId}/rankings/${memberId}`)
  },

  // 클럽 랭킹 갱신
  updateRankings(clubId) {
    return apiClient.post(`/clubs/${clubId}/rankings/update`)
  },

  // 시즌별 랭킹 조회
  getSeasonRankings(clubId, seasonId) {
    return apiClient.get(`/clubs/${clubId}/seasons/${seasonId}/rankings`)
  },

  // 시즌 랭킹 계산
  calculateSeasonRankings(clubId, seasonId) {
    return apiClient.post(`/clubs/${clubId}/seasons/${seasonId}/rankings/calculate`)
  },
}
