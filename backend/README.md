# AI Health Tracker Backend

**🚀 Intelligent healthcare analysis platform with AI-powered medical insights, multilingual OCR processing, and automated specialist appointment booking.**

## 📋 Project Description

AI Health Tracker is a comprehensive backend API that provides:
- **🔍 Advanced OCR Processing**: Extract health metrics from medical documents (Russian, English, Kazakh)
- **🤖 Intelligent Health Agent**: AI-powered analysis with automatic specialist recommendations and appointment booking
- **🌍 Full Localization**: Complete Russian and English language support
- **👨‍⚕️ Doctor Recommendations**: Smart specialist matching based on health metrics
- **🔬 Disease Risk Prediction**: AI-powered disease risk assessment
- **📅 Appointment Management**: Automated booking system for critical health cases
- **💬 Secure Communication**: HIPAA-compliant patient-doctor messaging
- **📊 Comprehensive Analytics**: Health trend analysis and user statistics

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.8+** - Programming language
- **Uvicorn** - ASGI server for production deployment

### Database & ORM
- **SQLAlchemy** - SQL toolkit and Object-Relational Mapping
- **SQLite** - Lightweight database (development)
- **PostgreSQL** - Production database (optional)

### AI & Machine Learning
- **Groq API** - Advanced language model integration
- **OpenRouter API** - Enhanced AI analysis capabilities
- **Custom ML Models** - Disease risk prediction algorithms

### OCR & Document Processing
- **EasyOCR** - Multi-language OCR processing
- **PyMuPDF** - PDF document processing
- **Pillow (PIL)** - Image processing and manipulation
- **OpenCV** - Computer vision for document analysis

### Security & Authentication
- **JWT (JSON Web Tokens)** - Secure authentication
- **bcrypt** - Password hashing
- **python-multipart** - File upload handling

### Additional Libraries
- **Pydantic** - Data validation and settings management
- **python-dotenv** - Environment variable management
- **aiofiles** - Asynchronous file operations
- **requests** - HTTP client library

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd ai-health-backend/backend
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DATABASE_URL=sqlite:///./health_tracker.db
# For PostgreSQL: postgresql://username:password@localhost/dbname

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services API Keys
GROQ_API_KEY=your-groq-api-key-here
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Email Configuration (Optional)
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# File Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB in bytes
UPLOAD_DIR=uploads

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 5. Initialize Database
```bash
# The database will be automatically created when you first run the application
python -c "from app.database import create_tables; create_tables()"
```

### 6. Run the Application

#### Development Mode
```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Or using Python module
python -m app.main
```

#### Production Mode
```bash
# Using Gunicorn (install separately: pip install gunicorn)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# Or using uvicorn for production
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

## 📋 Environment Variables

### Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` |
| `GROQ_API_KEY` | Groq API key for AI processing | `gsk_xxx...` |

### Optional Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./health_tracker.db` | Database connection string |
| `OPENROUTER_API_KEY` | None | Enhanced AI analysis (optional) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | JWT token expiration |
| `MAX_FILE_SIZE` | 10485760 | Maximum upload file size (bytes) |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins |

### Email Configuration (Optional)
| Variable | Description |
|----------|-------------|
| `SMTP_USERNAME` | Email username |
| `SMTP_PASSWORD` | Email password/app password |
| `FROM_EMAIL` | Sender email address |
| `SMTP_SERVER` | SMTP server (e.g., smtp.gmail.com) |
| `SMTP_PORT` | SMTP port (e.g., 587) |

## 🧪 Running Tests

### Unit Tests
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest test_authentication_system.py

# Run with coverage
python -m pytest --cov=app
```

### API Testing
```bash
# Test comprehensive API functionality
python test_comprehensive_api.py

# Test Russian localization
python test_russian_localization.py

# Test specific OCR functionality
python test_groq_api_migration.py
```

### Manual Testing Scripts
```bash
# Create test health analysis
python create_test_analysis.py

# Test authentication system
python test_authentication_system.py

# Test chat functionality
python test_chat_system.py
```

## 📚 API Documentation

### Interactive Documentation
Once the server is running, visit:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

### Comprehensive Documentation
See `API_ENDPOINTS_DOCUMENTATION.md` for detailed endpoint documentation including:
- All available endpoints
- Request/response formats
- Authentication requirements
- Language support details
- Example requests and responses

## 🌐 Server Configuration

### Default Configuration
- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `8001`
- **URL**: `http://localhost:8001`

### Health Checks
- **Root**: `GET /` - Basic server status
- **Health**: `GET /health` - Detailed health check

### CORS Configuration
The API supports Cross-Origin Resource Sharing (CORS) for frontend integration.

## 🔧 Development

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   ├── routers/             # API route handlers
│   └── services/            # Business logic services
├── uploads/                 # File upload directory
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

### Adding New Features
1. **Models**: Add database models in `app/models.py`
2. **Schemas**: Define Pydantic schemas in `app/schemas.py`
3. **Services**: Implement business logic in `app/services/`
4. **Routes**: Add API endpoints in `app/routers/`
5. **Tests**: Create tests for new functionality

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for better code documentation
- Add docstrings to functions and classes
- Keep functions focused and modular

## 🚀 Deployment

### Docker Deployment (Recommended)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Cloud Deployment
- **Heroku**: Use `Procfile` with gunicorn
- **AWS EC2**: Use systemd service with gunicorn
- **Google Cloud Run**: Use Docker container
- **Azure Container Instances**: Deploy with container

### Production Considerations
- Use PostgreSQL for production database
- Set up proper logging and monitoring
- Configure SSL/TLS certificates
- Set up backup strategies for uploaded files
- Use environment-specific configuration files

## 🔐 Security

### Authentication
- JWT tokens with configurable expiration
- Secure password hashing with bcrypt
- Role-based access control (patients/doctors)

### Data Protection
- User data isolation (users only access their own data)
- Secure file upload with validation
- HIPAA-compliant communication features
- Input validation and sanitization

### Best Practices
- Never commit API keys or secrets to version control
- Use strong, unique SECRET_KEY in production
- Regularly update dependencies for security patches
- Implement rate limiting for production deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues
- **Import Errors**: Ensure virtual environment is activated and dependencies are installed
- **Database Errors**: Check DATABASE_URL in .env file
- **API Key Errors**: Verify GROQ_API_KEY is set correctly
- **File Upload Issues**: Check upload directory permissions

### Getting Help
- Check the API documentation at `/docs`
- Review the comprehensive endpoint documentation
- Create an issue in the repository for bugs or feature requests

## 🔄 Version History

### Latest Updates
- ✅ Intelligent Health Agent with Russian localization
- ✅ Automated appointment booking for critical cases
- ✅ Enhanced Kazakh OCR support with 100% success rate
- ✅ Disease risk prediction with AI analysis
- ✅ Comprehensive patient-doctor communication system
- ✅ Multi-language support (Russian, English, Kazakh)

---

**Built with ❤️ for better healthcare accessibility and intelligent medical analysis.** 