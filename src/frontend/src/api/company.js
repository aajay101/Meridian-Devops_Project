import api from './axios'

export const getDashboard = () => {
  return api.get('/api/company/dashboard')
}

export const getProfile = () => {
  return api.get('/api/company/profile')
}

export const updateProfile = (data) => {
  return api.put('/api/company/profile', data)
}

export const getDrives = () => {
  return api.get('/api/company/drives')
}

export const getDrive = (id) => {
  return api.get(`/api/company/drives/${id}`)
}

export const createDrive = (data) => {
  return api.post('/api/company/drives', data)
}

export const editDrive = (id, data) => {
  return api.put(`/api/company/drives/${id}`, data)
}

export const deleteDrive = (id) => {
  return api.delete(`/api/company/drives/${id}`)
}

export const closeDrive = (id) => {
  return api.post(`/api/company/drives/${id}/close`)
}

export const getApplicants = (id) => {
  return api.get(`/api/company/drives/${id}/applicants`)
}

export const shortlistApplicant = (applicationId) => {
  return api.post(`/api/company/application/${applicationId}/shortlist`)
}

export const rejectApplicant = (applicationId, data = {}) => {
  return api.post(`/api/company/application/${applicationId}/reject`, data)
}

export const scheduleInterview = (applicationId, data) => {
  return api.post(`/api/company/application/${applicationId}/schedule-interview`, data)
}

export const selectApplicant = (applicationId, data = {}) => {
  return api.post(`/api/company/application/${applicationId}/select`, data)
}
