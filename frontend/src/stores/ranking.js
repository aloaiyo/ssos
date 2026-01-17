/**
 * 랭킹 스토어
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import rankingsApi from '@/api/rankings'

export const useRankingStore = defineStore('ranking', () => {
  // State
  const rankings = ref([])
  const memberRanking = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Actions

  /**
   * 클럽 랭킹 목록 조회
   */
  async function fetchRankings(clubId, params = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await rankingsApi.getRankings(clubId, params)
      rankings.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '랭킹을 불러올 수 없습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 특정 회원 랭킹 조회
   */
  async function fetchMemberRanking(clubId, memberId) {
    isLoading.value = true
    error.value = null

    try {
      const response = await rankingsApi.getMemberRanking(clubId, memberId)
      memberRanking.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '회원 랭킹을 불러올 수 없습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 랭킹 업데이트 (재계산)
   */
  async function updateRankings(clubId) {
    isLoading.value = true
    error.value = null

    try {
      const response = await rankingsApi.updateRankings(clubId)
      // 업데이트 후 랭킹 목록 다시 조회
      await fetchRankings(clubId)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '랭킹 업데이트에 실패했습니다.'
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

  return {
    // State
    rankings,
    memberRanking,
    isLoading,
    error,
    // Actions
    fetchRankings,
    fetchMemberRanking,
    updateRankings,
    clearError,
  }
})
