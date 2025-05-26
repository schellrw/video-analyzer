import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { CheckCircle, Mail, AlertTriangle } from 'lucide-react'

const EmailConfirmationPage = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { resendConfirmation, initializeAuth } = useAuthStore()
  
  const [email, setEmail] = useState(searchParams.get('email') || '')
  const [isResending, setIsResending] = useState(false)
  const [resendMessage, setResendMessage] = useState('')
  const [resendSuccess, setResendSuccess] = useState(false)
  const [confirmationStatus, setConfirmationStatus] = useState<'waiting' | 'confirmed' | 'error'>('waiting')

  useEffect(() => {
    // Check if user just confirmed their email (from URL hash)
    const checkConfirmation = async () => {
      const hash = window.location.hash
      if (hash.includes('access_token') || hash.includes('type=signup')) {
        setConfirmationStatus('confirmed')
        // Initialize auth to get the new session
        await initializeAuth()
        // Redirect to dashboard after a short delay
        setTimeout(() => {
          navigate('/')
        }, 2000)
      }
    }

    checkConfirmation()
  }, [initializeAuth, navigate])

  const handleResendConfirmation = async () => {
    if (!email) {
      setResendMessage('Please enter your email address')
      setResendSuccess(false)
      return
    }

    setIsResending(true)
    setResendMessage('')
    
    try {
      const result = await resendConfirmation(email)
      setResendMessage(result.message)
      setResendSuccess(result.success)
    } catch (error: any) {
      setResendMessage(error.message || 'Failed to resend confirmation email')
      setResendSuccess(false)
    } finally {
      setIsResending(false)
    }
  }

  const handleBackToLogin = () => {
    navigate('/login')
  }

  if (confirmationStatus === 'confirmed') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <CheckCircle className="mx-auto h-16 w-16 text-green-500" />
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
              Email Confirmed!
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Your email has been successfully confirmed. Redirecting to dashboard...
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Mail className="mx-auto h-16 w-16 text-blue-500" />
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Check Your Email
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            We've sent a confirmation link to your email address. Please click the link to complete your registration.
          </p>
        </div>

        <div className="bg-white p-8 rounded-lg shadow">
          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <Mail className="h-5 w-5 text-blue-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">
                    Confirmation Email Sent
                  </h3>
                  <div className="mt-2 text-sm text-blue-700">
                    <p>
                      Please check your email inbox (and spam folder) for a confirmation link.
                      The link will expire in 24 hours.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your email to resend confirmation"
                />
              </div>

              {resendMessage && (
                <div className={`p-3 rounded-md ${
                  resendSuccess 
                    ? 'bg-green-100 border border-green-400 text-green-700'
                    : 'bg-red-100 border border-red-400 text-red-700'
                }`}>
                  <div className="flex">
                    <div className="flex-shrink-0">
                                           {resendSuccess ? (
                       <CheckCircle className="h-5 w-5 text-green-400" />
                     ) : (
                       <AlertTriangle className="h-5 w-5 text-red-400" />
                     )}
                    </div>
                    <div className="ml-3">
                      <p className="text-sm">{resendMessage}</p>
                    </div>
                  </div>
                </div>
              )}

              <button
                onClick={handleResendConfirmation}
                disabled={isResending || !email}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isResending ? 'Sending...' : 'Resend Confirmation Email'}
              </button>
            </div>

            <div className="text-center">
              <button
                onClick={handleBackToLogin}
                className="text-blue-600 hover:text-blue-500 text-sm font-medium"
              >
                Back to Login
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmailConfirmationPage 