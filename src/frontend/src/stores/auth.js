import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin, registerStudent as apiRegisterStudent, registerCompany as apiRegisterCompany, logout as apiLogout, getMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchUser = async () => {
    try {
      const response = await getMe()
      if (response.data.authenticated) {
        user.value = response.data
      } else {
        user.value = null
      }
    } catch (err) {
      user.value = null
    }
  }

  const login = async (email, password, role) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiLogin(email, password, role)
      if (response.data.success) {
        await fetchUser()
        return response.data.role
      }
    } catch (err) {
      if (err.response && err.response.data) {
        error.value = err.response.data.error
      } else {
        error.value = 'server_error'
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  const registerStudent = async (data) => {
    loading.value = true
    error.value = null
    try {
      await apiRegisterStudent(data)
      return true
    } catch (err) {
      if (err.response && err.response.data) {
        error.value = err.response.data.error
      } else {
        error.value = 'server_error'
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  const registerCompany = async (data) => {
    loading.value = true
    error.value = null
    try {
      await apiRegisterCompany(data)
      return true
    } catch (err) {
      if (err.response && err.response.data) {
        error.value = err.response.data.error
      } else {
        error.value = 'server_error'
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      await apiLogout()
    } catch (err) {
      // ignore logout errors
    } finally {
      user.value = null
    }
  }

  return { user, loading, error, fetchUser, login, registerStudent, registerCompany, logout }
})
