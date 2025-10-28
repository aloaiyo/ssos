// 매치 스토어 (Phase 2에서 사용 예정)
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMatchStore = defineStore('match', () => {
  // State
  const matches = ref([])
  const currentMatch = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Actions - Phase 2에서 구현 예정
  async function generateMatches(sessionId, config) {
    // TODO: Phase 2에서 구현
  }

  async function fetchMatches(sessionId) {
    // TODO: Phase 2에서 구현
  }

  async function updateMatch(matchId, matchData) {
    // TODO: Phase 2에서 구현
  }

  async function recordResult(matchId, resultData) {
    // TODO: Phase 2에서 구현
  }

  return {
    // State
    matches,
    currentMatch,
    isLoading,
    error,
    // Actions
    generateMatches,
    fetchMatches,
    updateMatch,
    recordResult,
  }
})
