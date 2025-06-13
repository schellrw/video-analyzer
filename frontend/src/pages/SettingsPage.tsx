import React, { useState } from 'react'
import { toast } from '@/stores/toastStore'

interface VideoTypeSettings {
  enabled: boolean
  priority: number
  analysisOptions: {
    detectObjects: boolean
    detectPeople: boolean
    detectActions: boolean
    transcribeAudio: boolean
    detectViolations: boolean
  }
}

interface Settings {
  videoTypes: {
    bodycam: VideoTypeSettings
    cctv: VideoTypeSettings
    dashcam: VideoTypeSettings
    mobile: VideoTypeSettings
    other: VideoTypeSettings
  }
  analysisPreferences: {
    confidenceThreshold: number
    maxConcurrentAnalysis: number
    autoStartAnalysis: boolean
    notifyOnCompletion: boolean
    saveIntermediateResults: boolean
  }
  storagePreferences: {
    maxVideoSize: number
    retentionPeriod: number
    compressionEnabled: boolean
    compressionQuality: number
  }
}

const DEFAULT_SETTINGS: Settings = {
  videoTypes: {
    bodycam: {
      enabled: true,
      priority: 1,
      analysisOptions: {
        detectObjects: true,
        detectPeople: true,
        detectActions: true,
        transcribeAudio: true,
        detectViolations: true
      }
    },
    cctv: {
      enabled: true,
      priority: 2,
      analysisOptions: {
        detectObjects: true,
        detectPeople: true,
        detectActions: true,
        transcribeAudio: false,
        detectViolations: true
      }
    },
    dashcam: {
      enabled: true,
      priority: 3,
      analysisOptions: {
        detectObjects: true,
        detectPeople: true,
        detectActions: true,
        transcribeAudio: true,
        detectViolations: true
      }
    },
    mobile: {
      enabled: true,
      priority: 4,
      analysisOptions: {
        detectObjects: true,
        detectPeople: true,
        detectActions: true,
        transcribeAudio: true,
        detectViolations: true
      }
    },
    other: {
      enabled: true,
      priority: 5,
      analysisOptions: {
        detectObjects: true,
        detectPeople: true,
        detectActions: true,
        transcribeAudio: true,
        detectViolations: true
      }
    }
  },
  analysisPreferences: {
    confidenceThreshold: 75,
    maxConcurrentAnalysis: 3,
    autoStartAnalysis: true,
    notifyOnCompletion: true,
    saveIntermediateResults: true
  },
  storagePreferences: {
    maxVideoSize: 500, // MB
    retentionPeriod: 365, // days
    compressionEnabled: true,
    compressionQuality: 80 // percentage
  }
}

const SettingsPage = () => {
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS)
  const [activeTab, setActiveTab] = useState<'video-types' | 'analysis' | 'storage'>('video-types')
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = async () => {
    setIsSaving(true)
    try {
      // In a real implementation, this would save to the backend
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('Settings saved', 'Your preferences have been updated successfully')
    } catch (error) {
      toast.error('Error', 'Failed to save settings')
    } finally {
      setIsSaving(false)
    }
  }

  const handleVideoTypeChange = (type: keyof Settings['videoTypes'], field: keyof VideoTypeSettings, value: any) => {
    setSettings(prev => ({
      ...prev,
      videoTypes: {
        ...prev.videoTypes,
        [type]: {
          ...prev.videoTypes[type],
          [field]: value
        }
      }
    }))
  }

  const handleAnalysisOptionChange = (type: keyof Settings['videoTypes'], option: keyof VideoTypeSettings['analysisOptions'], value: boolean) => {
    setSettings(prev => ({
      ...prev,
      videoTypes: {
        ...prev.videoTypes,
        [type]: {
          ...prev.videoTypes[type],
          analysisOptions: {
            ...prev.videoTypes[type].analysisOptions,
            [option]: value
          }
        }
      }
    }))
  }

  const handleAnalysisPreferenceChange = (field: keyof Settings['analysisPreferences'], value: any) => {
    setSettings(prev => ({
      ...prev,
      analysisPreferences: {
        ...prev.analysisPreferences,
        [field]: value
      }
    }))
  }

  const handleStoragePreferenceChange = (field: keyof Settings['storagePreferences'], value: any) => {
    setSettings(prev => ({
      ...prev,
      storagePreferences: {
        ...prev.storagePreferences,
        [field]: value
      }
    }))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Configure your video analysis preferences</p>
        </div>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {isSaving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('video-types')}
              className={`px-6 py-4 text-sm font-medium ${
                activeTab === 'video-types'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Video Types
            </button>
            <button
              onClick={() => setActiveTab('analysis')}
              className={`px-6 py-4 text-sm font-medium ${
                activeTab === 'analysis'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Analysis Preferences
            </button>
            <button
              onClick={() => setActiveTab('storage')}
              className={`px-6 py-4 text-sm font-medium ${
                activeTab === 'storage'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Storage
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'video-types' && (
            <div className="space-y-6">
              {Object.entries(settings.videoTypes).map(([type, config]) => (
                <div key={type} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={config.enabled}
                        onChange={(e) => handleVideoTypeChange(type as keyof Settings['videoTypes'], 'enabled', e.target.checked)}
                        className="h-4 w-4 text-blue-600 rounded border-gray-300"
                      />
                      <label className="ml-2 text-lg font-medium text-gray-900 capitalize">
                        {type}
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <label className="text-sm text-gray-600">Priority:</label>
                      <input
                        type="number"
                        min="1"
                        max="5"
                        value={config.priority}
                        onChange={(e) => handleVideoTypeChange(type as keyof Settings['videoTypes'], 'priority', parseInt(e.target.value))}
                        className="w-16 px-2 py-1 text-sm border rounded-md"
                        disabled={!config.enabled}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {Object.entries(config.analysisOptions).map(([option, enabled]) => (
                      <div key={option} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={enabled}
                          onChange={(e) => handleAnalysisOptionChange(type as keyof Settings['videoTypes'], option as keyof VideoTypeSettings['analysisOptions'], e.target.checked)}
                          className="h-4 w-4 text-blue-600 rounded border-gray-300"
                          disabled={!config.enabled}
                        />
                        <label className="ml-2 text-sm text-gray-700 capitalize">
                          {option.replace(/([A-Z])/g, ' $1').trim()}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'analysis' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confidence Threshold (%)
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={settings.analysisPreferences.confidenceThreshold}
                    onChange={(e) => handleAnalysisPreferenceChange('confidenceThreshold', parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="text-sm text-gray-500 text-right">
                    {settings.analysisPreferences.confidenceThreshold}%
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Concurrent Analysis
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={settings.analysisPreferences.maxConcurrentAnalysis}
                    onChange={(e) => handleAnalysisPreferenceChange('maxConcurrentAnalysis', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.analysisPreferences.autoStartAnalysis}
                    onChange={(e) => handleAnalysisPreferenceChange('autoStartAnalysis', e.target.checked)}
                    className="h-4 w-4 text-blue-600 rounded border-gray-300"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Automatically start analysis after upload
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.analysisPreferences.notifyOnCompletion}
                    onChange={(e) => handleAnalysisPreferenceChange('notifyOnCompletion', e.target.checked)}
                    className="h-4 w-4 text-blue-600 rounded border-gray-300"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Notify when analysis is complete
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.analysisPreferences.saveIntermediateResults}
                    onChange={(e) => handleAnalysisPreferenceChange('saveIntermediateResults', e.target.checked)}
                    className="h-4 w-4 text-blue-600 rounded border-gray-300"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Save intermediate analysis results
                  </label>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'storage' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Maximum Video Size (MB)
                  </label>
                  <input
                    type="number"
                    min="100"
                    max="2000"
                    value={settings.storagePreferences.maxVideoSize}
                    onChange={(e) => handleStoragePreferenceChange('maxVideoSize', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Retention Period (days)
                  </label>
                  <input
                    type="number"
                    min="30"
                    max="3650"
                    value={settings.storagePreferences.retentionPeriod}
                    onChange={(e) => handleStoragePreferenceChange('retentionPeriod', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.storagePreferences.compressionEnabled}
                    onChange={(e) => handleStoragePreferenceChange('compressionEnabled', e.target.checked)}
                    className="h-4 w-4 text-blue-600 rounded border-gray-300"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Enable video compression
                  </label>
                </div>

                {settings.storagePreferences.compressionEnabled && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Compression Quality (%)
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={settings.storagePreferences.compressionQuality}
                      onChange={(e) => handleStoragePreferenceChange('compressionQuality', parseInt(e.target.value))}
                      className="w-full"
                    />
                    <div className="text-sm text-gray-500 text-right">
                      {settings.storagePreferences.compressionQuality}%
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SettingsPage 