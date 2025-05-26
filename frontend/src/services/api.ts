import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth-storage')
  if (token) {
    try {
      const authData = JSON.parse(token)
      if (authData.state?.token) {
        config.headers.Authorization = `Bearer ${authData.state.token}`
      }
    } catch (error) {
      console.error('Error parsing auth token:', error)
    }
  }
  return config
})

// Types for Case Management
export interface CaseData {
  id?: string
  name: string
  description?: string
  case_number?: string
  incident_date?: string
  incident_location?: string
  incident_description?: string
  status?: 'pending' | 'analyzing' | 'completed' | 'archived' | 'closed'
  priority?: 'low' | 'medium' | 'high' | 'urgent'
  tags?: string[]
  court_jurisdiction?: string
  opposing_party?: string
  legal_theory?: string
  created_at?: string
  updated_at?: string
  closed_at?: string
  video_count?: number
  analysis_progress?: {
    total: number
    completed: number
    percentage: number
  }
}

export interface CasesResponse {
  success: boolean
  data: {
    cases: CaseData[]
    pagination: {
      page: number
      per_page: number
      total: number
      pages: number
      has_next: boolean
      has_prev: boolean
    }
  }
}

export interface CaseStatsResponse {
  success: boolean
  data: {
    total_cases: number
    status_counts: Record<string, number>
    priority_counts: Record<string, number>
    recent_cases: number
  }
}

export interface CasesFilters {
  page?: number
  per_page?: number
  status?: string
  priority?: string
  search?: string
}

// Auth API endpoints
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password })
    return response.data
  },

  register: async (userData: {
    email: string
    password: string
    firstName: string
    lastName: string
    organization?: string
    role?: string
  }) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  logout: async () => {
    const response = await api.post('/auth/logout')
    return response.data
  },
}

// Cases API endpoints
export const casesAPI = {
  // Get all cases with filtering and pagination
  getCases: async (filters: CasesFilters = {}): Promise<CasesResponse> => {
    const params = new URLSearchParams()
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.append(key, value.toString())
      }
    })
    
    const response = await api.get(`/cases?${params.toString()}`)
    return response.data
  },

  // Get a single case by ID
  getCase: async (caseId: string, includeVideos: boolean = false): Promise<{ success: boolean; data: CaseData }> => {
    const params = includeVideos ? '?include_videos=true' : ''
    const response = await api.get(`/cases/${caseId}${params}`)
    return response.data
  },

  // Create a new case
  createCase: async (caseData: Omit<CaseData, 'id' | 'case_number' | 'created_at' | 'updated_at' | 'video_count' | 'analysis_progress'>): Promise<{ success: boolean; data: CaseData; message: string }> => {
    const response = await api.post('/cases', caseData)
    return response.data
  },

  // Update an existing case
  updateCase: async (caseId: string, caseData: Partial<CaseData>): Promise<{ success: boolean; data: CaseData; message: string }> => {
    const response = await api.put(`/cases/${caseId}`, caseData)
    return response.data
  },

  // Delete a case
  deleteCase: async (caseId: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/cases/${caseId}`)
    return response.data
  },

  // Get case statistics
  getCaseStats: async (): Promise<CaseStatsResponse> => {
    const response = await api.get('/cases/stats')
    return response.data
  },
}

// Health check
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health')
    return response.data
  },
}

export default api 