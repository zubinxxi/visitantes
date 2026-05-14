import axios from 'axios'

const host = window.location.hostname
const protocol = host === 'localhost' || host === '127.0.0.1'
  ? window.location.protocol
  : 'https:'
const api = axios.create({
  baseURL: `${protocol}//${host}/api/v1`,
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
