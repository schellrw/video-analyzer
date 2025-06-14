import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { videosAPI, VideoData, casesAPI, CaseData } from '@/services/api'
import { toast } from '@/stores/toastStore'

const VideoAnalysisPage = () => {
  const { id: videoId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [video, setVideo] = useState<VideoData | null>(null)
  const [videos, setVideos] = useState<VideoData[]>([])
  const [cases, setCases] = useState<CaseData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTab, setSelectedTab] = useState<'overview' | 'analysis' | 'transcript' | 'violations'>('overview')
  const [selectedCaseFilter, setSelectedCaseFilter] = useState<string>('')

  useEffect(() => {
    if (videoId) {
      fetchVideo()
    } else {
      fetchAllVideos()
      fetchCases()
    }
  }, [videoId])

  const fetchVideo = async () => {
    try {
      setLoading(true)
      const response = await videosAPI.getVideo(videoId!)
      setVideo(response.data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to load video')
      toast.error('Error', 'Failed to load video details')
    } finally {
      setLoading(false)
    }
  }

  const fetchAllVideos = async () => {
    try {
      setLoading(true)
      const filters = selectedCaseFilter ? { case_id: selectedCaseFilter } : {}
      const response = await videosAPI.getAllVideos(filters)
      setVideos(response.data.videos)
      setError(null)
    } catch (err: any) {
      setError('Failed to load videos')
    } finally {
      setLoading(false)
    }
  }

  const fetchCases = async () => {
    try {
      const response = await casesAPI.getCases()
      setCases(response.data.cases)
    } catch (err: any) {
      // Ignore for now
    }
  }

  useEffect(() => {
    if (!videoId) {
      fetchAllVideos()
    }
  }, [selectedCaseFilter, videoId])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error && videoId) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-medium text-red-800">Error</h2>
          <p className="mt-2 text-red-700">{error || 'Video not found'}</p>
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

  // If no videoId, show video list
  if (!videoId) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Video Analysis</h1>
            <p className="text-gray-600">Manage and analyze your video evidence</p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={selectedCaseFilter}
              onChange={(e) => setSelectedCaseFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Cases</option>
              {cases.map((caseItem) => (
                <option key={caseItem.id} value={caseItem.id}>
                  {caseItem.name}
                </option>
              ))}
            </select>
            <button
              onClick={() => navigate('/?upload=true')}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Upload Video
            </button>
          </div>
        </div>

        {videos.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No videos found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {selectedCaseFilter ? 'No videos found for the selected case.' : 'Upload videos to your cases to get started with analysis.'}
            </p>
            <div className="mt-6">
              <button
                onClick={() => navigate('/cases')}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Go to Cases
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="divide-y divide-gray-200">
              {videos.map((videoItem) => (
                <div key={videoItem.id} className="p-6 hover:bg-gray-50 cursor-pointer" onClick={() => navigate(`/videos/${videoItem.id}/analysis`)}>
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <div className="flex items-center text-gray-600 mr-4">
                          {getTypeIcon(videoItem.type)}
                          <span className="ml-2 text-sm capitalize">{videoItem.type}</span>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(videoItem.status)}`}>
                          {videoItem.status}
                        </span>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">{videoItem.filename}</h3>
                      <p className="text-gray-600 text-sm mb-2">
                        {(videoItem.file_size / (1024 * 1024)).toFixed(2)} MB • {videoItem.duration} seconds
                      </p>
                      <div className="text-xs text-gray-500">
                        <span>Uploaded: {new Date(videoItem.upload_date).toLocaleDateString()}</span>
                        {videoItem.case_id && (
                          <span className="ml-4">
                            Case: {cases.find(c => c.id === videoItem.case_id)?.name || videoItem.case_id}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="ml-4">
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  // If videoId exists, show specific video analysis (existing code)
  if (!video) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-medium text-red-800">Error</h2>
          <p className="mt-2 text-red-700">Video not found</p>
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

  const getStatusColor = (status: VideoData['status']) => {
    switch (status) {
      case 'uploading':
        return 'bg-yellow-100 text-yellow-800'
      case 'processing':
        return 'bg-blue-100 text-blue-800'
      case 'analyzed':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeIcon = (type: VideoData['type']) => {
    switch (type) {
      case 'bodycam':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        )
      case 'cctv':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        )
      case 'dashcam':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        )
      case 'mobile':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        )
      default:
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        )
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Video Analysis</h1>
          <p className="text-gray-600">Analyzing {video.filename}</p>
        </div>
        <div className="flex items-center space-x-4">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(video.status)}`}>
            {video.status.charAt(0).toUpperCase() + video.status.slice(1)}
          </span>
          <button
            onClick={() => navigate(`/cases/${video.case_id}`)}
            className="px-4 py-2 text-gray-600 hover:text-gray-900"
          >
            View Case
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setSelectedTab('overview')}
              className={`px-6 py-4 text-sm font-medium ${
                selectedTab === 'overview'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setSelectedTab('analysis')}
              className={`px-6 py-4 text-sm font-medium ${
                selectedTab === 'analysis'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Analysis
            </button>
            <button
              onClick={() => setSelectedTab('transcript')}
              className={`px-6 py-4 text-sm font-medium ${
                selectedTab === 'transcript'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Transcript
            </button>
            <button
              onClick={() => setSelectedTab('violations')}
              className={`px-6 py-4 text-sm font-medium ${
                selectedTab === 'violations'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Violations
            </button>
          </nav>
        </div>

        <div className="p-6">
          {selectedTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Video Details</h3>
                  <dl className="space-y-3">
                    <div className="flex justify-between">
                      <dt className="text-gray-500">Type</dt>
                      <dd className="text-gray-900 flex items-center">
                        {getTypeIcon(video.type)}
                        <span className="ml-2 capitalize">{video.type}</span>
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-500">Duration</dt>
                      <dd className="text-gray-900">{video.duration} seconds</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-500">File Size</dt>
                      <dd className="text-gray-900">{(video.file_size / (1024 * 1024)).toFixed(2)} MB</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-500">Upload Date</dt>
                      <dd className="text-gray-900">{new Date(video.upload_date).toLocaleDateString()}</dd>
                    </div>
                  </dl>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Analysis Progress</h3>
                  {video.analysis_progress ? (
                    <div className="space-y-4">
                      <div className="flex justify-between text-sm text-gray-600">
                        <span>Progress</span>
                        <span>{video.analysis_progress.percentage}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${video.analysis_progress.percentage}%` }}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Completed:</span>
                          <span className="ml-2 text-gray-900">{video.analysis_progress.completed}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Total:</span>
                          <span className="ml-2 text-gray-900">{video.analysis_progress.total}</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-500">No analysis progress available</p>
                  )}
                </div>
              </div>

              {video.metadata && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Technical Details</h3>
                  <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <dt className="text-gray-500">Resolution</dt>
                      <dd className="text-gray-900">{video.metadata.resolution}</dd>
                    </div>
                    <div>
                      <dt className="text-gray-500">FPS</dt>
                      <dd className="text-gray-900">{video.metadata.fps}</dd>
                    </div>
                    <div>
                      <dt className="text-gray-500">Codec</dt>
                      <dd className="text-gray-900">{video.metadata.codec}</dd>
                    </div>
                    <div>
                      <dt className="text-gray-500">Source</dt>
                      <dd className="text-gray-900">{video.metadata.source}</dd>
                    </div>
                    {video.metadata.location && (
                      <div>
                        <dt className="text-gray-500">Location</dt>
                        <dd className="text-gray-900">{video.metadata.location}</dd>
                      </div>
                    )}
                    {video.metadata.timestamp && (
                      <div>
                        <dt className="text-gray-500">Timestamp</dt>
                        <dd className="text-gray-900">{video.metadata.timestamp}</dd>
                      </div>
                    )}
                  </dl>
                </div>
              )}
            </div>
          )}

          {selectedTab === 'analysis' && video.analysis_results && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-blue-800">Key Frames</h4>
                  <p className="mt-2 text-3xl font-semibold text-blue-900">{video.analysis_results.key_frames}</p>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-green-800">Objects Detected</h4>
                  <p className="mt-2 text-3xl font-semibold text-green-900">{video.analysis_results.detected_objects}</p>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-purple-800">People Detected</h4>
                  <p className="mt-2 text-3xl font-semibold text-purple-900">{video.analysis_results.detected_people}</p>
                </div>
                <div className="bg-yellow-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-yellow-800">Actions Detected</h4>
                  <p className="mt-2 text-3xl font-semibold text-yellow-900">{video.analysis_results.detected_actions}</p>
                </div>
              </div>

              <div className="bg-white rounded-lg border p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Analysis Timeline</h3>
                <div className="space-y-4">
                  {/* Timeline visualization would go here */}
                  <p className="text-gray-500">Timeline visualization coming soon...</p>
                </div>
              </div>
            </div>
          )}

          {selectedTab === 'transcript' && video.analysis_results?.audio_transcript && (
            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Audio Transcript</h3>
                <div className="prose max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap">{video.analysis_results.audio_transcript}</p>
                </div>
              </div>
            </div>
          )}

          {selectedTab === 'violations' && video.analysis_results?.violations && (
            <div className="space-y-4">
              {video.analysis_results.violations.map((violation, index) => (
                <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-red-900">{violation.type}</h3>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-red-700">Confidence: {violation.confidence}%</span>
                      <span className="text-sm text-red-700">@ {violation.timestamp}</span>
                    </div>
                  </div>
                  <p className="text-red-800">{violation.description}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default VideoAnalysisPage 