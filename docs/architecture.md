# Video Evidence Analysis Platform - Technical Architecture

## 1. System Overview

The Video Evidence Analysis Platform is built as a modern, scalable SaaS application with a clear separation of concerns between frontend, backend, AI processing, and data storage layers.

### 1.1 High-Level Architecture
- **Frontend**: React + Vite SPA deployed on Netlify
- **Backend**: Flask REST API deployed on Digital Ocean
- **Database**: Supabase (PostgreSQL) for structured data
- **File Storage**: Digital Ocean Spaces (S3-compatible) for video files
- **AI Processing**: Containerized ML services with GPU support
- **Queue System**: Redis + Celery for asynchronous processing

## 2. Frontend Architecture (React + Vite)

### 2.1 Technology Stack
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **State Management**: Zustand (lightweight alternative to Redux)
- **Routing**: React Router v6
- **UI Components**: Tailwind CSS + Headless UI
- **Video Player**: Custom player built on Video.js
- **HTTP Client**: Axios with interceptors for auth
- **File Upload**: react-dropzone with chunked upload support

### 2.2 Project Structure
```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # Basic UI primitives
│   │   ├── video/          # Video player components
│   │   ├── upload/         # File upload components
│   │   └── reports/        # Report generation components
│   ├── pages/              # Route components
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API calls and external services
│   ├── stores/             # Zustand state stores
│   ├── utils/              # Helper functions
│   ├── types/              # TypeScript type definitions
│   └── config/             # Configuration files
├── public/                 # Static assets
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

### 2.3 Key Features
- **Progressive Web App**: Service worker for offline capability
- **Responsive Design**: Mobile-first approach
- **Real-time Updates**: WebSocket connection for processing status
- **Chunked Uploads**: Large file upload with resume capability
- **Video Synchronization**: Multi-source timeline view

## 3. Backend Architecture (Flask)

### 3.1 Technology Stack
- **Framework**: Flask with Flask-RESTX for API documentation
- **Database ORM**: SQLAlchemy with Alembic migrations
- **Authentication**: Supabase Auth integration
- **Task Queue**: Celery with Redis broker
- **File Processing**: FFmpeg for video manipulation
- **API Documentation**: Swagger/OpenAPI via Flask-RESTX
- **Deployment**: Gunicorn WSGI server

### 3.2 Project Structure
```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration classes
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── case.py
│   │   ├── video.py
│   │   └── analysis.py
│   ├── routes/              # API route blueprints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── cases.py
│   │   ├── videos.py
│   │   └── analysis.py
│   ├── services/            # Business logic services
│   │   ├── __init__.py
│   │   ├── video_service.py
│   │   ├── analysis_service.py
│   │   ├── report_service.py
│   │   └── storage_service.py
│   ├── tasks/               # Celery tasks
│   │   ├── __init__.py
│   │   ├── video_processing.py
│   │   └── ai_analysis.py
│   ├── utils/               # Helper utilities
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   ├── decorators.py
│   │   └── exceptions.py
│   └── extensions.py        # Flask extensions initialization
├── migrations/              # Alembic database migrations
├── tests/                   # Unit and integration tests
├── requirements.txt         # Python dependencies
├── Dockerfile
└── run.py                   # Application entry point
```

### 3.3 API Design Principles
- **RESTful Architecture**: Standard HTTP methods and status codes
- **Consistent Response Format**: Standardized JSON response structure
- **Error Handling**: Comprehensive error responses with codes
- **Rate Limiting**: API throttling to prevent abuse
- **Versioning**: URL-based versioning (/api/v1/)

### 3.4 Key Services

#### Video Processing Service
- File format conversion and standardization
- Chunk creation for parallel processing
- Metadata extraction and validation
- Thumbnail generation

#### Analysis Service
- Coordination of AI model inference
- Result aggregation and confidence scoring
- Violation detection and classification
- Timeline reconstruction

#### Storage Service
- Secure file upload to Digital Ocean Spaces
- Presigned URL generation for direct upload
- File lifecycle management
- CDN integration for fast delivery

## 4. AI/ML Architecture

### 4.1 Model Pipeline
- **Video Analysis**: LLaVA-HF for visual understanding
- **Audio Transcription**: OpenAI Whisper for speech-to-text
- **NLP Processing**: Custom models for violation detection
- **Scene Detection**: Computer vision for scene boundaries

### 4.2 Processing Strategy
```
Input Video → Preprocessing → Parallel Analysis → Result Aggregation → Report Generation
     ↓              ↓              ↓                    ↓                    ↓
Format/Chunk   Frame Sampling   VLM + Whisper    Confidence Scoring   JSON + PDF
```

### 4.3 Optimization Techniques
- **Smart Sampling**: Adaptive frame selection based on scene complexity
- **Batch Processing**: Group similar operations for efficiency
- **Model Caching**: Keep frequently used models in memory
- **GPU Scheduling**: Optimal resource allocation across tasks

## 5. Database Architecture (Supabase/PostgreSQL)

### 5.1 Core Tables
```sql
-- Users and Authentication (managed by Supabase Auth)
users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Legal Cases
cases (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR DEFAULT 'active',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Video Files
videos (
    id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size BIGINT,
    duration FLOAT,
    format VARCHAR,
    status VARCHAR DEFAULT 'uploaded',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Analysis Results
analyses (
    id UUID PRIMARY KEY,
    video_id UUID REFERENCES videos(id),
    analysis_type VARCHAR NOT NULL,
    results JSONB,
    confidence_score FLOAT,
    status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Detected Violations
violations (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES analyses(id),
    violation_type VARCHAR NOT NULL,
    timestamp_start FLOAT,
    timestamp_end FLOAT,
    confidence FLOAT,
    description TEXT,
    severity VARCHAR,
    created_at TIMESTAMP
)
```

### 5.2 Indexing Strategy
- Composite indexes on frequently queried combinations
- Full-text search indexes on transcription data
- Time-based partitioning for large analysis tables

## 6. Security Architecture

### 6.1 Authentication & Authorization
- **Supabase Auth**: JWT-based authentication
- **Row Level Security**: Database-level access controls
- **API Key Authentication**: For service-to-service communication
- **Role-Based Access**: Attorney, paralegal, admin roles

### 6.2 Data Protection
- **Encryption at Rest**: Database and file storage encryption
- **Encryption in Transit**: TLS 1.3 for all communications
- **File Access Control**: Presigned URLs with expiration
- **Audit Logging**: Complete access and modification tracking

### 6.3 Privacy Measures
- **Data Minimization**: Only collect necessary information
- **Retention Policies**: Automated data cleanup
- **Geographic Restrictions**: Data residency compliance
- **Redaction Capabilities**: Automatic PII removal

## 7. Deployment Architecture

### 7.1 Infrastructure Overview
- **Frontend**: Netlify with global CDN
- **Backend**: Digital Ocean Droplets with load balancer
- **Database**: Supabase managed PostgreSQL
- **File Storage**: Digital Ocean Spaces
- **Compute**: Digital Ocean + external GPU services

### 7.2 Scaling Strategy
- **Horizontal Scaling**: Multiple backend instances
- **Database Scaling**: Read replicas and connection pooling
- **File Storage**: CDN for global distribution
- **AI Processing**: Elastic GPU compute via RunPod/Vast.ai

### 7.3 Monitoring & Observability
- **Application Monitoring**: Sentry for error tracking
- **Performance Monitoring**: New Relic or DataDog
- **Infrastructure Monitoring**: Digital Ocean monitoring
- **Log Aggregation**: Centralized logging with search

## 8. Development Workflow

### 8.1 Local Development
- **Docker Compose**: Complete local environment
- **Hot Reload**: Frontend and backend auto-reload
- **Database**: Local PostgreSQL or Supabase local
- **Mock Services**: AI model mocks for faster development

### 8.2 CI/CD Pipeline
- **Version Control**: Git with feature branch workflow
- **Testing**: Automated unit and integration tests
- **Code Quality**: ESLint, Prettier, Black, type checking
- **Deployment**: Automated deployment on merge to main

### 8.3 Environment Management
- **Development**: Local development environment
- **Staging**: Production-like testing environment
- **Production**: Live customer environment
- **Feature Flags**: Gradual feature rollout capability

## 9. Performance Considerations

### 9.1 Frontend Optimization
- **Code Splitting**: Lazy loading of route components
- **Asset Optimization**: Image compression and WebP format
- **Caching Strategy**: Browser caching with cache busting
- **Bundle Analysis**: Regular bundle size monitoring

### 9.2 Backend Optimization
- **Database Optimization**: Query optimization and indexing
- **Caching Layer**: Redis for frequently accessed data
- **Connection Pooling**: Efficient database connections
- **Async Processing**: Non-blocking operations where possible

### 9.3 Video Processing Optimization
- **Streaming Upload**: Direct-to-storage uploads
- **Parallel Processing**: Concurrent chunk processing
- **Smart Sampling**: Reduce processing without losing accuracy
- **Result Caching**: Avoid reprocessing identical content

## 10. Cost Management

### 10.1 Infrastructure Costs
- **Compute**: Estimated $200-500/month initially
- **Storage**: Pay-per-use file storage
- **Database**: Supabase Pro plan $25/month
- **CDN**: Minimal costs with Netlify/DO Spaces

### 10.2 AI Processing Costs
- **GPU Compute**: On-demand via RunPod ($0.50-2.00/hour)
- **Model Inference**: Batch processing for efficiency
- **Cost Per Analysis**: Target $5-15 per video hour

### 10.3 Scaling Economics
- **Revenue Growth**: Subscription and per-case pricing
- **Cost Optimization**: Economies of scale with usage
- **Margin Improvement**: Better AI efficiency over time

## 11. Risk Mitigation

### 11.1 Technical Risks
- **Single Point of Failure**: Redundancy in critical components
- **Data Loss**: Multiple backup strategies
- **Performance Degradation**: Monitoring and auto-scaling
- **Security Breaches**: Regular security audits

### 11.2 Business Continuity
- **Service Uptime**: 99.9% uptime SLA target
- **Data Recovery**: Point-in-time recovery capability
- **Incident Response**: Clear escalation procedures
- **Vendor Lock-in**: Multi-cloud strategy where feasible