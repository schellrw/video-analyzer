import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { casesAPI, videosAPI, CaseData, VideoData } from '../services/api'

const CaseDetailPage = () => {
  const { id: caseId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [caseData, setCaseData] = useState<CaseData | null>(null)
  const [videos, setVideos] = useState<VideoData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (caseId) {
      fetchCase()
      fetchVideos()
    }
  }, [caseId])

  const fetchCase = async () => {
    try {
      setLoading(true)
      const response = await casesAPI.getCase(caseId!, false)
      setCaseData(response.data)
      setError(null)
    } catch (err: any) {
      setError('Failed to load case details')
    } finally {
      setLoading(false)
    }
  }

  const fetchVideos = async () => {
    try {
      const response = await videosAPI.getCaseVideos(caseId!)
      setVideos(response.data.videos)
    } catch (err: any) {
      // Ignore for now
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error || !caseData) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-medium text-red-800">Error</h2>
          <p className="mt-2 text-red-700">{error || 'Case not found'}</p>
          <button
            onClick={() => navigate(-1)}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Case Details</h1>
        <button
          onClick={() => navigate(`/cases/${caseId}/edit`)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Edit
        </button>
      </div>
      <div className="bg-white p-6 rounded-lg shadow space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">{caseData.name}</h2>
          <div className="text-sm text-gray-500 mb-2">Case #{caseData.case_number}</div>
          <div className="mb-2 text-gray-700">{caseData.description}</div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
            <div><strong>Status:</strong> {caseData.status}</div>
            <div><strong>Priority:</strong> {caseData.priority}</div>
            <div><strong>Incident Date:</strong> {caseData.incident_date ? new Date(caseData.incident_date).toLocaleDateString() : 'N/A'}</div>
            <div><strong>Incident Location:</strong> {caseData.incident_location || 'N/A'}</div>
            <div><strong>Court Jurisdiction:</strong> {caseData.court_jurisdiction || 'N/A'}</div>
            <div><strong>Opposing Party:</strong> {caseData.opposing_party || 'N/A'}</div>
            <div><strong>Legal Theory:</strong> {caseData.legal_theory || 'N/A'}</div>
            <div><strong>Tags:</strong> {caseData.tags?.join(', ') || 'None'}</div>
          </div>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Videos</h3>
          {videos.length === 0 ? (
            <div className="text-gray-500">No videos uploaded for this case.</div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {videos.map((video) => (
                <li key={video.id} className="py-3 flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900">{video.filename}</div>
                    <div className="text-xs text-gray-500">{video.type} &bull; Uploaded {new Date(video.upload_date).toLocaleDateString()}</div>
                  </div>
                  <button
                    onClick={() => navigate(`/videos/${video.id}/analysis`)}
                    className="px-3 py-1.5 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-xs"
                  >
                    View Analysis
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Reports</h3>
          <div className="text-gray-500">(Reports integration coming soon)</div>
        </div>
      </div>
    </div>
  )
}

export default CaseDetailPage 