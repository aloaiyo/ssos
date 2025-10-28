// Axios 인스턴스 설정 및 인터셉터
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터: JWT 토큰 자동 추가
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터: 에러 처리
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      // 서버 응답이 있는 경우
      switch (error.response.status) {
        case 401:
          // 인증 실패 - 토큰 삭제 및 로그인 페이지로 이동
          localStorage.removeItem('token')
          if (window.location.pathname !== '/auth/login') {
            window.location.href = '/auth/login'
          }
          break
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
      // 요청이 전송되었지만 응답이 없는 경우
      console.error('서버에 연결할 수 없습니다.')
    } else {
      // 요청 설정 중 오류 발생
      console.error('요청 설정 오류:', error.message)
    }
    return Promise.reject(error)
  }
)

export default apiClient
