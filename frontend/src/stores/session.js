// 세션 스토어 (Phase 2에서 사용 예정)
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSessionStore = defineStore('session', () => {
  // State
  const sessions = ref([])
  const currentSession = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Actions - Phase 2에서 구현 예정
  async function fetchSessions(eventId) {
    // TODO: Phase 2에서 구현
  }

  async function fetchSession(sessionId) {
    // TODO: Phase 2에서 구현
  }

  async function createSession(eventId, sessionData) {
    // TODO: Phase 2에서 구현
  }

  async function updateSession(sessionId, sessionData) {
    // TODO: Phase 2에서 구현
  }

  async function deleteSession(sessionId) {
    // TODO: Phase 2에서 구현
  }

  return {
    // State
    sessions,
    currentSession,
    isLoading,
    error,
    // Actions
    fetchSessions,
    fetchSession,
    createSession,
    updateSession,
    deleteSession,
  }
})
