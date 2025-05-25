# AI Health Tracker - Development Setup Guide

## 🚀 **Quick Start - Run Both Backend + Frontend**

This guide shows you how to run the complete AI Health Tracker application with both backend and frontend services.

---

## 📋 **Prerequisites**

### **System Requirements**
- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **npm or yarn** (for frontend package management)
- **Git** (for version control)

### **Check Your Setup**
```bash
# Check Python version
python --version  # Should be 3.8+

# Check Node.js version
node --version    # Should be 16+

# Check npm version
npm --version
```

---

## ⚙️ **Environment Setup**

### **1. Clone and Navigate**
```bash
# If not already cloned
git clone <your-repo-url>
cd ai-health-backend
```

### **2. Backend Environment Variables**
Create a `.env` file in the project root:

```bash
# Create .env file
touch .env
```

Add the following content to `.env`:
```env
# Database Configuration
DATABASE_URL=sqlite:///./app.db

# Authentication
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI/OCR Services
GROQ_API_KEY=your-groq-api-key-here

# CORS Settings (for development)
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# File Upload Settings
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=10485760  # 10MB

# Logging
LOG_LEVEL=INFO
```

### **3. Frontend Environment Variables**
Create `.env` file in the `frontend` directory:

```bash
# Navigate to frontend and create .env
cd frontend
touch .env
```

Add the following content to `frontend/.env`:
```env
# Backend API URL
REACT_APP_API_URL=http://localhost:8000

# Other settings
REACT_APP_VERSION=1.0.0
```

---

## 🔧 **Backend Setup**

### **1. Python Virtual Environment**
```bash
# Navigate to project root
cd /path/to/ai-health-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### **2. Install Backend Dependencies**
```bash
# Install all required packages
pip install -r backend/requirements.txt

# Verify installation
pip list | grep fastapi
```

### **3. Initialize Database**
```bash
# Navigate to backend directory
cd backend

# Initialize database (if using Alembic)
# This creates the database tables
python -c "
from app.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
print('Database initialized successfully!')
"
```

---

## 🌐 **Frontend Setup**

### **1. Install Frontend Dependencies**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (choose one)
npm install
# OR
yarn install
```

### **2. Verify Frontend Setup**
```bash
# Check if packages installed correctly
npm list react
npm list @tanstack/react-query
```

---

## 🏃‍♂️ **Running the Application**

### **Method 1: Manual Start (Two Terminals)**

#### **Terminal 1 - Backend**
```bash
# Navigate to project root and activate venv
cd /path/to/ai-health-backend
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start FastAPI backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
```

#### **Terminal 2 - Frontend**
```bash
# Navigate to frontend directory
cd /path/to/ai-health-backend/frontend

# Start React development server
npm start

# You should see:
# Compiled successfully!
# You can now view ai-health-frontend in the browser.
# Local: http://localhost:3000
```

### **Method 2: Using Process Manager (Recommended)**

#### **Install Concurrently (One-time setup)**
```bash
# In project root
npm install -g concurrently
```

#### **Create Start Script**
Create `start-dev.sh` in project root:

```bash
#!/bin/bash

# AI Health Tracker - Development Starter Script

echo "🚀 Starting AI Health Tracker Development Environment..."

# Activate Python virtual environment
source venv/bin/activate

# Start both backend and frontend concurrently
concurrently \
  --prefix "[{name}]" \
  --names "backend,frontend" \
  --prefix-colors "blue,green" \
  "cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" \
  "cd frontend && npm start"
```

Make it executable and run:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

---

## 🔗 **Application URLs**

Once both services are running:

- **Frontend (React)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Alternative Docs**: http://localhost:8000/redoc

---

## 🧪 **Testing the Setup**

### **1. Backend Health Check**
```bash
# Test backend is running
curl http://localhost:8000/health

# Should return: {"status": "healthy"}
```

### **2. Frontend Connection Test**
1. Open http://localhost:3000 in your browser
2. Try to register/login
3. Upload a test medical file
4. Check if API calls work in browser developer tools

### **3. Full Integration Test**
1. Register a new user account
2. Upload a medical document
3. Check if OCR analysis works
4. Verify individual metric explanations appear
5. Test the text analysis feature

---

## 🐛 **Troubleshooting**

### **Common Issues & Solutions**

#### **Backend Issues**

**Port 8000 already in use:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --port 8001
# Update REACT_APP_API_URL to http://localhost:8001
```

**Database errors:**
```bash
# Reset database
rm app.db  # If using SQLite
python -c "
from app.database import engine, Base
from app.models import *
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
"
```

**Missing dependencies:**
```bash
# Reinstall all dependencies
pip install -r backend/requirements.txt --force-reinstall
```

#### **Frontend Issues**

**Port 3000 already in use:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or start on different port
PORT=3001 npm start
```

**API connection errors:**
- Check `frontend/.env` has correct `REACT_APP_API_URL`
- Verify backend is running on the specified port
- Check browser console for CORS errors

**Build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### **CORS Issues**
If you get CORS errors, ensure your backend `.env` includes:
```env
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"]
```

---

## 📦 **Production Deployment**

### **Backend Production**
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### **Frontend Production**
```bash
# Build for production
cd frontend
npm run build

# Serve built files (install serve globally)
npm install -g serve
serve -s build -l 3000
```

---

## 🔄 **Development Workflow**

### **Daily Development**
1. **Start development servers**: `./start-dev.sh`
2. **Make changes** to backend (Python) or frontend (React/TypeScript)
3. **Auto-reload** happens automatically
4. **Test changes** in browser at http://localhost:3000
5. **Check API docs** at http://localhost:8000/docs

### **Adding New Features**
1. **Backend changes**: Modify files in `backend/app/`
2. **Frontend changes**: Modify files in `frontend/src/`
3. **API integration**: Update `frontend/src/config/api.ts`
4. **Test integration**: Use both frontend UI and API docs

---

## 📖 **Additional Resources**

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **TypeScript Documentation**: https://www.typescriptlang.org/docs/
- **Tailwind CSS Documentation**: https://tailwindcss.com/docs

---

## ✅ **Success Checklist**

- [ ] Python virtual environment activated
- [ ] Backend dependencies installed
- [ ] Database initialized
- [ ] Frontend dependencies installed
- [ ] Environment variables configured
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] API documentation accessible
- [ ] User registration/login works
- [ ] File upload functionality works
- [ ] OCR analysis with individual explanations works
- [ ] Text analysis feature works

**🎉 You're ready to develop with the AI Health Tracker!** 