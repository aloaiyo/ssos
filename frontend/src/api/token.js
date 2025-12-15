import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export async function refreshAccessToken(refreshToken) {
    const response = await axios.post(`${baseURL}/auth/refresh`, {
        refresh_token: refreshToken
    })
    return response.data
}
