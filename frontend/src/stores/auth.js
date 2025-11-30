import { defineStore } from 'pinia'
import api from '@/utils/request'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.is_admin || false
  },

  actions: {
    async login(email, password) {
      const data = await api.post('/auth/login', { email, password })
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      return data
    },

    async register(userData) {
      const data = await api.post('/auth/register', userData)
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      return data
    },

    async fetchCurrentUser() {
      const data = await api.get('/auth/me')
      this.user = data
      localStorage.setItem('user', JSON.stringify(data))
      return data
    },

    async updateProfile(profileData) {
      const data = await api.put('/auth/update-profile', profileData)
      this.user = data.user
      localStorage.setItem('user', JSON.stringify(data.user))
      return data
    },

    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
