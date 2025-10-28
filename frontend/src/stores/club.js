// 동호회 스토어
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import clubsApi from '@/api/clubs'

export const useClubStore = defineStore('club', () => {
  // State
  const clubs = ref([])
  const currentClub = ref(null)
  const selectedClubId = ref(localStorage.getItem('selectedClubId'))
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const selectedClub = computed(() => {
    if (!selectedClubId.value) return null
    return clubs.value.find(club => club.id === parseInt(selectedClubId.value))
  })

  // Actions
  /**
   * 동호회 목록 조회
   */
  async function fetchClubs(params = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await clubsApi.getClubs(params)
      clubs.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '동호회 목록을 불러올 수 없습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 동호회 상세 조회
   */
  async function fetchClub(clubId) {
    isLoading.value = true
    error.value = null

    try {
      const response = await clubsApi.getClub(clubId)
      currentClub.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '동호회 정보를 불러올 수 없습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 동호회 생성
   */
  async function createClub(clubData) {
    isLoading.value = true
    error.value = null

    try {
      const response = await clubsApi.createClub(clubData)
      clubs.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '동호회 생성에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 동호회 수정
   */
  async function updateClub(clubId, clubData) {
    isLoading.value = true
    error.value = null

    try {
      const response = await clubsApi.updateClub(clubId, clubData)
      const index = clubs.value.findIndex(c => c.id === clubId)
      if (index !== -1) {
        clubs.value[index] = response.data
      }
      if (currentClub.value?.id === clubId) {
        currentClub.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '동호회 수정에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 동호회 삭제
   */
  async function deleteClub(clubId) {
    isLoading.value = true
    error.value = null

    try {
      await clubsApi.deleteClub(clubId)
      clubs.value = clubs.value.filter(c => c.id !== clubId)
      if (currentClub.value?.id === clubId) {
        currentClub.value = null
      }
      if (selectedClubId.value === clubId.toString()) {
        selectClub(null)
      }
    } catch (err) {
      error.value = err.response?.data?.detail || '동호회 삭제에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 동호회 선택
   */
  function selectClub(clubId) {
    selectedClubId.value = clubId ? clubId.toString() : null
    if (clubId) {
      localStorage.setItem('selectedClubId', clubId.toString())
    } else {
      localStorage.removeItem('selectedClubId')
    }
  }

  return {
    // State
    clubs,
    currentClub,
    selectedClubId,
    isLoading,
    error,
    // Getters
    selectedClub,
    // Actions
    fetchClubs,
    fetchClub,
    createClub,
    updateClub,
    deleteClub,
    selectClub,
  }
})
