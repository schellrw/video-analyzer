import { supabase } from './supabase'
import type { User, Session } from '@supabase/supabase-js'

export interface AuthUser {
  id: string
  email: string
  firstName: string
  lastName: string
  organization?: string
  role: string
  emailConfirmed: boolean
}

export interface AuthResponse {
  success: boolean
  user?: AuthUser
  session?: Session
  message?: string
  needsEmailConfirmation?: boolean
}

class SupabaseAuthService {
  // Register new user with email confirmation
  async signUp(userData: {
    email: string
    password: string
    firstName: string
    lastName: string
    organization?: string
    role?: string
  }): Promise<AuthResponse> {
    try {
      const { data, error } = await supabase.auth.signUp({
        email: userData.email,
        password: userData.password,
        options: {
          data: {
            first_name: userData.firstName,
            last_name: userData.lastName,
            organization: userData.organization || '',
            role: userData.role || 'attorney'
          }
        }
      })

      if (error) {
        return {
          success: false,
          message: error.message
        }
      }

      // If user is created but not confirmed
      if (data.user && !data.user.email_confirmed_at) {
        return {
          success: true,
          needsEmailConfirmation: true,
          message: 'Please check your email and click the confirmation link to complete registration.'
        }
      }

      // If user is immediately confirmed (shouldn't happen in production)
      if (data.user && data.session) {
        const authUser = await this.createUserProfile(data.user, data.session)
        return {
          success: true,
          user: authUser,
          session: data.session
        }
      }

      return {
        success: true,
        needsEmailConfirmation: true,
        message: 'Registration successful! Please check your email for confirmation.'
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Registration failed'
      }
    }
  }

  // Sign in existing user
  async signIn(email: string, password: string): Promise<AuthResponse> {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) {
        return {
          success: false,
          message: error.message
        }
      }

      if (data.user && data.session) {
        // Check if user has confirmed email
        if (!data.user.email_confirmed_at) {
          return {
            success: false,
            message: 'Please confirm your email address before signing in.'
          }
        }

        const authUser = await this.getUserProfile(data.user, data.session)
        return {
          success: true,
          user: authUser,
          session: data.session
        }
      }

      return {
        success: false,
        message: 'Sign in failed'
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Sign in failed'
      }
    }
  }

  // Sign out user
  async signOut(): Promise<{ success: boolean; message?: string }> {
    try {
      const { error } = await supabase.auth.signOut()
      
      if (error) {
        return {
          success: false,
          message: error.message
        }
      }

      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Sign out failed'
      }
    }
  }

  // Get current session
  async getCurrentSession(): Promise<{ user: AuthUser | null; session: Session | null }> {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      
      if (session?.user) {
        const authUser = await this.getUserProfile(session.user, session)
        return { user: authUser, session }
      }

      return { user: null, session: null }
    } catch (error) {
      console.error('Error getting current session:', error)
      return { user: null, session: null }
    }
  }

  // Listen to auth state changes
  onAuthStateChange(callback: (user: AuthUser | null, session: Session | null) => void) {
    return supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.user && event === 'SIGNED_IN') {
        const authUser = await this.getUserProfile(session.user, session)
        callback(authUser, session)
      } else {
        callback(null, null)
      }
    })
  }

  // Resend confirmation email
  async resendConfirmation(email: string): Promise<{ success: boolean; message: string }> {
    try {
      const { error } = await supabase.auth.resend({
        type: 'signup',
        email
      })

      if (error) {
        return {
          success: false,
          message: error.message
        }
      }

      return {
        success: true,
        message: 'Confirmation email sent successfully!'
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Failed to resend confirmation email'
      }
    }
  }

  // Create user profile in our backend after Supabase auth
  private async createUserProfile(user: User, session: Session): Promise<AuthUser> {
    try {
      // Call our backend to create user profile
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          supabase_user_id: user.id,
          email: user.email,
          first_name: user.user_metadata.first_name,
          last_name: user.user_metadata.last_name,
          organization: user.user_metadata.organization,
          role: user.user_metadata.role
        })
      })

      if (response.ok) {
        const data = await response.json()
        return {
          id: user.id,
          email: user.email!,
          firstName: data.data.first_name,
          lastName: data.data.last_name,
          organization: data.data.organization,
          role: data.data.role,
          emailConfirmed: !!user.email_confirmed_at
        }
      }
    } catch (error) {
      console.error('Error creating user profile:', error)
    }

    // Fallback to user metadata if backend call fails
    return {
      id: user.id,
      email: user.email!,
      firstName: user.user_metadata.first_name || '',
      lastName: user.user_metadata.last_name || '',
      organization: user.user_metadata.organization || '',
      role: user.user_metadata.role || 'attorney',
      emailConfirmed: !!user.email_confirmed_at
    }
  }

  // Get user profile from our backend
  private async getUserProfile(user: User, session: Session): Promise<AuthUser> {
    try {
      // Try to get profile from our backend
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        return {
          id: user.id,
          email: user.email!,
          firstName: data.data.first_name,
          lastName: data.data.last_name,
          organization: data.data.organization,
          role: data.data.role,
          emailConfirmed: !!user.email_confirmed_at
        }
      } else if (response.status === 404) {
        // Profile doesn't exist, create it
        console.log('Profile not found, creating new profile...')
        return await this.createUserProfile(user, session)
      }
    } catch (error) {
      console.error('Error fetching user profile:', error)
    }

    // Fallback to user metadata
    return {
      id: user.id,
      email: user.email!,
      firstName: user.user_metadata.first_name || '',
      lastName: user.user_metadata.last_name || '',
      organization: user.user_metadata.organization || '',
      role: user.user_metadata.role || 'attorney',
      emailConfirmed: !!user.email_confirmed_at
    }
  }
}

export const supabaseAuth = new SupabaseAuthService() 