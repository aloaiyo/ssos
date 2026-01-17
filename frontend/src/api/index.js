/**
 * Axios 인스턴스 설정 (HTTP-only 쿠키 기반 인증)
 */
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  // HTTP-only 쿠키 자동 전송
  withCredentials: true,
})

// 토큰 갱신 중 상태 (중복 요청 방지)
let isRefreshing = false
let failedQueue = []

const processQueue = (error) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve()
    }
  })
  failedQueue = []
}

const redirectToLogin = () => {
  // 이미 로그인 관련 페이지면 리다이렉트 안함
  if (window.location.pathname !== '/' &&
      !window.location.pathname.startsWith('/auth/')) {
    window.location.href = '/'
  }
}

// 요청 인터셉터
apiClient.interceptors.request.use(
  (config) => {
    // 쿠키는 자동으로 전송되므로 별도 처리 불필요
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터: 에러 처리 및 토큰 갱신
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    if (error.response) {
      switch (error.response.status) {
        case 401: {
          // 인증 관련 요청은 refresh 시도하지 않음 (무한 루프 방지)
          const skipRefreshUrls = ['/auth/refresh', '/auth/check', '/auth/me', '/auth/login']
          const shouldSkipRefresh = skipRefreshUrls.some(url => originalRequest.url?.includes(url))

          if (shouldSkipRefresh) {
            // 인증 체크 요청은 조용히 실패 처리
            return Promise.reject(error)
          }

          // 이미 재시도한 요청이면 로그인으로
          if (originalRequest._retry) {
            redirectToLogin()
            return Promise.reject(error)
          }

          // 토큰 갱신 중이면 대기열에 추가
          if (isRefreshing) {
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject })
            })
              .then(() => apiClient(originalRequest))
              .catch((err) => Promise.reject(err))
          }

          originalRequest._retry = true
          isRefreshing = true

          try {
            // 쿠키 기반 토큰 갱신 (refresh_token 쿠키 자동 전송)
            await apiClient.post('/auth/refresh')
            processQueue(null)
            // 갱신 성공 시 원래 요청 재시도
            return apiClient(originalRequest)
          } catch (refreshError) {
            processQueue(refreshError)
            console.error('토큰 갱신 실패:', refreshError)
            redirectToLogin()
            return Promise.reject(refreshError)
          } finally {
            isRefreshing = false
          }
        }

        case 403:
          console.error('접근 권한이 없습니다.')
          break
        case 404:
          console.error('요청한 리소스를 찾을 수 없습니다.')
          break
        case 500:
          console.error('서버 오류가 발생했습니다.')
          break
        default:
          console.error('알 수 없는 오류가 발생했습니다.')
      }
    } else if (error.request) {
      console.error('서버에 연결할 수 없습니다.')
    } else {
      console.error('요청 설정 오류:', error.message)
    }
    return Promise.reject(error)
  }
)

export default apiClient
