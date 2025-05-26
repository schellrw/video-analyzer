import React from 'react'
import { CaseData } from '../services/api'

interface CaseCardProps {
  case: CaseData
  onView: (caseId: string) => void
  onEdit?: (caseId: string) => void
  onDelete?: (caseId: string) => void
}

const CaseCard: React.FC<CaseCardProps> = ({ case: caseItem, onView, onEdit, onDelete }) => {
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'analyzing':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'archived':
        return 'bg-gray-100 text-gray-800 border-gray-200'
      case 'closed':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'low':
        return 'bg-green-100 text-green-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'high':
        return 'bg-orange-100 text-orange-800'
      case 'urgent':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString()
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200">
      <div className="p-6">
        {/* Header */}
        <div className="mb-4">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-gray-900 mb-1 truncate">
                {caseItem.name}
              </h3>
            </div>
            <div className="flex space-x-2 flex-shrink-0 ml-3">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(caseItem.status)}`}>
                {caseItem.status}
              </span>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(caseItem.priority)}`}>
                {caseItem.priority}
              </span>
            </div>
          </div>
          {/* Case number on its own line with full width */}
          {caseItem.case_number ? (
            <p className="text-sm text-gray-600 font-mono">
              Case #{caseItem.case_number}
            </p>
          ) : (
            <p className="text-sm text-gray-400 italic">
              No case number assigned
            </p>
          )}
        </div>

        {/* Description */}
        {caseItem.description && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">
            {caseItem.description}
          </p>
        )}

        {/* Case Details */}
        <div className="space-y-2 mb-4">
          {caseItem.incident_date && (
            <div className="flex items-center text-sm text-gray-600">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Incident: {formatDate(caseItem.incident_date)}
            </div>
          )}
          {caseItem.incident_location && (
            <div className="flex items-center text-sm text-gray-600">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {caseItem.incident_location}
            </div>
          )}
        </div>

        {/* Video Count and Progress */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Videos: {caseItem.video_count || 0}</span>
            <span>Analysis: {caseItem.analysis_progress?.percentage || 0}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: `${caseItem.analysis_progress?.percentage || 0}%` }}
            ></div>
          </div>
        </div>

        {/* Tags */}
        {caseItem.tags && caseItem.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-4">
            {caseItem.tags.slice(0, 3).map((tag, index) => (
              <span key={index} className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700">
                {tag}
              </span>
            ))}
            {caseItem.tags.length > 3 && (
              <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-50 text-gray-700">
                +{caseItem.tags.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <span className="text-xs text-gray-500">
            Created {formatDate(caseItem.created_at)}
          </span>
          <div className="flex space-x-2">
            <button
              onClick={() => onView(caseItem.id!)}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              View
            </button>
            {onEdit && (
              <button
                onClick={() => onEdit(caseItem.id!)}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Edit
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(caseItem.id!)}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Delete
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CaseCard 