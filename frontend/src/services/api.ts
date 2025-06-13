import axios from 'axios'
import { supabase } from './supabase'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include Supabase auth token
api.interceptors.request.use(async (config) => {
  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
    }
  } catch (error) {
    console.error('Error getting Supabase session:', error)
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

// Types for Video Management
export interface VideoData {
  id: string
  case_id: string
  filename: string
  file_size: number
  duration: number
  type: 'bodycam' | 'cctv' | 'dashcam' | 'mobile' | 'other'
  status: 'uploading' | 'processing' | 'analyzed' | 'failed'
  upload_date: string
  analysis_progress?: {
    total: number
    completed: number
    percentage: number
  }
  metadata?: {
    resolution: string
    fps: number
    codec: string
    source: string
    location?: string
    timestamp?: string
  }
  analysis_results?: {
    key_frames: number
    detected_objects: number
    detected_people: number
    detected_actions: number
    audio_transcript?: string
    violations?: {
      type: string
      confidence: number
      timestamp: string
      description: string
    }[]
  }
}

export interface VideosResponse {
  success: boolean
  data: {
    videos: VideoData[]
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

// Video API endpoints
export const videosAPI = {
  // Get all videos for a case
  getCaseVideos: async (caseId: string, filters: { page?: number; per_page?: number } = {}): Promise<VideosResponse> => {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, value.toString())
      }
    })
    const response = await api.get(`/cases/${caseId}/videos?${params.toString()}`)
    return response.data
  },

  // Get all videos across all cases
  getAllVideos: async (filters: { page?: number; per_page?: number; case_id?: string } = {}): Promise<VideosResponse> => {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, value.toString())
      }
    })
    const response = await api.get(`/videos?${params.toString()}`)
    return response.data
  },

  // Get a single video by ID
  getVideo: async (videoId: string): Promise<{ success: boolean; data: VideoData }> => {
    const response = await api.get(`/videos/${videoId}`)
    return response.data
  },

  // Upload a new video to a case
  uploadVideo: async (caseId: string, file: File, metadata: Partial<VideoData['metadata']> = {}): Promise<{ success: boolean; data: VideoData; message: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('metadata', JSON.stringify(metadata))
    const response = await api.post(`/cases/${caseId}/videos`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // Delete a video
  deleteVideo: async (videoId: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/videos/${videoId}`)
    return response.data
  }
}

export default api 