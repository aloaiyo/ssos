/**
 * 매치 스토어
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import matchesApi from '@/api/matches'
import sessionsApi from '@/api/sessions'

export const useMatchStore = defineStore('match', () => {
  // State
  const matches = ref([])
  const currentMatch = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Actions

  /**
   * 경기 자동 생성
   */
  async function generateMatches(clubId, sessionId, config = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await sessionsApi.generateMatches(clubId, sessionId, config)
      // 생성 후 경기 목록 다시 조회
      await fetchMatches(clubId, sessionId)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '경기 생성에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 세션의 경기 목록 조회
   */
  async function fetchMatches(clubId, sessionId) {
    isLoading.value = true
    error.value = null

    try {
      const response = await matchesApi.getMatches(clubId, sessionId)
      matches.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '경기 목록을 불러올 수 없습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 경기 상세 조회
   */
  async function fetchMatch(clubId, matchId) {
    isLoading.value = true
    error.value = null

    try {
      const response = await matchesApi.getMatch(clubId, matchId)
      currentMatch.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '경기 정보를 불러올 수 없습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 경기 수정 (점수 업데이트 등)
   */
  async function updateMatch(clubId, matchId, matchData) {
    isLoading.value = true
    error.value = null

    try {
      const response = await matchesApi.updateMatch(clubId, matchId, matchData)
      // 수정된 경기 정보로 목록 업데이트
      const index = matches.value.findIndex(m => m.id === matchId)
      if (index !== -1) {
        matches.value[index] = { ...matches.value[index], ...response.data }
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '경기 수정에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 경기 결과 기록
   */
  async function recordResult(clubId, matchId, resultData) {
    isLoading.value = true
    error.value = null

    try {
      const response = await matchesApi.recordResult(clubId, matchId, resultData)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '결과 기록에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 경기 삭제
   */
  async function deleteMatch(clubId, matchId) {
    isLoading.value = true
    error.value = null

    try {
      await matchesApi.deleteMatch(clubId, matchId)
      // 삭제된 경기를 목록에서 제거
      matches.value = matches.value.filter(m => m.id !== matchId)
    } catch (err) {
      error.value = err.response?.data?.detail || '경기 삭제에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 에러 초기화
   */
  function clearError() {
    error.value = null
  }

  /**
   * 상태 초기화
   */
  function resetState() {
    matches.value = []
    currentMatch.value = null
    error.value = null
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
    fetchMatch,
    updateMatch,
    recordResult,
    deleteMatch,
    clearError,
    resetState,
  }
})
