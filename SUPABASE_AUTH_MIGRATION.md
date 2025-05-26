# 🔄 Supabase Auth Migration Guide

## Overview
This guide walks you through migrating from custom authentication to Supabase Auth, which will:
- ✅ Use Supabase's built-in authentication system
- ✅ Remove redundant custom User table
- ✅ Keep Profiles table linked to `auth.users`
- ✅ Enable advanced auth features (email verification, password reset, social login)

## 📋 Prerequisites

### 1. Supabase Environment Variables
Add these to your `.env` file:
```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret
```

### 2. Get Supabase Keys
1. Go to your Supabase Dashboard
2. Navigate to Settings > API
3. Copy the required keys:
   - **Project URL**: `https://your-project.supabase.co`
   - **Anon Key**: `eyJ...` (public key)
   - **Service Role Key**: `eyJ...` (private key - keep secure!)
   - **JWT Secret**: Found in Settings > API > JWT Settings

## 🚀 Migration Steps

### Step 1: Export Current Users
```bash
cd backend
python migration_supabase_auth.py
```
This creates `migration_users_export.json` with your current user data.

### Step 2: Create Users in Supabase Auth
1. Go to Supabase Dashboard > Authentication > Users
2. For each user in the export file:
   - Click "Add User"
   - Enter the email address
   - Set a temporary password (users will reset)
   - Enable "Auto Confirm User"
   - Click "Create User"
   - **Important**: Note the new `auth.user.id` for each user

### Step 3: Update Profiles Table
Update your profiles to reference the new Supabase auth user IDs:

```sql
-- Example: Update profile to reference new auth.user.id
UPDATE profiles 
SET id = 'new-supabase-auth-user-id' 
WHERE id = 'old-custom-user-id';
```

### Step 4: Update Backend Code

#### A. Update Models
Replace `backend/app/models/user.py` with the new profile-only model:
```python
# Remove User model, keep only Profile model
# Profile.id now references auth.users.id directly
```

#### B. Update Routes
Replace authentication routes:
```python
# In backend/app/__init__.py
from .routes.auth_supabase import auth_supabase_bp
app.register_blueprint(auth_supabase_bp, url_prefix='/api/auth')
```

#### C. Update JWT Middleware
Create new middleware to verify Supabase JWT tokens:
```python
# backend/app/middleware/supabase_auth.py
from functools import wraps
from flask import request, jsonify
from ..services.supabase_auth import supabase_auth

def require_supabase_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = supabase_auth.verify_jwt_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        request.current_user = user_data
        return f(*args, **kwargs)
    return decorated_function
```

### Step 5: Update Frontend Code

#### A. Install Supabase Client
```bash
cd frontend
npm install @supabase/supabase-js
```

#### B. Create Supabase Client
```typescript
// frontend/src/services/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

#### C. Update Auth Store
```typescript
// frontend/src/stores/authStore.ts
import { supabase } from '../services/supabase'

// Replace custom login with Supabase auth
const login = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  })
  
  if (error) throw error
  
  // Verify token with backend to get profile
  const response = await api.post('/auth/verify-token', {
    access_token: data.session.access_token
  })
  
  // Store user data and token
  setUser(response.data.user)
  setToken(data.session.access_token)
}
```

### Step 6: Database Cleanup
After confirming everything works:

```sql
-- Remove foreign key constraints
ALTER TABLE cases DROP CONSTRAINT IF EXISTS cases_created_by_fkey;

-- Drop the custom users table
DROP TABLE users CASCADE;

-- Update any other tables that referenced users
-- (Update foreign keys to reference auth.users if needed)
```

### Step 7: Environment Variables
Update your frontend `.env`:
```bash
# Frontend .env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 🔧 Testing the Migration

### 1. Test Authentication Flow
1. Try logging in with existing user credentials
2. Verify profile data loads correctly
3. Test token verification
4. Test protected routes

### 2. Test Registration
1. Register a new user
2. Verify user appears in Supabase Auth
3. Verify profile is created in your database

### 3. Test Case Management
1. Verify cases still load correctly
2. Test creating new cases
3. Verify user associations work

## 🚨 Rollback Plan
If something goes wrong:

1. **Keep the export file** (`migration_users_export.json`)
2. **Database backup**: Take a full backup before starting
3. **Restore custom auth**: Revert to original auth routes
4. **Restore users table**: Recreate from backup if needed

## 🎯 Benefits After Migration

### Enhanced Security
- ✅ Professional authentication system
- ✅ Built-in password policies
- ✅ Email verification
- ✅ Password reset functionality

### Better User Experience
- ✅ "Forgot password" functionality
- ✅ Email confirmation
- ✅ Social login options (Google, GitHub, etc.)
- ✅ Better session management

### Developer Experience
- ✅ Less authentication code to maintain
- ✅ Built-in security best practices
- ✅ Row Level Security integration
- ✅ Real-time subscriptions support

## 📞 Support
If you encounter issues during migration:
1. Check Supabase logs in Dashboard > Logs
2. Verify environment variables are correct
3. Test API endpoints with Postman/curl
4. Check browser console for frontend errors

## 🔄 Migration Checklist
- [ ] Export current users
- [ ] Create Supabase environment variables
- [ ] Create users in Supabase Auth
- [ ] Update profiles table references
- [ ] Update backend models and routes
- [ ] Update frontend auth service
- [ ] Test authentication flow
- [ ] Test case management
- [ ] Clean up old users table
- [ ] Update documentation

---

**Ready to start?** Run the export script and follow the steps above! 