// 랭킹 스토어 (Phase 2에서 사용 예정)
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useRankingStore = defineStore('ranking', () => {
  // State
  const rankings = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  // Actions - Phase 2에서 구현 예정
  async function fetchRankings(clubId) {
    // TODO: Phase 2에서 구현
  }

  async function fetchMemberRanking(clubId, memberId) {
    // TODO: Phase 2에서 구현
  }

  async function updateRankings(clubId) {
    // TODO: Phase 2에서 구현
  }

  return {
    // State
    rankings,
    isLoading,
    error,
    // Actions
    fetchRankings,
    fetchMemberRanking,
    updateRankings,
  }
})
