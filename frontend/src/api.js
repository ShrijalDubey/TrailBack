const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function api(path, options = {}) {
  const headers = new Headers(options.headers || {})
  if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
  const apiKey = localStorage.getItem('trailback_api_key')
  if (apiKey && !headers.has('X-API-Key')) headers.set('X-API-Key', apiKey)

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  const text = await response.text()
  let data = null
  try { data = text ? JSON.parse(text) : null } catch { data = text }
  if (!response.ok) {
    const message = data?.detail || data?.message || `Request failed (${response.status})`
    throw new Error(message)
  }
  return data
}

export const apiInfo = () => ({ baseUrl: BASE_URL })
