// 인증 스토어
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authApi from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.role === 'super_admin')
  const isSuperAdmin = computed(() => user.value?.role === 'super_admin')

  // Actions
  /**
   * 로그인
   */
  async function login(credentials) {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.login(credentials)
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)

      // 사용자 정보 로드
      await loadUser()

      // 홈으로 이동
      router.push({ name: 'home' })
    } catch (err) {
      error.value = err.response?.data?.detail || '로그인에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 회원가입
   */
  async function register(userData) {
    isLoading.value = true
    error.value = null

    try {
      await authApi.register(userData)
      // 회원가입 후 자동 로그인
      await login({
        username: userData.username,
        password: userData.password,
      })
    } catch (err) {
      error.value = err.response?.data?.detail || '회원가입에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 로그아웃
   */
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    router.push({ name: 'login' })
  }

  /**
   * 사용자 정보 로드
   */
  async function loadUser() {
    if (!token.value) {
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.getCurrentUser()
      user.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '사용자 정보를 불러올 수 없습니다.'
      // 토큰이 유효하지 않으면 로그아웃
      if (err.response?.status === 401) {
        logout()
      }
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
    } catch (err) {
      error.value = err.response?.data?.detail || '프로필 수정에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 비밀번호 변경
   */
  async function changePassword(passwords) {
    isLoading.value = true
    error.value = null

    try {
      await authApi.changePassword(passwords)
    } catch (err) {
      error.value = err.response?.data?.detail || '비밀번호 변경에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    user,
    token,
    isLoading,
    error,
    // Getters
    isAuthenticated,
    isAdmin,
    isSuperAdmin,
    // Actions
    login,
    register,
    logout,
    loadUser,
    updateProfile,
    changePassword,
  }
})
