# PWC Contract Analysis System

A comprehensive GenAI-powered contract analysis system built with FastAPI, Celery, and MongoDB. This system provides automated contract analysis, clause extraction, and health evaluation using OpenAI's GPT models.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI API   │    │ Celery Workers  │
│  (Streamlit)    │◄──►│                 │◄──►│                 │
│                 │    │  • Auth         │    │ • Analysis      │
│                 │    │  • Contracts    │    │ • Evaluation    │
│                 │    │  • GenAI        │    │ • Callbacks     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │    MongoDB      │    │      Redis      │
                       │                 │    │                 │
                       │ • Contracts     │    │ • Task Queue    │
                       │ • Users         │    │ • Results       │
                       │ • Logs          │    │                 │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Features

### Core Features
- **JWT Authentication** - Secure user registration and login
- **Contract Upload** - PDF contract upload with metadata
- **GenAI Analysis** - Automated clause extraction using OpenAI
- **Contract Evaluation** - Health assessment and approval logic
- **Client Management** - Organize contracts by clients
- **Async Processing** - Background task processing with Celery
- **API Logging** - Request tracking and monitoring
- **Metrics Dashboard** - System performance metrics

### API Endpoints

#### Authentication (No JWT Required)
- `POST /auth/register` - Create new user
- `POST /auth/login` - User login and token generation

#### GenAI Analysis (JWT Required)
- `POST /genai/analyze-contract` - Direct PDF analysis
- `POST /genai/evaluate-contract` - Contract health evaluation

#### Contract Management (JWT Required)
- `POST /contracts/` - Upload new contract
- `GET /contracts/` - List contracts with filtering
- `GET /contracts/{id}` - Get specific contract
- `POST /contracts/{id}/init-genai` - Trigger analysis pipeline

#### Client Management (JWT Required)
- `POST /clients/` - Create new client
- `GET /clients/{id}/contracts` - Get client's contracts

#### System Monitoring (JWT Required)
- `GET /logs` - Paginated logs with filters
- `GET /metrics` - System metrics
- `GET /healthz` - Health check
- `GET /readyz` - Readiness check

## 📁 Project Structure

```
src/python/
├── libs/pwc/                    # Shared library
│   ├── ai/                      # AI factory (OpenAI, future: HuggingFace)
│   ├── storage/                 # Storage factory (Local, future: S3)
│   ├── settings.py              # Configuration management
│   ├── logger.py                # Logging utilities
│   ├── task_interface.py        # Shared data models
│   └── api_interface.py         # API client for workers
├── projects/
│   ├── api/                     # FastAPI application
│   │   ├── api/
│   │   │   ├── core/           # Security, database, celery
│   │   │   ├── db/             # MongoDB models
│   │   │   ├── handlers/v1/    # API route handlers
│   │   │   └── main.py         # Application entry point
│   │   ├── Dockerfile
│   │   └── Makefile
│   ├── analyze_contracts/       # Celery worker
│   │   ├── analyze_contracts/
│   │   │   ├── tasks/          # Analysis and evaluation tasks
│   │   │   ├── core/           # Worker database connection
│   │   │   └── main.py         # Celery app configuration
│   │   ├── Dockerfile
│   │   └── Makefile
│   └── frontend/               # Streamlit frontend (future)
└── docker-compose.yml          # Complete system orchestration
```

## 🛠️ Setup Instructions

### Prerequisites
- Docker & Docker Compose
- OpenAI API key
- Make (for using Makefiles)

### Quick Start

1. **Clone and setup the project:**
   ```bash
   git clone <repository>
   cd PWC/task2
   make setup
   ```

2. **Configure environment:**
   ```bash
   # Edit .env file and add your OpenAI API key
   nano .env
   # Set OPENAI_API_KEY=your-actual-api-key
   ```

3. **Start the system:**
   ```bash
   make up
   ```

4. **Access the services:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - MongoDB Admin (Mongo Express): http://localhost:8081 (admin/admin123)
   - MongoDB: localhost:27017
   - Redis: localhost:6379

### Development Setup

1. **Install dependencies:**
   ```bash
   make install-dev
   ```

2. **Run services individually:**
   ```bash
   # Terminal 1: Start API
   make dev-api

   # Terminal 2: Start worker
   make dev-worker
   ```

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your-openai-api-key-here
SECRET_KEY=your-secret-key

# Database
MONGODB_URL=mongodb://admin:password123@localhost:27017/pwc_contracts?authSource=admin

# Storage (Factory Pattern)
STORAGE_TYPE=local  # local, s3 (future)
LOCAL_STORAGE_PATH=./storage

# AI Provider (Factory Pattern)
AI_PROVIDER=openai  # openai, huggingface (future)
OPENAI_MODEL=gpt-4
```

### Factory Patterns

The system uses factory patterns for extensibility:

**Storage Factory:**
- Current: Local filesystem storage
- Future: S3, Azure Blob, Google Cloud Storage

**AI Factory:**
- Current: OpenAI GPT models
- Future: HuggingFace, Anthropic Claude, local models

## 📊 Monitoring

### System Metrics
Access metrics at `/metrics` endpoint:
- Request count and latency
- Contract processing statistics
- Error rates

### Logging
Structured logs available at `/logs` endpoint with filtering:
- User activity
- API endpoint usage
- Error tracking

### Health Checks
- `/healthz` - Liveness probe
- `/readyz` - Readiness probe with dependency checks

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific tests
make test-api
make test-worker
```

## 🐳 Docker Commands

```bash
# Build and start
make build
make up

# View logs
make logs
make logs-api
make logs-worker

# Stop and cleanup
make down
make clean
```

## 🔍 Contract Analysis Workflow

1. **Upload Contract** - User uploads PDF via API
2. **Trigger Analysis** - Call `/contracts/{id}/init-genai`
3. **Extract Clauses** - Celery worker uses OpenAI to analyze PDF
4. **Evaluate Health** - Second task evaluates contract approval
5. **Callback Notification** - Optional webhook notification
6. **Results Available** - Access via `/contracts/{id}`

## 🚧 Future Enhancements

- **Frontend**: Streamlit dashboard for contract management
- **Storage**: S3 and cloud storage support
- **AI Providers**: HuggingFace and local model support
- **Advanced Analytics**: Contract comparison and trend analysis
- **Kubernetes**: Helm charts for production deployment

## 📝 License

This project is part of the PWC assessment and is for evaluation purposes only.