# Deployment Guide

## Overview
This guide covers deployment of the Video Analyzer platform to production environments.

## Prerequisites
- Docker and Docker Compose
- Node.js 18+
- Python 3.11+
- Supabase account
- Digital Ocean account
- Netlify account (optional for frontend)

## Environment Setup

### 1. Supabase Configuration
1. Create new project in Supabase
2. Run database migrations:
```sql
-- Users table (extends Supabase auth.users)
CREATE TABLE profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email VARCHAR NOT NULL,
  first_name VARCHAR NOT NULL,
  last_name VARCHAR NOT NULL,
  organization VARCHAR,
  role VARCHAR CHECK (role IN ('attorney', 'investigator', 'admin')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cases table
CREATE TABLE cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) NOT NULL,
  name VARCHAR NOT NULL,
  description TEXT,
  incident_date TIMESTAMP WITH TIME ZONE,
  location VARCHAR,
  tags TEXT[],
  status VARCHAR DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Videos table
CREATE TABLE videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
  filename VARCHAR NOT NULL,
  original_filename VARCHAR NOT NULL,
  file_size BIGINT,
  duration REAL,
  format VARCHAR,
  storage_url VARCHAR,
  status VARCHAR DEFAULT 'uploaded',
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analysis results table
CREATE TABLE analysis_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
  analysis_type VARCHAR NOT NULL,
  results JSONB NOT NULL,
  confidence REAL,
  status VARCHAR DEFAULT 'completed',
  processing_time INTERVAL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own profile" ON profiles 
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles 
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own cases" ON cases 
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view videos in own cases" ON videos 
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM cases 
      WHERE cases.id = videos.case_id 
      AND cases.user_id = auth.uid()
    )
  );
```

3. Set up storage bucket for video files
4. Configure authentication providers

### 2. Digital Ocean Spaces
1. Create Spaces bucket for file storage
2. Generate API keys
3. Configure CORS for web uploads

### 3. Environment Variables

#### Backend (.env)
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key-here

# Redis/Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Digital Ocean Spaces
DO_SPACES_KEY=your-spaces-key
DO_SPACES_SECRET=your-spaces-secret
DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
DO_SPACES_BUCKET=your-bucket-name

# AI Models
HUGGINGFACE_API_KEY=your-hf-api-key
OPENAI_API_KEY=your-openai-key  # Optional

# Email (for notifications)
SENDGRID_API_KEY=your-sendgrid-key
FROM_EMAIL=noreply@yourdomain.com

# Monitoring
SENTRY_DSN=your-sentry-dsn  # Optional
```

#### Frontend (.env.local)
```bash
# API Configuration
VITE_API_URL=https://api.yourdomain.com
VITE_ENVIRONMENT=production

# Supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Optional
VITE_SENTRY_DSN=your-frontend-sentry-dsn
```

## Deployment Options

### Option 1: Digital Ocean App Platform

1. **Setup Repository**
```bash
git clone https://github.com/yourusername/video-analyzer.git
cd video-analyzer
```

2. **Deploy using App Spec**
```bash
doctl apps create --spec infrastructure/digital-ocean/app.yaml
```

3. **Configure Environment Variables**
- Set all required environment variables in Digital Ocean dashboard
- Enable automatic deployments from GitHub

### Option 2: Docker Compose (VPS)

1. **Prepare VPS**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Clone and Deploy**
```bash
git clone https://github.com/yourusername/video-analyzer.git
cd video-analyzer

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit environment files with your values
nano backend/.env
nano frontend/.env.local

# Build and start services
docker-compose -f docker-compose.prod.yml up -d
```

3. **Setup SSL with Let's Encrypt**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificates
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Option 3: Kubernetes (Advanced)

1. **Prepare Kubernetes Manifests**
```bash
# Create namespace
kubectl create namespace video-analyzer

# Apply configurations
kubectl apply -f infrastructure/k8s/
```

## Frontend Deployment (Netlify)

1. **Connect Repository**
- Link GitHub repository to Netlify
- Set build directory to `frontend`
- Set publish directory to `frontend/dist`

2. **Build Settings**
```bash
# Build command
npm run build

# Build directory
frontend
```

3. **Environment Variables**
- Set all VITE_ prefixed variables in Netlify dashboard

## Post-Deployment Checklist

### 1. Health Checks
```bash
# Backend health
curl https://api.yourdomain.com/api/health

# Frontend
curl https://yourdomain.com

# Database connection
# Check Supabase dashboard for connection status
```

### 2. SSL Certificate Verification
```bash
# Check SSL rating
curl -I https://yourdomain.com
curl -I https://api.yourdomain.com
```

### 3. Performance Testing
```bash
# Load testing with Artillery
npm install -g artillery
artillery quick --count 10 --num 3 https://api.yourdomain.com/api/health
```

### 4. Monitoring Setup

#### Application Monitoring
```bash
# Install monitoring agents
# Datadog, New Relic, or similar
```

#### Log Aggregation
```bash
# Setup log forwarding to external service
# ELK Stack, Datadog Logs, etc.
```

## Backup Strategy

### 1. Database Backups
```bash
# Automated Supabase backups are included
# Additional manual backup:
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. File Storage Backups
```bash
# Digital Ocean Spaces backup
# Use rclone or similar tool
rclone sync spaces:your-bucket /backup/location
```

### 3. Application Code
```bash
# Automated GitHub backups
# Tag releases for easy rollback
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0
```

## Scaling Considerations

### 1. Horizontal Scaling
- Use load balancers for multiple backend instances
- Scale Celery workers based on queue depth
- Implement Redis clustering for high availability

### 2. Database Scaling
- Use read replicas for query optimization
- Implement connection pooling
- Consider database sharding for large datasets

### 3. File Storage Scaling
- Use CDN for static assets
- Implement multi-region storage
- Optimize video encoding and compression

## Troubleshooting

### Common Issues

1. **Video Upload Failures**
```bash
# Check file size limits
# Verify Digital Ocean Spaces configuration
# Check network timeouts
```

2. **AI Processing Delays**
```bash
# Monitor Celery queue
celery -A app.celery inspect active

# Check worker status
celery -A app.celery inspect stats
```

3. **Authentication Issues**
```bash
# Verify Supabase configuration
# Check JWT token expiration
# Validate CORS settings
```

### Monitoring Commands
```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f celery-worker

# System resources
htop
iotop
```

## Security Checklist

- [ ] SSL certificates installed and configured
- [ ] Environment variables secured
- [ ] Database access restricted
- [ ] API rate limiting enabled
- [ ] File upload validation implemented
- [ ] Regular security updates scheduled
- [ ] Backup and recovery tested
- [ ] Monitoring and alerting configured

## Rollback Procedure

1. **Quick Rollback (Docker)**
```bash
# Pull previous image
docker-compose pull backend:previous-tag
docker-compose up -d backend
```

2. **Database Rollback**
```bash
# Restore from backup
psql $DATABASE_URL < backup_previous.sql
```

3. **Frontend Rollback**
```bash
# Netlify automatic rollback from dashboard
# Or redeploy previous commit
``` 