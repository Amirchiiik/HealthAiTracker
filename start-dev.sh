#!/bin/bash

# ============================================
# AI Health Tracker - Development Starter
# ============================================

echo "🚀 Starting AI Health Tracker Development Environment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}🐍 Activating Python virtual environment...${NC}"
source venv/bin/activate

# Check if backend dependencies are installed
echo -e "${BLUE}📦 Checking backend dependencies...${NC}"
if ! pip show fastapi > /dev/null 2>&1; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    pip install -r backend/requirements.txt
    echo -e "${GREEN}✅ Backend dependencies installed${NC}"
fi

# Check if frontend dependencies are installed
echo -e "${BLUE}📦 Checking frontend dependencies...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
fi
cd ..

# Check if environment files exist
echo -e "${BLUE}⚙️ Checking environment configuration...${NC}"

# Backend .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating backend .env file...${NC}"
    cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///./app.db

# Authentication
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI/OCR Services
GROQ_API_KEY=your-groq-api-key-here

# CORS Settings (for development)
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# File Upload Settings
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=10485760

# Logging
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}✅ Backend .env created${NC}"
    echo -e "${YELLOW}⚠️ Please update your GROQ_API_KEY in .env${NC}"
fi

# Frontend .env
if [ ! -f "frontend/.env" ]; then
    echo -e "${YELLOW}Creating frontend .env file...${NC}"
    cat > frontend/.env << EOF
# Backend API URL
REACT_APP_API_URL=http://localhost:8000

# Other settings
REACT_APP_VERSION=1.0.0
EOF
    echo -e "${GREEN}✅ Frontend .env created${NC}"
fi

# Initialize database if needed
echo -e "${BLUE}🗄️ Checking database...${NC}"
cd backend
if [ ! -f "app.db" ]; then
    echo -e "${YELLOW}Initializing database...${NC}"
    python -c "
from app.database import engine, Base
from app.models import *
try:
    Base.metadata.create_all(bind=engine)
    print('Database initialized successfully!')
except Exception as e:
    print(f'Database initialization error: {e}')
"
    echo -e "${GREEN}✅ Database initialized${NC}"
fi
cd ..

# Check if concurrently is installed
if ! command -v concurrently &> /dev/null; then
    echo -e "${YELLOW}Installing concurrently for process management...${NC}"
    npm install -g concurrently
    echo -e "${GREEN}✅ Concurrently installed${NC}"
fi

# Start both services
echo -e "${GREEN}🌟 Starting both Backend and Frontend...${NC}"
echo -e "${BLUE}📍 Backend will run on: http://localhost:8000${NC}"
echo -e "${BLUE}📍 Frontend will run on: http://localhost:3000${NC}"
echo -e "${BLUE}📍 API Docs will be at: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both services${NC}"
echo ""

# Start both services with concurrently
concurrently \
  --prefix "[{name}]" \
  --names "🔧 BACKEND,🌐 FRONTEND" \
  --prefix-colors "blue,green" \
  --kill-others \
  --restart-tries 3 \
  "cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" \
  "cd frontend && npm start" 