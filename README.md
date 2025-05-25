# 🏥 AI Health Tracker - Backend API

## 📋 **Overview**

This is the backend API for the AI Health Tracker application, providing comprehensive healthcare data processing, AI-powered analysis, and intelligent agent capabilities.

## 🚀 **Features**

### **Core API Endpoints**
- **Authentication**: User registration, login, JWT token management
- **File Upload & OCR**: Medical document processing with text extraction
- **Health Analysis**: AI-powered health metric analysis and recommendations
- **Chat System**: Real-time messaging between patients and doctors
- **Appointment Management**: Scheduling and management system
- **Intelligent Agent**: AI agent for critical value detection and recommendations

### **AI & Machine Learning**
- **OCR Processing**: Extract text from medical documents (PDF, images)
- **Health Metric Analysis**: Parse and analyze lab results
- **Critical Value Detection**: Automatic detection of dangerous health values
- **Specialist Recommendations**: AI-powered specialist matching
- **Multilingual Support**: Supports Kazakh, Russian, and English medical texts

### **Real-time Features**
- **WebSocket Support**: Real-time chat and notifications
- **Live Updates**: Instant updates for appointments and messages
- **Critical Alerts**: Immediate notifications for critical health values

## 🛠 **Technology Stack**

- **Framework**: FastAPI 0.110.0
- **Database**: SQLAlchemy 2.0.36 with SQLite/PostgreSQL
- **Authentication**: JWT with passlib and bcrypt
- **AI/ML**: Groq API, scikit-learn, pandas, numpy
- **OCR**: EasyOCR, OpenCV, PyMuPDF, Pillow
- **Real-time**: WebSockets, asyncio
- **Deployment**: Uvicorn, Gunicorn

## 📁 **Project Structure**

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database configuration
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── health_analysis.py
│   │   ├── chat.py
│   │   └── appointment.py
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── upload.py           # File upload and OCR
│   │   ├── health.py           # Health analysis endpoints
│   │   ├── chat.py             # Chat system endpoints
│   │   ├── appointments.py     # Appointment management
│   │   └── agent.py            # AI agent endpoints
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── ocr_service.py
│   │   ├── health_service.py
│   │   ├── chat_service.py
│   │   └── agent_service.py
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   └── helpers.py
│   └── websocket.py            # WebSocket handlers
├── uploads/                    # File upload directory
├── database.db                 # SQLite database (development)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── README.md                   # This file
```

## 🔧 **Installation & Setup**

### **Prerequisites**
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### **1. Clone Repository**
```bash
git clone https://github.com/Amirchiiik/HealthAiTracker.git -b backend-only
cd HealthAiTracker
```

### **2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Environment Configuration**
Create a `.env` file in the root directory:
```bash
# Database
DATABASE_URL=sqlite:///./database.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
GROQ_API_KEY=your-groq-api-key

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### **5. Initialize Database**
```bash
python -c "from app.database import create_tables; create_tables()"
```

### **6. Run Development Server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## 📚 **API Documentation**

### **Interactive Documentation**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### **Key Endpoints**

#### **Authentication**
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

#### **File Upload & Analysis**
- `POST /upload/file` - Upload medical document
- `GET /upload/ocr/{filename}` - Get OCR analysis results
- `POST /upload/text-analysis` - Analyze text directly

#### **Health Management**
- `GET /health/analyses` - Get user's health analyses
- `GET /health/metrics` - Get health metrics
- `POST /health/analysis/{id}/summary` - Generate analysis summary

#### **Chat System**
- `GET /chat/conversations` - Get user conversations
- `GET /chat/history/{user_id}` - Get chat history
- `POST /chat/send` - Send message
- `PUT /chat/read/{message_id}` - Mark message as read

#### **Appointments**
- `GET /appointments` - Get appointments
- `POST /appointments` - Create appointment
- `PUT /appointments/{id}` - Update appointment
- `DELETE /appointments/{id}` - Cancel appointment

#### **AI Agent**
- `POST /agent/analyze-and-act` - Trigger AI agent analysis
- `GET /agent/notifications` - Get agent notifications
- `GET /agent/thresholds` - Get critical value thresholds

#### **WebSocket**
- `WS /ws/{user_id}` - WebSocket connection for real-time updates

## 🔒 **Security Features**

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **CORS Protection**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic models for request validation
- **File Upload Security**: File type and size validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## 🧪 **Testing**

### **Run Tests**
```bash
pytest
```

### **Run with Coverage**
```bash
pytest --cov=app tests/
```

### **Test Categories**
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **WebSocket Tests**: Real-time functionality testing

## 🚀 **Deployment**

### **Production Server**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### **Docker Deployment**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Environment Variables for Production**
```bash
DATABASE_URL=postgresql://user:password@localhost/healthtracker
SECRET_KEY=production-secret-key
GROQ_API_KEY=production-groq-key
ALLOWED_ORIGINS=https://yourdomain.com
```

## 📊 **Performance & Monitoring**

### **Health Check**
- `GET /health` - API health status

### **Metrics**
- Request/response times
- Database query performance
- File upload success rates
- AI analysis accuracy

## 🔧 **Development**

### **Code Style**
- **Formatter**: Black
- **Linter**: Flake8
- **Type Checking**: mypy

### **Pre-commit Hooks**
```bash
pip install pre-commit
pre-commit install
```

## 📞 **Support**

### **Common Issues**
1. **Database Connection**: Check DATABASE_URL in .env
2. **File Upload Errors**: Verify UPLOAD_DIR permissions
3. **AI Analysis Failures**: Check GROQ_API_KEY configuration
4. **WebSocket Issues**: Ensure proper CORS configuration

### **Logs**
Application logs are available in the console output. For production, configure proper logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License.

---

## 🎯 **API Status: Production Ready**

✅ **Authentication System**: Complete with JWT  
✅ **File Upload & OCR**: Multi-format support  
✅ **Health Analysis**: AI-powered insights  
✅ **Chat System**: Real-time messaging  
✅ **Appointment Management**: Full CRUD operations  
✅ **AI Agent**: Critical value detection  
✅ **WebSocket Support**: Real-time updates  
✅ **Security**: Production-grade security measures  
✅ **Documentation**: Comprehensive API docs  
✅ **Testing**: Unit and integration tests  

**Ready for production deployment!**

*Last updated: January 25, 2025* 