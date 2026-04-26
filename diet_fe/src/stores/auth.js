import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  function setAuth(data) {
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
  }

  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function login(credentials) {
    const res = await authApi.login(credentials)
    setAuth(res.data.data)
    return res.data
  }

  async function register(credentials) {
    const res = await authApi.register(credentials)
    setAuth(res.data.data)
    return res.data
  }

  function logout() {
    clearAuth()
  }

  return { token, user, isLoggedIn, login, register, logout }
})
