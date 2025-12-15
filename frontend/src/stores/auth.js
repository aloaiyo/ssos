/**
 * 인증 스토어 (HTTP-only 쿠키 기반)
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authApi from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const isAuthenticated = ref(false)

  // 회원가입 중간 상태 (이메일 인증 대기)
  const pendingEmail = ref(null)

  // Getters
  const isAdmin = computed(() => user.value?.role === 'super_admin')
  const isPremium = computed(() => user.value?.is_premium || false)
  const isProfileComplete = computed(() => {
    if (!user.value) return false
    return user.value.gender && user.value.birth_date
  })

  // Actions

  /**
   * 회원가입 (1단계: 이메일 인증번호 발송)
   */
  async function register(email, password, name) {
    isLoading.value = true
    error.value = null

    try {
      await authApi.register(email, password, name)
      pendingEmail.value = email
      return { success: true, email }
    } catch (err) {
      error.value = err.response?.data?.detail || '회원가입에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 이메일 인증번호 확인 (2단계: 계정 활성화)
   */
  async function verifyEmail(email, code) {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.verifyEmail(email, code)
      user.value = response.data.user
      isAuthenticated.value = true
      pendingEmail.value = null
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '인증번호 확인에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 인증번호 재발송
   */
  async function resendCode(email) {
    isLoading.value = true
    error.value = null

    try {
      await authApi.resendCode(email)
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || '재발송에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 로그인
   */
  async function login(email, password) {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.login(email, password)
      user.value = response.data.user
      isAuthenticated.value = true
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '로그인에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 로그아웃
   */
  async function logout() {
    try {
      await authApi.logout()
    } catch (err) {
      console.error('로그아웃 API 오류:', err)
    } finally {
      user.value = null
      isAuthenticated.value = false
      router.push('/')
    }
  }

  /**
   * 인증 상태 확인 및 사용자 정보 로드
   * 초기 로드 시 에러 메시지를 표시하지 않음 (silent check)
   */
  async function checkAuth() {
    try {
      const authCheck = await authApi.checkAuth()
      if (authCheck.data.authenticated) {
        // silent=true로 호출하여 에러 팝업 표시하지 않음
        try {
          await loadUser(true)
          return true
        } catch (loadErr) {
          // 토큰이 유효하지 않은 경우 - 조용히 실패 처리
          console.debug('인증 확인 중 사용자 로드 실패:', loadErr)
          return false
        }
      }
      return false
    } catch (err) {
      isAuthenticated.value = false
      user.value = null
      return false
    }
  }

  /**
   * 사용자 정보 로드
   * @param {boolean} silent - true면 에러 메시지를 설정하지 않음 (초기 인증 확인용)
   */
  async function loadUser(silent = false) {
    isLoading.value = true
    if (!silent) {
      error.value = null
    }

    try {
      const response = await authApi.getCurrentUser()
      user.value = response.data
      isAuthenticated.value = true
      return response.data
    } catch (err) {
      if (!silent) {
        error.value = err.response?.data?.detail || '사용자 정보를 불러올 수 없습니다.'
      }
      isAuthenticated.value = false
      user.value = null
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 프로필 수정
   */
  async function updateProfile(userData) {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.updateProfile(userData)
      user.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '프로필 수정에 실패했습니다.'
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
   * OAuth 콜백 처리 (구글 로그인 후)
   */
  async function handleCallback(code) {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.handleCallback(code)
      user.value = response.data.user
      isAuthenticated.value = true
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'OAuth 인증에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    user,
    isLoading,
    error,
    isAuthenticated,
    pendingEmail,
    // Getters
    isAdmin,
    isPremium,
    isProfileComplete,
    // Actions
    register,
    verifyEmail,
    resendCode,
    login,
    logout,
    checkAuth,
    loadUser,
    updateProfile,
    clearError,
    handleCallback,
  }
})
