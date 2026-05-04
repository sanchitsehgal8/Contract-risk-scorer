import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 180000,
  headers: {
    'Accept': 'application/json',
  }
})

// Request interceptor
client.interceptors.request.use(
  config => {
    // For FormData, let browser set Content-Type automatically
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    console.log(`→ ${config.method.toUpperCase()} ${config.url}`)
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor
client.interceptors.response.use(
  response => {
    console.log(`← ${response.status} ${response.config.url}`)
    return response.data
  },
  error => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred'
    
    const status = error.response?.status || 'unknown'
    console.error(`✗ [${status}] Error: ${message}`)
    console.error(`Full error:`, error.response?.data || error)
    
    return Promise.reject(new Error(message))
  }
)

export default client
