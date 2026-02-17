// API Service - Axios client configurado
import axios from 'axios'
import DOMPurify from 'dompurify'

const API_BASE_URL = 'http://localhost:8000'

// Axios instance con configuración segura
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - agregar token de autenticación
api.interceptors.request.use(
  async (config) => {
    // Obtener token desde keytar (OS keychain)
    if (window.electron) {
      const result = await window.electron.keytar.getPassword('auth-token')
      if (result.success && result.token) {
        config.headers.Authorization = `Bearer ${result.token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - manejo de errores
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token inválido o expirado - limpiar y redirigir al login
      if (window.electron) {
        await window.electron.keytar.deletePassword('auth-token')
      }
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 🔒 Sanitización de inputs (XSS protection)
export function sanitizeInput(input: string): string {
  return DOMPurify.sanitize(input, { ALLOWED_TAGS: [] })
}

// Health check
export async function checkHealth() {
  const response = await api.get('/health')
  return response.data
}

// TODO: API methods cuando se implementen los endpoints
// export const authAPI = { ... }
// export const studentsAPI = { ... }
// export const gradesAPI = { ... }
// etc.

export default api
