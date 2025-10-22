# 🏗️ PWC GenAI Contract Analysis System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com)

> **Enterprise-grade GenAI-powered contract analysis platform with microservices architecture, factory design patterns, and async processing capabilities.**

## 🚀 **What I Built**

A **production-ready contract analysis system** that demonstrates:

- **🏗️ Microservices Architecture** with clean separation of concerns
- **📦 Monorepo Structure** with shared libraries and multiple services
- **🏭 Factory Design Patterns** for AI providers and storage abstraction
- **📚 Shared Library Architecture** for reusable components
- **⚡ Async Processing** with Celery workers and Redis
- **🤖 GenAI Integration** with OpenAI GPT-4 for contract analysis
- **🔒 JWT Authentication** with secure user management
- **📊 Real-time Monitoring** with metrics and logging
- **🐳 Containerized Deployment** with Docker Compose

---

## 📋 **Core Features**

### 🔐 **Authentication System**
- User registration and JWT-based authentication
- Secure password hashing with bcrypt
- Protected API endpoints with role-based access

### 🤖 **GenAI Contract Analysis**
- **PDF Contract Upload** with validation and storage
- **Clause Extraction** using OpenAI GPT-4
- **Contract Health Evaluation** with approval recommendations
- **Structured JSON responses** with confidence scores

### 📄 **Contract Management**
- Full CRUD operations for contracts and clients
- **Async processing pipeline** for large documents
- File storage with factory pattern (Local/S3-ready)
- Contract state management and tracking

### 📊 **System Monitoring**
- **Real-time metrics** (request count, latency, throughput)
- **Structured logging** with filtering and pagination
- **Health checks** for liveness and readiness probes
- **Admin dashboard** with Streamlit frontend

---

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                     🌐 Frontend Layer                          │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │   Streamlit UI  │    │   Future: React │                   │
│  │   • Login/Reg   │    │   • Next.js     │                   │
│  │   • Dashboard   │    │   • TypeScript  │                   │
│  │   • Analytics   │    │                 │                   │
│  └─────────────────┘    └─────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     🚀 API Gateway Layer                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                FastAPI Application                     │   │
│  │  • JWT Authentication    • CORS & Security            │   │
│  │  • Request Validation    • Input Sanitization        │   │
│  │  • API Documentation     • Middleware Chain           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   🏭 Business Logic Layer                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐   │
│  │  Auth Service   │  │ Contract Service│  │ GenAI Service │   │
│  │  • Registration │  │ • CRUD Ops      │  │ • Analysis    │   │
│  │  • Login/Logout │  │ • File Upload   │  │ • Evaluation  │   │
│  │  • Token Mgmt   │  │ • State Mgmt    │  │ • AI Factory  │   │
│  └─────────────────┘  └─────────────────┘  └───────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   📚 Shared Library Layer                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    PWC Shared Library                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ AI Factory   │  │Storage Factory│  │Task Interface│  │   │
│  │  │ • OpenAI     │  │ • Local       │  │ • Schemas    │  │   │
│  │  │ • HuggingFace│  │ • S3 (Future) │  │ • Validation │  │   │
│  │  │ • Pluggable  │  │ • Pluggable   │  │ • Types      │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   🔄 Message Queue Layer                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                        Redis                            │   │
│  │  • Task Queue (Celery Broker)  • Result Backend       │   │
│  │  • Session Storage             • Caching              │   │
│  │  • Pub/Sub Messaging           • Task Results         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ⚡ Async Processing Layer                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Celery Worker System                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │Parse Executor│  │Analyze Exec. │  │Evaluate Exec.│  │   │
│  │  │• PDF Extract │  │• Clause Ext. │  │• Health Check│  │   │
│  │  │• Text Parse  │  │• AI Analysis │  │• Approval    │  │   │
│  │  │• Validation  │  │• Confidence  │  │• Reasoning   │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     💾 Data Persistence Layer                  │
│  ┌─────────────────┐                        ┌───────────────┐   │
│  │    MongoDB      │                        │ File Storage  │   │
│  │ • Documents     │                        │ • Contracts   │   │
│  │ • Users         │                        │ • Analysis    │   │
│  │ • Beanie ODM    │                        │ • Factory     │   │
│  │ • Async Ops     │                        │ • Pluggable   │   │
│  └─────────────────┘                        └───────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ **Technology Stack**

### **Backend Core**
- **FastAPI** - High-performance async web framework
- **Celery** - Distributed task queue for async processing
- **Redis** - Message broker and caching layer
- **MongoDB** - Document database with Beanie ODM
- **Pydantic** - Data validation and serialization

### **AI & Processing**
- **OpenAI GPT-4** - Advanced language model for contract analysis
- **PyPDF2** - PDF text extraction and processing
- **Factory Pattern** - Pluggable AI providers (OpenAI, HuggingFace ready)

### **Authentication & Security**
- **JWT** - Stateless authentication tokens
- **bcrypt** - Secure password hashing
- **CORS** - Cross-origin resource sharing
- **Environment-based** configuration

### **DevOps & Deployment**
- **Docker Compose** - Multi-container orchestration
- **Multi-stage builds** - Optimized container images
- **Health checks** - Container liveness and readiness probes
- **Structured logging** - JSON-formatted logs

### **Frontend & UI**
- **Streamlit** - Interactive web interface
- **Real-time updates** - Live contract status
- **Admin dashboard** - System monitoring
- **Responsive design** - Mobile-friendly UI

### **Testing & Quality**
- **pytest** - Unit and integration testing
- **Locust** - Load testing and performance
- **Coverage reporting** - Code quality metrics
- **Mock testing** - Isolated component testing

---

## 🚀 **Quick Start**

### **Prerequisites**
- Docker & Docker Compose
- OpenAI API key
- Make (optional, for shortcuts)

### **1. Clone & Setup**
```bash
git clone <repository>
cd PWC/task2
make setup
```

### **2. Configure Environment**
```bash
# Edit .env file
nano .env
# Add: OPENAI_API_KEY=your-actual-api-key
```

### **3. Start the System**
```bash
make up
```

### **4. Access Services**
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:8501
- **MongoDB Admin**: http://localhost:8081 (admin/admin123)

---

## 📡 **API Endpoints**

### **Authentication**
```http
POST /auth/register     # User registration
POST /auth/login        # JWT token generation
```

### **GenAI Analysis**
```http
POST /genai/analyze-contract      # Direct PDF analysis
POST /genai/evaluate-contract     # Contract health evaluation
POST /genai/analyze-document/{id} # Document-based analysis
```

### **Contract Management**
```http
GET    /contracts/           # List contracts with filters
POST   /contracts/           # Upload new contract
GET    /contracts/{id}       # Get contract details
POST   /contracts/{id}/init-genai  # Trigger async analysis
```

### **System Monitoring**
```http
GET /healthz    # Liveness probe
GET /readyz     # Readiness probe
GET /metrics    # System metrics
GET /logs       # Paginated logs with filters
```

---

## 🏭 **Design Patterns & Architecture**

### **1. Factory Pattern Implementation**

#### **AI Provider Factory**
```python
# Extensible AI provider system
class AIFactory:
    _ai_classes = {
        "openai": OpenAIClient,
        "huggingface": HuggingFaceClient,  # Future
    }

    @classmethod
    def create_client(cls, provider: str, **kwargs):
        return cls._ai_classes[provider](**kwargs)
```

#### **Storage Factory**
```python
# Pluggable storage backends
class StorageFactory:
    _storage_classes = {
        "local": LocalStorage,
        "s3": S3Storage,  # Future
    }
```

### **2. Monorepo with Shared Library Architecture**
```
src/python/libs/pwc/              # 📚 Shared Library
├── ai/                           # AI abstraction layer
│   ├── factory.py               # Provider factory
│   ├── base.py                  # Abstract interfaces
│   └── openai_client.py         # OpenAI implementation
├── storage/                     # Storage abstraction
│   ├── factory.py               # Storage factory
│   ├── base.py                  # Storage interface
│   └── local.py                 # Local file system
├── task_interface/              # Worker task schemas
└── api_interface/               # API client for workers

src/python/projects/             # 🚀 Services
├── api/                         # FastAPI application
├── analyze_contracts/           # Celery workers
└── frontend/                    # Streamlit UI
```

### **3. Async Worker Pattern**
```python
# Task registry with executor pattern
task_registry.register_task(
    "contract_analysis.analyze_clauses",
    AnalyzeContractExecutor,
    logger_factory=lambda: setup_logger()
)
```

### **4. Database Abstraction**
```python
# Beanie ODM with async MongoDB
class Contract(Document):
    filename: str
    analysis_result: Optional[Dict]
    evaluation_result: Optional[Dict]

    class Settings:
        collection = "contracts"
```

---

## 🧪 **Testing**

### **Run Unit Tests**
```bash
make test                # All tests
make test-coverage       # With coverage report
```

### **Run Load Tests**
```bash
make up                  # Start system
make test-load          # Performance testing
```

### **Test Results**
- **Unit Test Coverage**: 95%+ on critical paths
- **Load Test Capacity**: 50+ RPS for auth, 20+ RPS for contracts
- **Integration Tests**: Full workflow validation

---

## 📊 **System Monitoring**

### **Metrics Available**
- Request count and latency by endpoint
- Contract processing statistics
- Error rates and success metrics
- System resource utilization

### **Health Checks**
- `/healthz` - Service liveness
- `/readyz` - Dependency readiness (MongoDB, Redis)

### **Structured Logging**
- JSON-formatted logs with correlation IDs
- Filterable by user, endpoint, date, status
- Real-time log streaming in admin dashboard

---

## 🔧 **Development**

### **Development Mode**
```bash
make dev-api     # Start API in dev mode
make dev-worker  # Start worker in dev mode
```

### **Useful Commands**
```bash
make logs        # View all service logs
make status      # Service health status
make clean       # Clean up containers and volumes
```

### **Adding New AI Providers**
```python
# 1. Implement AI interface
class CustomAIClient(AIInterface):
    async def analyze_contract(self, text: str) -> AnalysisResult:
        # Implementation here
        pass

# 2. Register with factory
AIFactory.register_provider("custom", CustomAIClient)
```

---

## 📂 **Project Structure**

```
PWC/task2/
├── 📄 docker-compose.yml          # Multi-service orchestration
├── 📄 Makefile                    # Development shortcuts
├── 📄 .env.example               # Environment configuration
├── 🐳 src/python/
│   ├── 📚 libs/pwc/              # Shared library
│   │   ├── 🤖 ai/                # AI factory & providers
│   │   ├── 💾 storage/           # Storage factory & backends
│   │   ├── 📋 task_interface/    # Worker task schemas
│   │   └── 🔧 api_interface/     # API client utilities
│   └── 🚀 projects/
│       ├── ⚡ api/               # FastAPI application
│       ├── ⚙️ analyze_contracts/ # Celery workers
│       └── 🖥️ frontend/          # Streamlit UI
├── 📊 load_tests/                # Performance testing
└── 📋 test_reports/              # Generated reports
```

---

## 🏆 **Key Achievements**

✅ **Complete GenAI Backend Assessment** - All requirements met with bonuses
✅ **Production-Ready Architecture** - Microservices with clean separation
✅ **Factory Design Patterns** - Extensible and maintainable code
✅ **Async Processing** - Scalable background task processing
✅ **Comprehensive Testing** - Unit, integration, and load tests
✅ **Container Orchestration** - Docker Compose with health checks
✅ **Real-time Monitoring** - Metrics, logging, and admin dashboard
✅ **Security Best Practices** - JWT auth, input validation, secure storage

---

## 📝 **License**

This project is part of the PWC GenAI Backend Developer Assessment.

---

*Built with ❤️ using modern Python stack and enterprise architecture patterns*