const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

function getToken() {
  return localStorage.getItem('token')
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth) {
    const token = getToken()
    if (token) headers.Authorization = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  if (res.status === 204) return null

  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data.error || `Request failed with status ${res.status}`)
  }
  return data
}

export const authApi = {
  register: (username, password) =>
    request('/auth/register', { method: 'POST', body: { username, password }, auth: false }),
  login: (username, password) =>
    request('/auth/login', { method: 'POST', body: { username, password }, auth: false }),
}

export const userApi = {
  list: () => request('/users'),
}

export const projectApi = {
  list: () => request('/projects'),
  get: (id) => request(`/projects/${id}`),
  create: (project) => request('/projects', { method: 'POST', body: project }),
  update: (id, fields) => request(`/projects/${id}`, { method: 'PUT', body: fields }),
  remove: (id) => request(`/projects/${id}`, { method: 'DELETE' }),
}

export const taskApi = {
  list: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return request(`/tasks${query ? `?${query}` : ''}`)
  },
  create: (task) => request('/tasks', { method: 'POST', body: task }),
  update: (id, fields) => request(`/tasks/${id}`, { method: 'PUT', body: fields }),
  remove: (id) => request(`/tasks/${id}`, { method: 'DELETE' }),
}
