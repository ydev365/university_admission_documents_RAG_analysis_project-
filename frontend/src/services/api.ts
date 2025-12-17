import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Chat APIs
export const chatAPI = {
  getSubjects: async () => {
    const response = await api.get('/api/chat/subjects')
    return response.data
  },

  sendMessage: async (data: { subject: string; question: string }) => {
    const response = await api.post('/api/chat', data)
    return response.data
  },
}

// History APIs
export const historyAPI = {
  getHistory: async (params?: { skip?: number; limit?: number; subject?: string }) => {
    const response = await api.get('/api/history', { params })
    return response.data
  },

  getHistoryDetail: async (id: number) => {
    const response = await api.get(`/api/history/${id}`)
    return response.data
  },
}

export default api
