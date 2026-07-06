import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const res = await axios.post('/api/v1/auth/refresh', { refresh_token: refreshToken })
          const { access_token, refresh_token: newRefresh } = res.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', newRefresh)
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return client(originalRequest)
        } catch {
          const authStore = useAuthStore()
          authStore.logout()
          router.push('/login')
        }
      } else {
        const authStore = useAuthStore()
        authStore.logout()
        router.push('/login')
      }
    }
    return Promise.reject(error)
  },
)

export default client
