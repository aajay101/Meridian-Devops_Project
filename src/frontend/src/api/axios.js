import axios from 'axios'

const api = axios.create({
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

let csrfToken = ''

api.interceptors.request.use((config) => {
  if (csrfToken && config.method && !['get', 'head', 'options'].includes(config.method.toLowerCase())) {
    config.headers['X-CSRF-Token'] = csrfToken
  }
  return config
})

api.interceptors.response.use(
  (response) => {
    if (response.headers['x-csrf-token']) csrfToken = response.headers['x-csrf-token']
    return response
  },
  (error) => {
    const isLoginRequest = error.config?.url?.includes('/api/auth/login')
    if (error.response && error.response.status === 401 && !isLoginRequest) {
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
