import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { supabaseAuth, type AuthUser } from '@/services/supabaseAuth'
import type { Session } from '@supabase/supabase-js'

interface AuthState {
  user: AuthUser | null
  session: Session | null
  isAuthenticated: boolean
  isLoading: boolean
  isInitialized: boolean
  // Actions
  signIn: (email: string, password: string) => Promise<{ success: boolean; message?: string; needsEmailConfirmation?: boolean; user: AuthUser | null; session: Session | null }>
  signUp: (userData: {
    email: string
    password: string
    firstName: string
    lastName: string
    organization?: string
    role?: string
  }) => Promise<{ success: boolean; message?: string; needsEmailConfirmation?: boolean; user: AuthUser | null; session: Session | null }>
  signOut: () => Promise<void>
  resendConfirmation: (email: string) => Promise<{ success: boolean; message: string }>
  initializeAuth: () => Promise<void>
  setUser: (user: AuthUser | null, session: Session | null) => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      session: null,
      isAuthenticated: false,
      isLoading: true,
      isInitialized: false,

      signIn: async (email: string, password: string) => {
        // Don't set loading here to prevent bounce - let the login form handle its own loading
        try {
          const result = await supabaseAuth.signIn(email, password)
          
          if (result.success && result.user && result.session) {
            set({
              user: result.user,
              session: result.session,
              isAuthenticated: true,
              isLoading: false,
              isInitialized: true
            })
          } else {
            // Only set loading false if auth failed, don't change auth state
            set({ isLoading: false })
          }
          
          return {
            success: result.success,
            message: result.message,
            needsEmailConfirmation: result.needsEmailConfirmation,
            user: result.user ?? null,
            session: result.session ?? null
          }
        } catch (error: any) {
          set({ isLoading: false })
          return {
            success: false,
            message: error.message || 'Sign in failed',
            user: null,
            session: null
          }
        }
      },

      signUp: async (userData) => {
        // Don't set loading here to prevent bounce - let the signup form handle its own loading
        try {
          const result = await supabaseAuth.signUp(userData)
          
          if (result.success && result.user && result.session) {
            set({
              user: result.user,
              session: result.session,
              isAuthenticated: true,
              isLoading: false,
              isInitialized: true
            })
          } else {
            set({ isLoading: false })
          }
          
          return {
            success: result.success,
            message: result.message,
            needsEmailConfirmation: result.needsEmailConfirmation,
            user: result.user ?? null,
            session: result.session ?? null
          }
        } catch (error: any) {
          set({ isLoading: false })
          return {
            success: false,
            message: error.message || 'Registration failed',
            user: null,
            session: null
          }
        }
      },

      signOut: async () => {
        set({ isLoading: true })
        try {
          await supabaseAuth.signOut()
          set({
            user: null,
            session: null,
            isAuthenticated: false,
            isLoading: false,
            isInitialized: true
          })
        } catch (error) {
          console.error('Sign out error:', error)
          set({ isLoading: false })
        }
      },

      resendConfirmation: async (email: string) => {
        return await supabaseAuth.resendConfirmation(email)
      },

      initializeAuth: async () => {
        // Only show loading during initial app load
        if (!get().isInitialized) {
          set({ isLoading: true })
        }
        
        try {
          // Get current session
          const { user, session } = await supabaseAuth.getCurrentSession()
          
          set({
            user,
            session,
            isAuthenticated: !!user,
            isLoading: false,
            isInitialized: true
          })

          // Listen for auth state changes
          supabaseAuth.onAuthStateChange((user, session) => {
            set({
              user,
              session,
              isAuthenticated: !!user,
              isLoading: false,
              isInitialized: true
            })
          })
        } catch (error) {
          console.error('Auth initialization error:', error)
          set({
            user: null,
            session: null,
            isAuthenticated: false,
            isLoading: false,
            isInitialized: true
          })
        }
      },

      setUser: (user: AuthUser | null, session: Session | null) => {
        set({
          user,
          session,
          isAuthenticated: !!user,
          isInitialized: true
        })
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      }
    }),
    {
      name: 'auth-storage',
      // Only persist user data, not session or loading states
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
) 