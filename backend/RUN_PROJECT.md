# How to Run the AI Health Tracker

## 🚀 Quick Start (Automated Setup)

**Option 1: Use the automated setup script**
```bash
./setup_project.sh
```

This script will:
- ✅ Check your environment 
- ✅ Install dependencies
- ✅ Guide you through Groq API setup
- ✅ Initialize the database
- ✅ Handle port conflicts automatically
- ✅ Start the server

## 🔧 Manual Setup (Step by Step)

### Prerequisites
- Python 3.8+ installed
- Virtual environment activated
- Groq API account

### Step 1: Environment Setup
```bash
# Ensure you're in the project directory
cd /Users/toktarov112a/Desktop/project_2/AIHealthTracker/ai-health-backend

# Activate virtual environment (if not already active)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Groq API Configuration
1. **Get your Groq API key:**
   - Visit [Groq Console](https://console.groq.com/)
   - Sign up or log in
   - Navigate to API Keys section
   - Create a new API key
   - Copy the key (starts with `gsk_...`)

2. **Set the environment variable:**
```bash
# For current session
export GROQ_API_KEY="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"

# To make permanent, add to your shell profile:
echo 'export GROQ_API_KEY="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"' >> ~/.zshrc
```

### Step 3: Database Initialization
```bash
# Initialize database tables
python -c "from app.database import engine, Base; from app.models import User, HealthAnalysis, ChatInteraction; Base.metadata.create_all(bind=engine)"
```

### Step 4: Start the Server
```bash
# Check if port 8000 is available
lsof -ti:8000

# If port is free, start normally:
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# If port is busy, use alternative port:
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

## 📚 After Startup

Once the server is running, you can access:

### API Documentation
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Register a User
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "role": "patient"
  }'
```

### Login
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

## 🧪 Testing

### Run Test Suites
```bash
# Test Groq API integration
python test_groq_api_migration.py

# Test authentication system
python test_authentication_system.py
```

### Manual API Testing
```bash
# Get your token from login response, then:
TOKEN="your_jwt_token_here"

# Test health metric explanation
curl -X POST "http://127.0.0.1:8000/explain/metrics" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Гемоглобин: 140 г/л (норма: 120-160)\nГлюкоза: 110 мг/дл (норма: 70-99)"
  }'
```

## 🔧 Troubleshooting

### Common Issues

**1. Port Already in Use**
- Error: `[Errno 48] Address already in use`
- Solution: Use a different port or kill existing process
```bash
# Find what's using the port
lsof -ti:8000
# Kill the process (replace PID)
kill -9 PID
```

**2. Groq API Key Missing**
- Error: `GROQ_API_KEY environment variable not set`
- Solution: Set the environment variable as shown in Step 2

**3. bcrypt Warnings**
- Warning: `AttributeError: module 'bcrypt' has no attribute '__about__'`
- This is just a warning and doesn't affect functionality
- Optional fix: `pip install --upgrade bcrypt`

**4. Database Issues**
- Error: Table doesn't exist
- Solution: Run database initialization again (Step 3)

**5. Import Errors**
- Error: `ModuleNotFoundError`
- Solution: Ensure virtual environment is active and dependencies installed

### Performance Notes
- The bcrypt warnings are cosmetic and don't affect security
- "Using CPU" message for sentence transformers is normal
- Individual explanations may take 2-3 seconds per metric

## 🌟 Features Available

✅ **Authentication System**
- User registration and login
- JWT token authentication
- Role-based access (patient/doctor)
- Password security requirements

✅ **Health Analysis**
- OCR processing of medical documents
- Individual metric explanations using Groq AI
- Personal health history tracking
- Comprehensive health summaries

✅ **Data Management**
- User-specific file storage
- Chat history with AI
- Analysis history and statistics
- Secure data isolation

✅ **AI Integration**
- Groq API with Meta-Llama model
- Intelligent fallback responses
- Caching for performance
- Medical-specific prompts

The system is now production-ready with comprehensive authentication, AI-powered health analysis, and secure data management! 