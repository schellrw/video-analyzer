import { useAuthStore } from '@/stores/authStore'
import { useNavigate, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { casesAPI } from '@/services/api'
import QuickVideoUpload from '@/components/QuickVideoUpload'
import { toast } from '@/stores/toastStore'

const DashboardPage = () => {
  const { user, signOut } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [stats, setStats] = useState({
    totalCases: 0,
    activeCases: 0,
    loading: true,
    error: null as string | null
  })

  // Reset onboarding when navigating to dashboard
  useEffect(() => {
    if (location.pathname === '/') {
      const urlParams = new URLSearchParams(location.search)
      const shouldUpload = urlParams.get('upload') === 'true'
      
      if (shouldUpload) {
        setShowOnboarding(true)
      } else {
        // Only show onboarding for truly new users (no cases)
        if (stats.totalCases === 0 && !stats.loading) {
          setShowOnboarding(true)
        } else {
          setShowOnboarding(false)
        }
      }
    }
  }, [location.pathname, location.search, stats.totalCases, stats.loading])

  const handleLogout = async () => {
    await signOut()
    navigate('/login')
  }

  const handleUploadSuccess = (videoId: string, caseName: string) => {
    setShowOnboarding(false)
    toast.success('Upload successful!', `Case "${caseName}" has been created and analysis has started.`)
    // Refresh stats to show the newly created case
    fetchStats()
    // Clear the upload parameter from URL
    if (location.search.includes('upload=true')) {
      navigate('/', { replace: true })
    }
  }

  // Fetch dashboard statistics
  const fetchStats = async () => {
    try {
      setStats(prev => ({ ...prev, loading: true, error: null }))
      const response = await casesAPI.getCaseStats()
      
      if (response.success) {
        const { total_cases, status_counts } = response.data
        // Calculate active cases (all except closed and archived)
        const activeCases = total_cases - (status_counts.closed || 0) - (status_counts.archived || 0)
        
        setStats({
          totalCases: total_cases,
          activeCases: activeCases,
          loading: false,
          error: null
        })
        
        // Show onboarding for new users with no cases
        if (total_cases === 0) {
          setShowOnboarding(true)
        }
      } else {
        setStats(prev => ({ 
          ...prev, 
          loading: false, 
          error: 'Failed to load statistics' 
        }))
      }
    } catch (error: any) {
      console.error('Error fetching dashboard stats:', error)
      
      // Handle different error scenarios gracefully
      const status = error.response?.status
      const message = error.response?.data?.message || error.response?.data?.msg
      
      if (status === 401 || message === 'Missing Authorization Header') {
        // Auth issue - for new users, show onboarding instead of error
        console.warn('Authentication issue when fetching cases - showing onboarding for new user')
        setStats({
          totalCases: 0,
          activeCases: 0,
          loading: false,
          error: null
        })
        setShowOnboarding(true)
      } else if (status === 404) {
        // No cases found - show onboarding
        setStats({
          totalCases: 0,
          activeCases: 0,
          loading: false,
          error: null
        })
        setShowOnboarding(true)
      } else {
        // Other errors - show generic error
        setStats(prev => ({ 
          ...prev, 
          loading: false, 
          error: message || 'Failed to load statistics. Please check your connection and try again.' 
        }))
      }
    }
  }

  useEffect(() => {
    if (user) {
      fetchStats()
    }
  }, [user])

  // Show onboarding flow for new users
  if (showOnboarding) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Video Analyzer
                </h1>
                <p className="text-gray-600">Welcome, {user?.firstName}! Let's get started.</p>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Welcome to Video Analyzer! 👋
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Transform your video evidence into powerful legal insights with AI-powered analysis. 
              Upload your first video to get started - it only takes a few minutes to see results.
            </p>
          </div>
          
          <QuickVideoUpload 
            onUploadSuccess={handleUploadSuccess}
            onCancel={() => setShowOnboarding(false)}
          />
          
          <div className="mt-12 text-center">
            <button
              onClick={() => setShowOnboarding(false)}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              Skip for now and explore the dashboard
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Video Analyzer
              </h1>
              <p className="text-gray-600">Welcome back, {user?.firstName}!</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowOnboarding(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Upload Video
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
            <button
              onClick={fetchStats}
              className="text-gray-500 hover:text-gray-700 p-2 rounded-md hover:bg-gray-100"
              title="Refresh dashboard"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-blue-50 p-6 rounded-lg cursor-pointer hover:bg-blue-100 transition-colors" onClick={() => navigate('/cases')}>
              <h3 className="text-lg font-medium text-blue-900">Cases</h3>
              <p className="text-blue-700 mt-2">Manage your cases</p>
              <div className="mt-4">
                {stats.loading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-900"></div>
                    <span className="text-blue-700 ml-2">Loading...</span>
                  </div>
                ) : stats.error ? (
                  <div className="text-red-600 text-sm">{stats.error}</div>
                ) : (
                  <>
                    <span className="text-2xl font-bold text-blue-900">{stats.activeCases}</span>
                    <span className="text-blue-700 ml-2">Active cases</span>
                    {stats.totalCases > stats.activeCases && (
                      <div className="text-sm text-blue-600 mt-1">
                        {stats.totalCases} total cases
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
            
            <div className="bg-green-50 p-6 rounded-lg cursor-pointer hover:bg-green-100 transition-colors" onClick={() => setShowOnboarding(true)}>
              <h3 className="text-lg font-medium text-green-900">Upload Video</h3>
              <p className="text-green-700 mt-2">Quick video analysis</p>
              <div className="mt-4">
                <span className="text-2xl font-bold text-green-900">+</span>
                <span className="text-green-700 ml-2">Add new video</span>
                <div className="text-xs text-green-600 mt-1">Click to start</div>
              </div>
            </div>
            
            <div className="bg-purple-50 p-6 rounded-lg cursor-pointer hover:bg-purple-100 transition-colors" onClick={() => navigate('/reports')}>
              <h3 className="text-lg font-medium text-purple-900">Reports</h3>
              <p className="text-purple-700 mt-2">Generated analysis reports</p>
              <div className="mt-4">
                <span className="text-2xl font-bold text-purple-900">0</span>
                <span className="text-purple-700 ml-2">Reports created</span>
                <div className="text-xs text-purple-600 mt-1">View reports</div>
              </div>
            </div>
          </div>
          
          {stats.totalCases > 0 ? (
            <div className="mt-8 p-4 bg-green-50 border border-green-200 rounded-lg">
              <h4 className="text-lg font-medium text-green-800">🎉 Great Progress!</h4>
              <p className="text-green-700 mt-2">
                You have {stats.totalCases} case{stats.totalCases > 1 ? 's' : ''} in your account. 
                {stats.activeCases > 0 && ` ${stats.activeCases} ${stats.activeCases === 1 ? 'is' : 'are'} currently active.`}
              </p>
              <div className="mt-3 text-sm">
                <button
                  onClick={() => navigate('/cases')}
                  className="text-green-800 hover:text-green-900 font-medium"
                >
                  View all cases →
                </button>
              </div>
            </div>
          ) : (
            <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="text-lg font-medium text-blue-800">🚀 Ready to Get Started?</h4>
              <p className="text-blue-700 mt-2">
                Upload your first video to see the power of AI-driven video analysis in action.
              </p>
              <div className="mt-3">
                <button
                  onClick={() => setShowOnboarding(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors font-medium"
                >
                  Upload Your First Video
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DashboardPage 