# Video Evidence Analyzer

A comprehensive SaaS platform for civil rights attorneys to analyze video evidence using AI-powered tools. This platform helps legal professionals efficiently process bodycam footage, security recordings, and mobile video evidence to identify potential civil rights violations and generate detailed legal reports.

## 🚀 Features

### Core Functionality
- **Video Upload & Management**: Secure upload and organization of video evidence
- **AI-Powered Analysis**: Automated transcription, object detection, and violation identification
- **Case Management**: Organize evidence by legal cases with metadata and tags
- **Legal Report Generation**: Automated generation of professional legal reports
- **User Authentication**: Secure multi-user access with role-based permissions

### AI Capabilities
- **Audio Transcription**: Powered by OpenAI Whisper for accurate speech-to-text
- **Visual Analysis**: LLaVA-HF for comprehensive video content analysis
- **Violation Detection**: Custom NLP models trained for civil rights violation patterns
- **Sentiment Analysis**: Emotional context analysis of interactions
- **Object Detection**: Identification of weapons, vehicles, and other relevant objects

### Technical Features
- **Real-time Processing**: Async video processing with progress tracking
- **Scalable Architecture**: Microservices design with Docker containerization
- **Cloud Storage**: Digital Ocean Spaces for secure file storage
- **Database**: PostgreSQL with Supabase for authentication and data management
- **Modern UI**: React 18 + TypeScript + Tailwind CSS

## 🏗️ Architecture

```
video-evidence-analyzer/
├── frontend/                 # React + Vite + TypeScript
├── backend/                  # Flask + SQLAlchemy + Celery
├── ai-models/               # AI/ML processing modules
├── infrastructure/          # Deployment configurations
├── docs/                    # Documentation and diagrams
└── docker-compose.yml       # Local development setup
```

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Zustand** for state management
- **React Query** for API state management
- **React Router** for navigation
- **React Hook Form** for form handling

### Backend
- **Flask** with Python 3.11
- **SQLAlchemy** for database ORM
- **Celery** for async task processing
- **Redis** for caching and message queuing
- **JWT** for authentication
- **Marshmallow** for serialization

### AI/ML
- **Whisper** for audio transcription
- **LLaVA-HF** for visual analysis
- **Transformers** for NLP processing
- **OpenCV** for video processing
- **PyTorch** for model inference

### Infrastructure
- **Docker** for containerization
- **PostgreSQL** for database
- **Digital Ocean Spaces** for file storage
- **Supabase** for authentication
- **Netlify** for frontend deployment
- **Digital Ocean** for backend deployment

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+
- Python 3.11+
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/video-evidence-analyzer.git
cd video-evidence-analyzer
```

2. **Set up environment variables**
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration

# Frontend
cp frontend/.env.example frontend/.env.local
# Edit frontend/.env.local with your configuration
```

3. **Start the development environment**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/api/docs

### Manual Setup (Alternative)

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
flask run
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📖 Documentation

- [API Documentation](docs/api-spec.md)
- [Architecture Guide](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Product Requirements](docs/prd.md)

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# AI Models
HUGGINGFACE_API_KEY=your-hf-api-key
OPENAI_API_KEY=your-openai-key

# Storage
DO_SPACES_KEY=your-spaces-key
DO_SPACES_SECRET=your-spaces-secret
DO_SPACES_BUCKET=your-bucket-name
```

#### Frontend (.env.local)
```bash
VITE_API_URL=http://localhost:5000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

## 🚀 Deployment

### Production Deployment

#### Option 1: Digital Ocean App Platform
```bash
doctl apps create --spec infrastructure/digital-ocean/app.yaml
```

#### Option 2: Docker Compose on VPS
```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### Option 3: Netlify + Digital Ocean
- Frontend: Deploy to Netlify using `infrastructure/netlify/netlify.toml`
- Backend: Deploy to Digital Ocean using App Platform

See [Deployment Guide](docs/deployment.md) for detailed instructions.

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:ui
```

## 📊 Monitoring

- **Application Monitoring**: Sentry integration for error tracking
- **Performance Monitoring**: Built-in metrics and logging
- **Health Checks**: `/api/health` endpoint for service monitoring

## 🔒 Security

- JWT-based authentication
- Row-level security with Supabase
- File upload validation and scanning
- Rate limiting on API endpoints
- HTTPS enforcement in production
- Environment variable encryption

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript strict mode for frontend
- Use PEP 8 for Python code
- Write tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## 🗺️ Roadmap

### Phase 1 (Current)
- [x] Basic video upload and storage
- [x] User authentication and case management
- [x] AI transcription integration
- [ ] Basic violation detection

### Phase 2
- [ ] Advanced AI analysis features
- [ ] Real-time collaboration tools
- [ ] Mobile app development
- [ ] Advanced reporting features

### Phase 3
- [ ] Machine learning model training interface
- [ ] Integration with legal case management systems
- [ ] Advanced analytics and insights
- [ ] Multi-language support

## 🙏 Acknowledgments

- OpenAI for Whisper transcription models
- Hugging Face for LLaVA and transformer models
- The open-source community for various tools and libraries
- Civil rights attorneys who provided domain expertise

---

**Built with ❤️ for civil rights attorneys and justice advocates**
