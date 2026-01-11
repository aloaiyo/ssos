// 시즌 스토어
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import seasonsApi from '@/api/seasons'

export const useSeasonStore = defineStore('season', () => {
  // State
  const seasons = ref([])
  const currentSeason = ref(null)
  const seasonRankings = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const activeSeasons = computed(() => {
    return seasons.value.filter(season => season.status === 'active')
  })

  const upcomingSeasons = computed(() => {
    return seasons.value.filter(season => season.status === 'upcoming')
  })

  const completedSeasons = computed(() => {
    return seasons.value.filter(season => season.status === 'completed')
  })

  // Actions
  /**
   * 시즌 목록 조회
   */
  async function fetchSeasons(clubId, params = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await seasonsApi.getSeasons(clubId, params)
      seasons.value = Array.isArray(response.data) ? response.data : []
      return seasons.value
    } catch (err) {
      error.value = err.response?.data?.detail || '시즌 목록을 불러오는데 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 시즌 상세 조회
   */
  async function fetchSeason(clubId, seasonId) {
    isLoading.value = true
    error.value = null

    try {
      const response = await seasonsApi.getSeason(clubId, seasonId)
      currentSeason.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '시즌 정보를 불러오는데 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 시즌 생성
   */
  async function createSeason(clubId, seasonData) {
    isLoading.value = true
    error.value = null

    try {
      const response = await seasonsApi.createSeason(clubId, seasonData)
      seasons.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '시즌 생성에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 시즌 수정
   */
  async function updateSeason(clubId, seasonId, seasonData) {
    isLoading.value = true
    error.value = null

    try {
      const response = await seasonsApi.updateSeason(clubId, seasonId, seasonData)
      const index = seasons.value.findIndex(s => s.id === seasonId)
      if (index !== -1) {
        seasons.value[index] = response.data
      }
      if (currentSeason.value?.id === seasonId) {
        currentSeason.value = { ...currentSeason.value, ...response.data }
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '시즌 수정에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 시즌 삭제
   */
  async function deleteSeason(clubId, seasonId) {
    isLoading.value = true
    error.value = null

    try {
      await seasonsApi.deleteSeason(clubId, seasonId)
      seasons.value = seasons.value.filter(s => s.id !== seasonId)
      if (currentSeason.value?.id === seasonId) {
        currentSeason.value = null
      }
    } catch (err) {
      error.value = err.response?.data?.detail || '시즌 삭제에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 시즌 랭킹 조회
   */
  async function fetchSeasonRankings(clubId, seasonId) {
    isLoading.value = true
    error.value = null

    try {
      const response = await seasonsApi.getSeasonRankings(clubId, seasonId)
      seasonRankings.value = response.data.rankings || []
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '시즌 랭킹을 불러오는데 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 시즌 랭킹 계산
   */
  async function calculateRankings(clubId, seasonId) {
    isLoading.value = true
    error.value = null

    try {
      const response = await seasonsApi.calculateSeasonRankings(clubId, seasonId)
      // 랭킹 새로고침
      await fetchSeasonRankings(clubId, seasonId)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '랭킹 계산에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 현재 시즌 선택
   */
  function setCurrentSeason(season) {
    currentSeason.value = season
  }

  /**
   * 상태 초기화
   */
  function resetState() {
    seasons.value = []
    currentSeason.value = null
    seasonRankings.value = []
    error.value = null
  }

  return {
    // State
    seasons,
    currentSeason,
    seasonRankings,
    isLoading,
    error,
    // Getters
    activeSeasons,
    upcomingSeasons,
    completedSeasons,
    // Actions
    fetchSeasons,
    fetchSeason,
    createSeason,
    updateSeason,
    deleteSeason,
    fetchSeasonRankings,
    calculateRankings,
    setCurrentSeason,
    resetState,
  }
})
