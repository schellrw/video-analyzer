import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { casesAPI, CaseData } from '../services/api'
import CaseForm from '../components/CaseForm'
import { toast } from '@/stores/toastStore'

const CaseEditPage = () => {
  const { id: caseId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [caseData, setCaseData] = useState<CaseData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (caseId) {
      fetchCase()
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
      toast.error('Error', 'Failed to load case details')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateCase = async (updatedCaseData: Partial<CaseData>) => {
    try {
      setSaving(true)
      await casesAPI.updateCase(caseId!, updatedCaseData)
      toast.success('Success', 'Case updated successfully')
      navigate(`/cases/${caseId}`)
    } catch (err: any) {
      toast.error('Error', err.response?.data?.message || 'Failed to update case')
      throw err
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    navigate(`/cases/${caseId}`)
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
      <CaseForm
        mode="edit"
        case={caseData}
        onSubmit={handleUpdateCase}
        onCancel={handleCancel}
        isLoading={saving}
      />
    </div>
  )
}

export default CaseEditPage 