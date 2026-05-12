import axios from 'axios'

const api = axios.create({
  // Esto usará la URL del .env si existe, o '/api/v1' por defecto
  baseURL: (import.meta.env.VITE_API_URL || '') + '/api/v1',
})

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
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user_permissions')
      localStorage.removeItem('user_group_ids')
      localStorage.removeItem('user_priv_admin')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default api
