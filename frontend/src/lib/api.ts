import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
})

function isAuthError(status: number): boolean {
  return status === 401 || status === 403
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && isAuthError(error.response.status)) {
      const isLoginRequest = error.config?.url?.includes('/auth/login')
      const isAlreadyLogin = window.location.pathname === '/login'

      if (!isLoginRequest) {
        localStorage.removeItem('token')

        if (!isAlreadyLogin) {
          window.location.href = '/login'
        }
      }

      return Promise.reject(error)
    }

    const detail = error.response?.data?.detail
    const message = typeof detail === 'string' ? detail : error.message || 'Error desconocido'
    return Promise.reject(new Error(message))
  },
)

export default api
