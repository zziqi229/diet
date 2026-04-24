import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)

  function _persist(accessToken, userObj) {
    token.value = accessToken
    user.value = userObj
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('user', JSON.stringify(userObj))
  }

  async function loginAction(credentials) {
    const res = await apiLogin(credentials)
    _persist(res.data.access_token, res.data.user)
    return res
  }

  async function registerAction(data) {
    const res = await apiRegister(data)
    _persist(res.data.access_token, res.data.user)
    return res
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  return { token, user, isAuthenticated, loginAction, registerAction, logout }
})
