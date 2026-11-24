import api from './axios'

export const getDashboard = () => {
  return api.get('/api/student/dashboard')
}

export const getDrives = (query = '') => {
  const params = query ? { q: query } : {}
  return api.get('/api/student/drives', { params })
}

export const getDrive = (id) => {
  return api.get(`/api/student/drives/${id}`)
}

export const applyToDrive = (id) => {
  return api.post(`/api/student/drives/${id}/apply`)
}

export const applyToDriveWithResume = (id, file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/api/student/drives/${id}/apply`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getApplications = () => {
  return api.get('/api/student/applications')
}

export const getProfile = () => {
  return api.get('/api/student/profile')
}

export const updateProfile = (data) => {
  return api.put('/api/student/profile', data)
}

export const uploadResume = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/api/student/profile/resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getPlacementHistory = () => {
  return api.get('/api/student/applications/history')
}

export const acceptOffer = (applicationId) => {
  return api.post(`/api/student/applications/${applicationId}/accept-offer`)
}

export const declineOffer = (applicationId) => {
  return api.post(`/api/student/applications/${applicationId}/decline-offer`)
}

export const triggerExport = () => {
  return api.post('/api/jobs/export')
}

export const getExportStatus = (taskId) => {
  return api.get(`/api/jobs/export/status/${taskId}`)
}

export const getExportDownloadUrl = (taskId) => {
  return `/api/jobs/export/download/${taskId}`
}
