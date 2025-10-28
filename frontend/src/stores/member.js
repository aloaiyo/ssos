// 회원 스토어
import { defineStore } from 'pinia'
import { ref } from 'vue'
import membersApi from '@/api/members'

export const useMemberStore = defineStore('member', () => {
  // State
  const members = ref([])
  const currentMember = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Actions
  /**
   * 회원 목록 조회
   */
  async function fetchMembers(clubId, params = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await membersApi.getMembers(clubId, params)
      members.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '회원 목록을 불러올 수 없습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 회원 상세 조회
   */
  async function fetchMember(clubId, memberId) {
    isLoading.value = true
    error.value = null

    try {
      const response = await membersApi.getMember(clubId, memberId)
      currentMember.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '회원 정보를 불러올 수 없습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 회원 생성
   */
  async function createMember(clubId, memberData) {
    isLoading.value = true
    error.value = null

    try {
      const response = await membersApi.createMember(clubId, memberData)
      members.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '회원 추가에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 회원 수정
   */
  async function updateMember(clubId, memberId, memberData) {
    isLoading.value = true
    error.value = null

    try {
      const response = await membersApi.updateMember(clubId, memberId, memberData)
      const index = members.value.findIndex(m => m.id === memberId)
      if (index !== -1) {
        members.value[index] = response.data
      }
      if (currentMember.value?.id === memberId) {
        currentMember.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '회원 수정에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 회원 삭제
   */
  async function deleteMember(clubId, memberId) {
    isLoading.value = true
    error.value = null

    try {
      await membersApi.deleteMember(clubId, memberId)
      members.value = members.value.filter(m => m.id !== memberId)
      if (currentMember.value?.id === memberId) {
        currentMember.value = null
      }
    } catch (err) {
      error.value = err.response?.data?.detail || '회원 삭제에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 회원 통계 조회
   */
  async function fetchMemberStats(clubId, memberId) {
    isLoading.value = true
    error.value = null

    try {
      const response = await membersApi.getMemberStats(clubId, memberId)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '회원 통계를 불러올 수 없습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    members,
    currentMember,
    isLoading,
    error,
    // Actions
    fetchMembers,
    fetchMember,
    createMember,
    updateMember,
    deleteMember,
    fetchMemberStats,
  }
})
