import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { casesAPI, CaseData, CasesFilters } from '../services/api'
import CaseCard from '../components/CaseCard'
import CaseForm from '../components/CaseForm'
import { useAuthStore } from '../stores/authStore'

const CasesPage = () => {
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuthStore()
  const [cases, setCases] = useState<CaseData[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [editing, setEditing] = useState<CaseData | null>(null)
  const [deleting, setDeleting] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<CasesFilters>({
    page: 1,
    per_page: 12,
    search: '',
    status: '',
    priority: ''
  })
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 12,
    total: 0,
    pages: 0,
    has_next: false,
    has_prev: false
  })
  const [totalCasesCount, setTotalCasesCount] = useState(0) // Track total cases without filters

  useEffect(() => {
    if (isAuthenticated) {
      fetchCases()
    }
  }, [filters, isAuthenticated])

  const fetchCases = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await casesAPI.getCases(filters)
      setCases(response.data.cases)
      setPagination(response.data.pagination)
      
      // Also get total count without filters for empty state logic
      if (!filters.search && !filters.status && !filters.priority) {
        setTotalCasesCount(response.data.pagination.total)
      }
    } catch (err: any) {
      console.error('Error fetching cases:', err)
      
      // Handle different error scenarios gracefully
      const status = err.response?.status
      const message = err.response?.data?.message || err.response?.data?.msg
      
      if (status === 401 || message === 'Missing Authorization Header') {
        // Auth issue - for new users, just show empty state instead of error
        console.warn('Authentication issue when fetching cases - showing empty state for new user')
        setCases([])
        setPagination({
          page: 1,
          per_page: 12,
          total: 0,
          pages: 0,
          has_next: false,
          has_prev: false
        })
        setTotalCasesCount(0)
      } else if (status === 404) {
        // No cases found - show empty state
        setCases([])
        setPagination({
          page: 1,
          per_page: 12,
          total: 0,
          pages: 0,
          has_next: false,
          has_prev: false
        })
        setTotalCasesCount(0)
      } else if (status === 200 && (!err.response?.data?.data?.cases || err.response.data.data.cases.length === 0)) {
        // Successful response but no cases - show empty state
        setCases([])
        setPagination(err.response.data.data.pagination || {
          page: 1,
          per_page: 12,
          total: 0,
          pages: 0,
          has_next: false,
          has_prev: false
        })
        setTotalCasesCount(0)
      } else {
        // Other errors - show generic error
        setError(message || 'Failed to load cases. Please check your connection and try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleCreateCase = async (caseData: Partial<CaseData>) => {
    try {
      // Ensure required fields are present
      const createData = {
        name: caseData.name!,
        description: caseData.description,
        case_number: caseData.case_number,  // Include case_number
        incident_date: caseData.incident_date,
        incident_location: caseData.incident_location,
        incident_description: caseData.incident_description,
        status: caseData.status,
        priority: caseData.priority,
        tags: caseData.tags,
        court_jurisdiction: caseData.court_jurisdiction,
        opposing_party: caseData.opposing_party,
        legal_theory: caseData.legal_theory
      }
      await casesAPI.createCase(createData)
      setCreating(false)
      fetchCases()
    } catch (err: any) {
      throw new Error(err.response?.data?.message || 'Failed to create case')
    }
  }

  const handleUpdateCase = async (caseData: Partial<CaseData>) => {
    if (!editing?.id) return
    
    try {
      await casesAPI.updateCase(editing.id, caseData)
      setEditing(null)
      fetchCases()
    } catch (err: any) {
      throw new Error(err.response?.data?.message || 'Failed to update case')
    }
  }

  const handleDeleteCase = async (caseId: string) => {
    if (!confirm('Are you sure you want to delete this case? This action cannot be undone.')) {
      return
    }

    try {
      setDeleting(caseId)
      await casesAPI.deleteCase(caseId)
      fetchCases()
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to delete case')
    } finally {
      setDeleting(null)
    }
  }

  const handleViewCase = (caseId: string) => {
    navigate(`/cases/${caseId}`)
  }

  const handleFilterChange = (key: keyof CasesFilters, value: string | number) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: key === 'page' ? Number(value) : 1 // Reset to page 1 when changing filters
    }))
  }



  if (creating) {
    return (
      <div className="space-y-6">
        <CaseForm
          mode="create"
          onSubmit={handleCreateCase}
          onCancel={() => setCreating(false)}
        />
      </div>
    )
  }

  if (editing) {
    return (
      <div className="space-y-6">
        <CaseForm
          mode="edit"
          case={editing}
          onSubmit={handleUpdateCase}
          onCancel={() => setEditing(null)}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cases</h1>
          <p className="text-gray-600">Manage your legal cases and video evidence</p>
        </div>
        <button
          onClick={() => setCreating(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          New Case
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-64">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <input
              type="text"
              value={filters.search || ''}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              placeholder="Search cases by name, number, or location..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={filters.status || ''}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="analyzing">Analyzing</option>
              <option value="completed">Completed</option>
              <option value="archived">Archived</option>
              <option value="closed">Closed</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              value={filters.priority || ''}
              onChange={(e) => handleFilterChange('priority', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          {/* Clear filters button - only show when filters are active */}
          {(filters.search || filters.status || filters.priority) && (
            <button
              onClick={() => setFilters({ page: 1, per_page: 12, search: '', status: '', priority: '' })}
              className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
            <button
              onClick={() => setError(null)}
              className="ml-auto pl-3"
            >
              <svg className="w-5 h-5 text-red-400 hover:text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Cases Grid */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading cases...</span>
        </div>
      ) : cases.length === 0 ? (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {totalCasesCount === 0 ? (
            // No cases at all - first time user
            <>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No cases found</h3>
              <p className="mt-1 text-sm text-gray-500">Get started by creating your first case.</p>
              <div className="mt-6">
                <button
                  onClick={() => setCreating(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Create your first case
                </button>
              </div>
            </>
          ) : (
            // Has cases but none match current filters
            <>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No cases match your filters</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your search criteria or clear the filters to see all cases.
              </p>
              <div className="mt-6 space-x-3">
                <button
                  onClick={() => setFilters({ page: 1, per_page: 12, search: '', status: '', priority: '' })}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Clear Filters
                </button>
                <button
                  onClick={() => setCreating(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  New Case
                </button>
              </div>
            </>
          )}
        </div>
      ) : (
        <>
          {/* Cases Grid */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {cases.map((case_) => (
              <CaseCard
                key={case_.id}
                case={case_}
                onView={handleViewCase}
                onEdit={(caseId) => {
                  const caseToEdit = cases.find(c => c.id === caseId)
                  if (caseToEdit) setEditing(caseToEdit)
                }}
                onDelete={handleDeleteCase}
              />
            ))}
          </div>

          {/* Pagination */}
          {pagination.pages > 1 && (
            <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6">
              <div className="flex flex-1 justify-between sm:hidden">
                <button
                  onClick={() => handleFilterChange('page', pagination.page - 1)}
                  disabled={!pagination.has_prev}
                  className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => handleFilterChange('page', pagination.page + 1)}
                  disabled={!pagination.has_next}
                  className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
              <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Showing{' '}
                    <span className="font-medium">
                      {((pagination.page - 1) * pagination.per_page) + 1}
                    </span>{' '}
                    to{' '}
                    <span className="font-medium">
                      {Math.min(pagination.page * pagination.per_page, pagination.total)}
                    </span>{' '}
                    of{' '}
                    <span className="font-medium">{pagination.total}</span> results
                  </p>
                </div>
                <div>
                  <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                    <button
                      onClick={() => handleFilterChange('page', pagination.page - 1)}
                      disabled={!pagination.has_prev}
                      className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <span className="sr-only">Previous</span>
                      <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z" clipRule="evenodd" />
                      </svg>
                    </button>
                    
                    {/* Page numbers */}
                    {Array.from({ length: Math.min(5, pagination.pages) }, (_, i) => {
                      const pageNum = pagination.page <= 3 ? i + 1 : 
                                     pagination.page >= pagination.pages - 2 ? pagination.pages - 4 + i :
                                     pagination.page - 2 + i
                      return (
                        <button
                          key={pageNum}
                          onClick={() => handleFilterChange('page', pageNum)}
                          className={`relative inline-flex items-center px-4 py-2 text-sm font-semibold ${
                            pageNum === pagination.page
                              ? 'z-10 bg-blue-600 text-white focus:z-20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600'
                              : 'text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0'
                          }`}
                        >
                          {pageNum}
                        </button>
                      )
                    })}

                    <button
                      onClick={() => handleFilterChange('page', pagination.page + 1)}
                      disabled={!pagination.has_next}
                      className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <span className="sr-only">Next</span>
                      <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default CasesPage 