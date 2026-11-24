import api from './axios'

export const getDashboard = () => {
  return api.get('/api/admin/dashboard')
}

export const getCompanies = () => {
  return api.get('/api/admin/companies')
}

export const getCompany = (id) => {
  return api.get(`/api/admin/company/${id}`)
}

export const approveCompany = (id) => {
  return api.post(`/api/admin/company/${id}/approve`)
}

export const rejectCompany = (id) => {
  return api.post(`/api/admin/company/${id}/reject`)
}

export const deactivateCompany = (id) => {
  return api.patch(`/api/admin/company/${id}/deactivate`)
}

export const activateCompany = (id) => {
  return api.patch(`/api/admin/company/${id}/activate`)
}

export const getStudents = () => {
  return api.get('/api/admin/students')
}

export const getStudent = (id) => {
  return api.get(`/api/admin/student/${id}`)
}

export const deactivateStudent = (id) => {
  return api.patch(`/api/admin/student/${id}/deactivate`)
}

export const activateStudent = (id) => {
  return api.patch(`/api/admin/student/${id}/activate`)
}

export const getDrives = () => {
  return api.get('/api/admin/drives')
}

export const getDrive = (id) => {
  return api.get(`/api/admin/drive/${id}`)
}

export const approveDrive = (id) => {
  return api.post(`/api/admin/drive/${id}/approve`)
}

export const rejectDrive = (id) => {
  return api.post(`/api/admin/drive/${id}/reject`)
}

export const closeDrive = (id) => {
  return api.post(`/api/admin/drive/${id}/close`)
}

export const getApplications = () => {
  return api.get('/api/admin/applications')
}

export const getReportsSummary = () => {
  return api.get('/api/admin/reports/summary')
}
