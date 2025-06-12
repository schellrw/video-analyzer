import React, { useState } from 'react'
import { toast } from '@/stores/toastStore'

interface SampleReport {
  id: string
  title: string
  caseNumber: string
  dateGenerated: string
  type: 'analysis' | 'summary' | 'violations'
  status: 'completed' | 'processing' | 'draft'
  preview: string
  keyFindings: string[]
  violations?: {
    type: string
    confidence: number
    timestamp: string
    description: string
  }[]
}

const SAMPLE_REPORTS: SampleReport[] = [
  {
    id: 'rpt_001',
    title: 'Traffic Stop Video Analysis',
    caseNumber: 'CASE-2024-001',
    dateGenerated: '2024-01-15',
    type: 'analysis',
    status: 'completed',
    preview: 'Comprehensive analysis of traffic stop footage revealing multiple procedural concerns...',
    keyFindings: [
      'Officer failed to properly identify themselves',
      'No Miranda rights provided before questioning',
      'Use of force appeared disproportionate to threat level',
      'Vehicle search conducted without clear probable cause'
    ],
    violations: [
      {
        type: 'Fourth Amendment Violation',
        confidence: 85,
        timestamp: '02:34',
        description: 'Unreasonable search and seizure - vehicle searched without warrant or probable cause'
      },
      {
        type: 'Excessive Force',
        confidence: 78,
        timestamp: '04:12',
        description: 'Use of force appears disproportionate to resistance level shown by subject'
      }
    ]
  },
  {
    id: 'rpt_002',
    title: 'Body Camera Analysis Summary',
    caseNumber: 'CASE-2024-007',
    dateGenerated: '2024-01-12',
    type: 'summary',
    status: 'completed',
    preview: 'Executive summary of body-worn camera footage analysis for incident response review...',
    keyFindings: [
      'Clear documentation of incident timeline',
      'Officer maintained professional demeanor throughout',
      'Proper de-escalation techniques employed',
      'All required notifications were made'
    ]
  },
  {
    id: 'rpt_003',
    title: 'Civil Rights Violation Assessment',
    caseNumber: 'CASE-2024-012',
    dateGenerated: '2024-01-10',
    type: 'violations',
    status: 'processing',
    preview: 'Detailed analysis of potential civil rights violations based on video evidence...',
    keyFindings: [
      'Analysis in progress...',
      'Preliminary indicators suggest potential Section 1983 claim',
      'Multiple constitutional concerns identified'
    ],
    violations: [
      {
        type: 'Due Process Violation',
        confidence: 92,
        timestamp: '01:15',
        description: 'Subject denied opportunity to explain actions before arrest'
      }
    ]
  }
]

const ReportsPage = () => {
  const [selectedReport, setSelectedReport] = useState<SampleReport | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  const handleDownloadReport = (report: SampleReport) => {
    toast.info('Demo Mode', 'In a real application, this would download the full report as PDF')
  }

  const handleShareReport = (report: SampleReport) => {
    toast.info('Demo Mode', 'In a real application, this would generate a secure sharing link')
  }

  const getStatusColor = (status: SampleReport['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800'
      case 'draft':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeIcon = (type: SampleReport['type']) => {
    switch (type) {
      case 'analysis':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        )
      case 'summary':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        )
      case 'violations':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        )
    }
  }

  if (selectedReport) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setSelectedReport(null)}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Reports
          </button>
          <div className="flex space-x-3">
            <button
              onClick={() => handleShareReport(selectedReport)}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Share
            </button>
            <button
              onClick={() => handleDownloadReport(selectedReport)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Download PDF
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-8">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-3xl font-bold text-gray-900">{selectedReport.title}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedReport.status)}`}>
                {selectedReport.status.charAt(0).toUpperCase() + selectedReport.status.slice(1)}
              </span>
            </div>
            <div className="flex items-center text-gray-600 space-x-4">
              <span>Case: {selectedReport.caseNumber}</span>
              <span>Generated: {new Date(selectedReport.dateGenerated).toLocaleDateString()}</span>
            </div>
          </div>

          <div className="prose max-w-none">
            <h2>Executive Summary</h2>
            <p className="text-gray-700 leading-relaxed">{selectedReport.preview}</p>

            <h2>Key Findings</h2>
            <ul className="space-y-2">
              {selectedReport.keyFindings.map((finding, index) => (
                <li key={index} className="flex items-start">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span>{finding}</span>
                </li>
              ))}
            </ul>

            {selectedReport.violations && selectedReport.violations.length > 0 && (
              <>
                <h2>Identified Violations</h2>
                <div className="space-y-4">
                  {selectedReport.violations.map((violation, index) => (
                    <div key={index} className="border border-red-200 rounded-lg p-4 bg-red-50">
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
              </>
            )}

            <h2>Legal Analysis</h2>
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-blue-900">
                <strong>Note:</strong> This is a sample report for demonstration purposes. In a real implementation, 
                detailed legal analysis would include relevant case law, statutory references, and specific 
                recommendations for legal action.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600">AI-generated analysis reports for your cases</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex border border-gray-300 rounded-md">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 ${viewMode === 'grid' ? 'bg-gray-100' : ''}`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 ${viewMode === 'list' ? 'bg-gray-100' : ''}`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center">
          <svg className="w-6 h-6 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 className="text-blue-900 font-medium">Demo Reports</h3>
            <p className="text-blue-700 text-sm">
              These are sample reports for demonstration purposes. In the real application, reports would be generated from actual video analysis.
            </p>
          </div>
        </div>
      </div>

      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {SAMPLE_REPORTS.map((report) => (
            <div
              key={report.id}
              className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedReport(report)}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center text-gray-600">
                    {getTypeIcon(report.type)}
                    <span className="ml-2 text-sm capitalize">{report.type}</span>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                    {report.status}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{report.title}</h3>
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">{report.preview}</p>
                <div className="text-xs text-gray-500">
                  <p>Case: {report.caseNumber}</p>
                  <p>Generated: {new Date(report.dateGenerated).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="divide-y divide-gray-200">
            {SAMPLE_REPORTS.map((report) => (
              <div
                key={report.id}
                className="p-6 hover:bg-gray-50 cursor-pointer"
                onClick={() => setSelectedReport(report)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <div className="flex items-center text-gray-600 mr-4">
                        {getTypeIcon(report.type)}
                        <span className="ml-2 text-sm capitalize">{report.type}</span>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                        {report.status}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{report.title}</h3>
                    <p className="text-gray-600 text-sm mb-2 line-clamp-2">{report.preview}</p>
                    <div className="text-xs text-gray-500 flex space-x-4">
                      <span>Case: {report.caseNumber}</span>
                      <span>Generated: {new Date(report.dateGenerated).toLocaleDateString()}</span>
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

export default ReportsPage 