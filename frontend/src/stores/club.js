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
  const isAdminMode = ref(localStorage.getItem('isAdminMode') === 'true')

  // Getters
  const selectedClub = computed(() => {
    if (!selectedClubId.value) return null
    return clubs.value.find(club => club.id === parseInt(selectedClubId.value))
  })

  // 선택된 동호회에서 매니저인지 확인
  const isManagerOfSelectedClub = computed(() => {
    if (!selectedClub.value) return false
    const role = selectedClub.value.my_role || selectedClub.value.role
    return role === 'manager'
  })

  // Actions
  /**
   * 내 동호회 목록 조회
   */
  async function fetchClubs() {
    // 토큰이 없으면 요청하지 않음
    const token = localStorage.getItem('token')
    if (!token) return

    isLoading.value = true
    error.value = null

    try {
      const response = await clubsApi.getMyClubs()
      clubs.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '동호회 목록을 불러오는데 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 전체 동호회 목록 조회 (검색용)
   */
  async function searchClubs(search = null) {
    const token = localStorage.getItem('token')
    if (!token) return []

    try {
      const params = {}
      if (search) {
        params.search = search
      }
      const response = await clubsApi.getClubs(params)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '동호회 목록을 불러오는데 실패했습니다.'
      throw err
    }
  }

  /**
   * 동호회 가입
   */
  async function joinClub(clubId) {
    isLoading.value = true
    error.value = null
    try {
      await clubsApi.joinClub(clubId) // Assuming clubsApi has a joinClub method
    } catch (err) {
      error.value = err.response?.data?.detail || '동호회 가입 요청에 실패했습니다.'
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
      clubs.value.unshift(response.data)  // 목록 맨 앞에 추가
      selectClub(response.data.id)  // 새로 생성한 동호회 선택
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
    // 동호회 변경 시 어드민 모드 초기화
    setAdminMode(false)
  }

  /**
   * 어드민 모드 토글
   */
  function toggleAdminMode() {
    isAdminMode.value = !isAdminMode.value
    localStorage.setItem('isAdminMode', isAdminMode.value.toString())
  }

  /**
   * 어드민 모드 설정
   */
  function setAdminMode(value) {
    isAdminMode.value = value
    localStorage.setItem('isAdminMode', value.toString())
  }

  return {
    // State
    clubs,
    currentClub,
    selectedClubId,
    isLoading,
    error,
    isAdminMode,
    // Getters
    selectedClub,
    isManagerOfSelectedClub,
    // Actions
    fetchClubs,
    searchClubs,
    fetchClub,
    createClub,
    updateClub,
    deleteClub,
    selectClub,
    joinClub,
    toggleAdminMode,
    setAdminMode,
  }
})
