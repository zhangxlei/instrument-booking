import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserBrief } from '../types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserBrief | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))

  function setAuth(data: { access_token: string; refresh_token: string; user: UserBrief }) {
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
  }

  function setUser(u: UserBrief) {
    user.value = u
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  function isLoggedIn(): boolean {
    return !!token.value
  }

  function isAdmin(): boolean {
    return user.value?.role === 'admin'
  }

  return { user, token, setAuth, setUser, logout, isLoggedIn, isAdmin }
})
