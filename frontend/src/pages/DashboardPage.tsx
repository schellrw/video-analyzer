import { useAuthStore } from '@/stores/authStore'
import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { casesAPI } from '@/services/api'

const DashboardPage = () => {
  const { user, signOut } = useAuthStore()
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    totalCases: 0,
    activeCases: 0,
    loading: true,
    error: null as string | null
  })

  const handleLogout = async () => {
    await signOut()
    navigate('/login')
  }

  // Fetch dashboard statistics
  useEffect(() => {
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
        } else {
          setStats(prev => ({ 
            ...prev, 
            loading: false, 
            error: 'Failed to load statistics' 
          }))
        }
      } catch (error: any) {
        console.error('Error fetching dashboard stats:', error)
        setStats(prev => ({ 
          ...prev, 
          loading: false, 
          error: error.message || 'Failed to load statistics' 
        }))
      }
    }

    if (user) {
      fetchStats()
    }
  }, [user])

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
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
            <button
              onClick={() => window.location.reload()}
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
            
            <div className="bg-green-50 p-6 rounded-lg">
              <h3 className="text-lg font-medium text-green-900">Videos</h3>
              <p className="text-green-700 mt-2">Upload and analyze content</p>
              <div className="mt-4">
                <span className="text-2xl font-bold text-green-900">0</span>
                <span className="text-green-700 ml-2">Videos uploaded</span>
                <div className="text-xs text-green-600 mt-1">Coming soon</div>
              </div>
            </div>
            
            <div className="bg-purple-50 p-6 rounded-lg">
              <h3 className="text-lg font-medium text-purple-900">Reports</h3>
              <p className="text-purple-700 mt-2">Generated analysis reports</p>
              <div className="mt-4">
                <span className="text-2xl font-bold text-purple-900">0</span>
                <span className="text-purple-700 ml-2">Reports created</span>
                <div className="text-xs text-purple-600 mt-1">Coming soon</div>
              </div>
            </div>
          </div>
          
          <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h4 className="text-lg font-medium text-yellow-800">🎉 Authentication Working!</h4>
            <p className="text-yellow-700 mt-2">
              Your login system is fully functional. You're logged in as:
            </p>
            <div className="mt-3 text-sm bg-white p-3 rounded border">
              <p><strong>Email:</strong> {user?.email}</p>
              <p><strong>Name:</strong> {user?.firstName} {user?.lastName}</p>
              <p><strong>Role:</strong> {user?.role}</p>
              {user?.organization && <p><strong>Organization:</strong> {user.organization}</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage 