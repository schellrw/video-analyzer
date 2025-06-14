import React, { useState, useRef } from 'react'
import { toast } from '@/stores/toastStore'

interface QuickVideoUploadProps {
  onUploadSuccess: (videoId: string, caseName: string) => void
  onCancel?: () => void
}

const QuickVideoUpload: React.FC<QuickVideoUploadProps> = ({ onUploadSuccess, onCancel }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [caseName, setCaseName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.size > 2048 * 1024 * 1024) { // 2GB limit
        toast.error('File too large', 'Please select a video file smaller than 2GB')
        return
      }
      
      if (!file.type.startsWith('video/')) {
        toast.error('Invalid file type', 'Please select a video file')
        return
      }
      
      setSelectedFile(file)
      
      // Auto-generate case name from file name if not set
      if (!caseName) {
        const fileName = file.name.replace(/\.[^/.]+$/, "") // Remove extension
        setCaseName(fileName.charAt(0).toUpperCase() + fileName.slice(1))
      }
    }
  }

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    if (file) {
      if (file.type.startsWith('video/')) {
        setSelectedFile(file)
        if (!caseName) {
          const fileName = file.name.replace(/\.[^/.]+$/, "")
          setCaseName(fileName.charAt(0).toUpperCase() + fileName.slice(1))
        }
      } else {
        toast.error('Invalid file type', 'Please drop a video file')
      }
    }
  }

  const handleUpload = async () => {
    if (!selectedFile || !caseName.trim()) {
      toast.error('Missing information', 'Please select a video file and enter a case name')
      return
    }

    setUploading(true)
    setUploadProgress(0)

    try {
      // Simulate upload progress for now
      // In a real implementation, this would upload to your backend
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          const next = prev + Math.random() * 20
          return next > 90 ? 90 : next
        })
      }, 500)

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      // Simulate successful upload
      const mockVideoId = 'video_' + Date.now()
      
      toast.success('Upload successful!', 'Your video has been uploaded and analysis has started')
      onUploadSuccess(mockVideoId, caseName)
      
    } catch (error: any) {
      toast.error('Upload failed', error.message)
    } finally {
      setUploading(false)
    }
  }

  const resetForm = () => {
    setSelectedFile(null)
    setCaseName('')
    setUploadProgress(0)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Upload Your Video
          </h2>
          <p className="text-gray-600">
            Get AI-powered analysis in minutes. Simply drag and drop your video file or click to browse.
          </p>
        </div>

        {!selectedFile ? (
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-400 transition-colors cursor-pointer"
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="mx-auto w-16 h-16 text-gray-400 mb-4">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Drop your video here
            </h3>
            <p className="text-gray-500 mb-4">
              Upload your video evidence for AI-powered analysis. Our system will automatically detect 
              key events, transcribe audio, and identify potential violations.
            </p>
            <p className="text-sm text-gray-400 mb-6">
              Supports MP4, MOV, AVI files up to 2GB
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        ) : (
          <div className="space-y-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500">
                      {(selectedFile.size / (1024 * 1024)).toFixed(1)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={resetForm}
                  className="text-gray-400 hover:text-gray-600 p-1"
                  disabled={uploading}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div>
              <label htmlFor="caseName" className="block text-sm font-medium text-gray-700 mb-2">
                Case Name
              </label>
              <input
                id="caseName"
                type="text"
                value={caseName}
                onChange={(e) => setCaseName(e.target.value)}
                placeholder="Enter a name for this case"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
                disabled={uploading}
              />
            </div>

            {uploading && (
              <div>
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Uploading...</span>
                  <span>{Math.round(uploadProgress)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            <div className="flex space-x-4">
              <button
                onClick={handleUpload}
                disabled={uploading || !caseName.trim()}
                className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {uploading ? 'Uploading...' : 'Start Analysis'}
              </button>
              {onCancel && (
                <button
                  onClick={onCancel}
                  disabled={uploading}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Cancel
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default QuickVideoUpload 