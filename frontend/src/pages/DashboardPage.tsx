import { useAuthStore } from '@/stores/authStore'
import { useNavigate } from 'react-router-dom'

const DashboardPage = () => {
  const { user, signOut } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await signOut()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Video Evidence Analyzer
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
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Dashboard</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-blue-50 p-6 rounded-lg">
              <h3 className="text-lg font-medium text-blue-900">Cases</h3>
              <p className="text-blue-700 mt-2">Manage your legal cases</p>
              <div className="mt-4">
                <span className="text-2xl font-bold text-blue-900">0</span>
                <span className="text-blue-700 ml-2">Active cases</span>
              </div>
            </div>
            
            <div className="bg-green-50 p-6 rounded-lg">
              <h3 className="text-lg font-medium text-green-900">Videos</h3>
              <p className="text-green-700 mt-2">Upload and analyze evidence</p>
              <div className="mt-4">
                <span className="text-2xl font-bold text-green-900">0</span>
                <span className="text-green-700 ml-2">Videos uploaded</span>
              </div>
            </div>
            
            <div className="bg-purple-50 p-6 rounded-lg">
              <h3 className="text-lg font-medium text-purple-900">Reports</h3>
              <p className="text-purple-700 mt-2">Generated analysis reports</p>
              <div className="mt-4">
                <span className="text-2xl font-bold text-purple-900">0</span>
                <span className="text-purple-700 ml-2">Reports created</span>
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