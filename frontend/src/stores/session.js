// 세션 스토어
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import sessionsApi from '@/api/sessions'
import { today } from '@/utils/date'

/** @typedef {import('@/types/api').Session} Session */
/** @typedef {import('@/types/api').MyParticipation} MyParticipation */

export const useSessionStore = defineStore('session', () => {
  // State
  /** @type {import('vue').Ref<Session[]>} */
  const sessions = ref([])
  /** @type {import('vue').Ref<Session|null>} */
  const currentSession = ref(null)
  /** @type {import('vue').Ref<MyParticipation|null>} */
  const myParticipation = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const isParticipating = computed(() => myParticipation.value?.is_participating ?? false)
  const isMember = computed(() => myParticipation.value?.is_member ?? false)

  const upcomingSessions = computed(() => {
    const todayStr = today()
    return sessions.value.filter(s => s.date >= todayStr && s.status !== 'cancelled')
  })

  const pastSessions = computed(() => {
    const todayStr = today()
    return sessions.value.filter(s => s.date < todayStr || s.status === 'completed')
  })

  // Actions
  async function fetchSessions(clubId, params = {}) {
    isLoading.value = true
    error.value = null
    try {
      const response = await sessionsApi.getSessions(clubId, params)
      sessions.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '세션 목록을 불러오는데 실패했습니다'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSession(clubId, sessionId) {
    isLoading.value = true
    error.value = null
    try {
      const response = await sessionsApi.getSession(clubId, sessionId)
      currentSession.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '세션을 불러오는데 실패했습니다'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createSession(clubId, sessionData) {
    isLoading.value = true
    error.value = null
    try {
      const response = await sessionsApi.createSession(clubId, sessionData)
      sessions.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '세션 생성에 실패했습니다'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateSession(clubId, sessionId, sessionData) {
    isLoading.value = true
    error.value = null
    try {
      const response = await sessionsApi.updateSession(clubId, sessionId, sessionData)
      const index = sessions.value.findIndex(s => s.id === sessionId)
      if (index !== -1) {
        sessions.value[index] = { ...sessions.value[index], ...response.data }
      }
      if (currentSession.value?.id === sessionId) {
        currentSession.value = { ...currentSession.value, ...response.data }
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '세션 수정에 실패했습니다'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteSession(clubId, sessionId) {
    isLoading.value = true
    error.value = null
    try {
      await sessionsApi.deleteSession(clubId, sessionId)
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null
      }
    } catch (err) {
      error.value = err.response?.data?.detail || '세션 삭제에 실패했습니다'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 현재 사용자의 참가 여부 확인
  async function fetchMyParticipation(clubId, sessionId) {
    try {
      const response = await sessionsApi.getMyParticipation(clubId, sessionId)
      myParticipation.value = response.data
      return response.data
    } catch (err) {
      myParticipation.value = null
      throw err
    }
  }

  // 세션 참가
  async function joinSession(clubId, sessionId) {
    isLoading.value = true
    error.value = null
    try {
      const response = await sessionsApi.joinSession(clubId, sessionId)
      myParticipation.value = { ...myParticipation.value, is_participating: true }
      // 현재 세션의 참가자 수 업데이트
      if (currentSession.value?.id === sessionId) {
        await fetchSession(clubId, sessionId)
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '참가 신청에 실패했습니다'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 세션 불참
  async function leaveSession(clubId, sessionId) {
    isLoading.value = true
    error.value = null
    try {
      const response = await sessionsApi.leaveSession(clubId, sessionId)
      myParticipation.value = { ...myParticipation.value, is_participating: false }
      // 현재 세션의 참가자 수 업데이트
      if (currentSession.value?.id === sessionId) {
        await fetchSession(clubId, sessionId)
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '참가 취소에 실패했습니다'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 참가/불참 토글
  async function toggleParticipation(clubId, sessionId) {
    if (isParticipating.value) {
      return await leaveSession(clubId, sessionId)
    } else {
      return await joinSession(clubId, sessionId)
    }
  }

  // 세션 참가자 목록 조회
  async function fetchParticipants(clubId, sessionId) {
    try {
      const response = await sessionsApi.getSessionParticipants(clubId, sessionId)
      return Array.isArray(response.data) ? response.data : []
    } catch (err) {
      error.value = err.response?.data?.detail || '참가자 목록을 불러오는데 실패했습니다'
      throw err
    }
  }

  // 세션 경기 목록 조회
  async function fetchMatches(clubId, sessionId) {
    try {
      const response = await sessionsApi.getMatches(clubId, sessionId)
      return Array.isArray(response.data) ? response.data : []
    } catch (err) {
      error.value = err.response?.data?.detail || '경기 목록을 불러오는데 실패했습니다'
      throw err
    }
  }

  // AI 기반 경기 자동 생성 (미리보기)
  async function generateAIMatches(clubId, sessionId, options = {}) {
    error.value = null
    try {
      const response = await sessionsApi.generateAIMatches(clubId, sessionId, options)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'AI 경기 생성에 실패했습니다'
      throw err
    }
  }

  // AI 생성 경기 확정
  async function confirmAIMatches(clubId, sessionId, matches) {
    error.value = null
    try {
      const response = await sessionsApi.confirmAIMatches(clubId, sessionId, matches)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '경기 확정에 실패했습니다'
      throw err
    }
  }

  // 경기 자동 생성
  async function generateMatches(clubId, sessionId) {
    isLoading.value = true
    error.value = null
    try {
      const response = await sessionsApi.generateMatches(clubId, sessionId)
      // 세션 데이터 새로고침
      await fetchSession(clubId, sessionId)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '경기 생성에 실패했습니다'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 경기 결과 저장
  async function saveMatchResult(clubId, sessionId, matchId, score) {
    isLoading.value = true
    error.value = null
    try {
      const response = await sessionsApi.updateMatch(clubId, sessionId, matchId, score)
      // 세션 데이터 새로고침
      await fetchSession(clubId, sessionId)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '결과 저장에 실패했습니다'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 참가자 추가 (관리자용)
  async function addParticipant(clubId, sessionId, memberId) {
    isLoading.value = true
    error.value = null
    try {
      const response = await sessionsApi.addParticipant(clubId, sessionId, memberId)
      await fetchSession(clubId, sessionId)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '참가자 추가에 실패했습니다'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 참가자 제거 (관리자용)
  async function removeParticipant(clubId, sessionId, participantId) {
    isLoading.value = true
    error.value = null
    try {
      const response = await sessionsApi.removeParticipant(clubId, sessionId, participantId)
      await fetchSession(clubId, sessionId)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '참가자 제거에 실패했습니다'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 참가자 일괄 추가
  async function addParticipantsBulk(clubId, sessionId, memberIds) {
    error.value = null
    try {
      const response = await sessionsApi.addParticipantsBulk(clubId, sessionId, memberIds)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '참가자 일괄 추가에 실패했습니다'
      throw err
    }
  }

  // 점수 일괄 입력
  async function updateMatchesBulkScores(clubId, sessionId, scores) {
    error.value = null
    try {
      const response = await sessionsApi.updateMatchesBulkScores(clubId, sessionId, scores)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '점수 일괄 저장에 실패했습니다'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  function resetState() {
    sessions.value = []
    currentSession.value = null
    myParticipation.value = null
    error.value = null
  }

  return {
    // State
    sessions,
    currentSession,
    myParticipation,
    isLoading,
    error,
    // Getters
    isParticipating,
    isMember,
    upcomingSessions,
    pastSessions,
    // Actions
    fetchSessions,
    fetchSession,
    createSession,
    updateSession,
    deleteSession,
    fetchMyParticipation,
    joinSession,
    leaveSession,
    toggleParticipation,
    fetchParticipants,
    fetchMatches,
    generateMatches,
    generateAIMatches,
    confirmAIMatches,
    saveMatchResult,
    addParticipant,
    removeParticipant,
    addParticipantsBulk,
    updateMatchesBulkScores,
    clearError,
    resetState,
  }
})
