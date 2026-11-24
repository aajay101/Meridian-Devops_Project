import api from './axios'

export const login = (email, password, role) => {
  return api.post('/api/auth/login', { email, password, role })
}

export const registerStudent = (data) => {
  return api.post('/api/auth/student/register', data)
}

export const registerCompany = (data) => {
  return api.post('/api/auth/company/register', data)
}

export const logout = () => {
  return api.post('/api/auth/logout')
}

export const getMe = () => {
  return api.get('/api/auth/me')
}

export const getBranches = () => {
  return api.get('/api/auth/branches')
}
