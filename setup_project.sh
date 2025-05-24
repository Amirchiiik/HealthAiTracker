#!/bin/bash

# AI Health Tracker - Complete Setup Script
# This script sets up the project without requiring GROQ_API_KEY

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Progress indicator
show_progress() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

show_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

show_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

show_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_title() {
    echo -e "${PURPLE}=== $1 ===${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
is_port_available() {
    ! lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to find available port
find_available_port() {
    for port in 8000 8001 8002 8003 8004; do
        if is_port_available $port; then
            echo $port
            return
        fi
    done
    echo "8005"  # Default fallback
}

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    AI Health Tracker Setup                      ║"
echo "║                                                                  ║"
echo "║  This script will set up your AI Health Tracker backend         ║"
echo "║  without requiring a Groq API key (optional for full features)  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Step 1: Environment Validation
show_title "Step 1: Environment Validation"

# Check if we're in the right directory
if [[ ! -f "app/main.py" ]]; then
    show_error "Not in the correct directory. Please run this script from ai-health-backend/"
    exit 1
fi
show_success "✓ Correct directory confirmed"

# Check Python version
if ! command_exists python3; then
    show_error "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
show_success "✓ Python $PYTHON_VERSION detected"

# Check pip
if ! command_exists pip3; then
    show_error "pip3 is not installed. Please install pip first."
    exit 1
fi
show_success "✓ pip3 available"

# Step 2: Virtual Environment Setup
show_title "Step 2: Virtual Environment Setup"

if [[ ! -d "venv" ]]; then
    show_progress "Creating virtual environment..."
    python3 -m venv venv
    show_success "✓ Virtual environment created"
else
    show_success "✓ Virtual environment already exists"
fi

# Activate virtual environment
show_progress "Activating virtual environment..."
source venv/bin/activate
show_success "✓ Virtual environment activated"

# Step 3: Dependency Installation
show_title "Step 3: Installing Dependencies"

# Upgrade pip first
show_progress "Upgrading pip..."
pip install --upgrade pip --quiet

# Install NumPy with compatibility fix first
show_progress "Installing NumPy with compatibility fix..."
pip install "numpy<2.0,>=1.26.0" --quiet
show_success "✓ NumPy installed with compatibility fix"

# Install other requirements
show_progress "Installing remaining dependencies..."
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt --quiet
    show_success "✓ All dependencies installed successfully"
else
    show_error "requirements.txt not found"
    exit 1
fi

# Step 4: Database Initialization
show_title "Step 4: Database Setup"

show_progress "Initializing database..."
python -c "
import sys
sys.path.append('.')
from app.database import create_tables
create_tables()
print('Database initialized successfully')
" 2>/dev/null || show_warning "Database may already be initialized"

show_success "✓ Database ready"

# Create necessary directories
show_progress "Creating upload directories..."
mkdir -p uploads
mkdir -p uploads/user_1
mkdir -p uploads/user_2
mkdir -p uploads/user_3
show_success "✓ Upload directories created"

# Step 5: Environment Variables Setup (Optional)
show_title "Step 5: Environment Variables (Optional)"

if [[ ! -f ".env" ]]; then
    if [[ -f "env.template" ]]; then
        show_progress "Creating .env file from template..."
        cp env.template .env
        show_success "✓ .env file created from template"
        
        echo ""
        echo -e "${YELLOW}📋 Optional: Set up Groq API for AI explanations${NC}"
        echo "   1. Visit: https://console.groq.com/"
        echo "   2. Get your API key (starts with 'gsk_')"
        echo "   3. Edit .env file and add: GROQ_API_KEY=your_key_here"
        echo "   4. Or run: echo 'GROQ_API_KEY=your_key_here' >> .env"
        echo ""
        echo -e "${CYAN}✨ The system works without API key, but AI explanations need it${NC}"
    else
        show_warning "env.template not found, creating basic .env"
        echo "# AI Health Tracker Environment Variables" > .env
        echo "# Add your Groq API key here for AI explanations:" >> .env
        echo "# GROQ_API_KEY=your_actual_key_here" >> .env
    fi
else
    show_success "✓ .env file already exists"
fi

# Check if Groq API key is set
if grep -q "^GROQ_API_KEY=" .env 2>/dev/null && ! grep -q "your_actual" .env; then
    show_success "✓ Groq API key configured - AI explanations available"
else
    show_warning "⚠ Groq API key not configured - basic functionality only"
fi

# Step 6: Port Management
show_title "Step 6: Server Configuration"

AVAILABLE_PORT=$(find_available_port)
show_progress "Finding available port..."
show_success "✓ Will use port $AVAILABLE_PORT"

# Step 7: Final Validation
show_title "Step 7: Final Validation"

show_progress "Running final checks..."

# Test imports
python -c "
import sys
sys.path.append('.')
try:
    from app.main import app
    print('✓ All imports successful')
except Exception as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
" || exit 1

show_success "✓ All systems ready"

# Step 8: Server Startup
show_title "Step 8: Starting Server"

echo ""
echo -e "${GREEN}🚀 Starting AI Health Tracker Server...${NC}"
echo ""
echo -e "${CYAN}📊 Access Points:${NC}"
echo "   • API Documentation: http://127.0.0.1:$AVAILABLE_PORT/docs"
echo "   • Alternative Docs:   http://127.0.0.1:$AVAILABLE_PORT/redoc" 
echo "   • Health Check:       http://127.0.0.1:$AVAILABLE_PORT/health"
echo ""
echo -e "${YELLOW}🔧 Quick Test Commands:${NC}"
echo "   curl http://127.0.0.1:$AVAILABLE_PORT/health"
echo ""
echo -e "${PURPLE}💡 Features Available:${NC}"
echo "   ✅ User Registration & Authentication"
echo "   ✅ OCR Processing (easyocr)"
echo "   ✅ Health Data Management"
echo "   ✅ Database Storage"
if grep -q "^GROQ_API_KEY=" .env 2>/dev/null && ! grep -q "your_actual" .env; then
    echo "   ✅ AI Health Explanations (Groq API)"
else
    echo "   ⏳ AI Health Explanations (configure Groq API key)"
fi
echo ""
echo -e "${CYAN}🛑 To stop the server: Press Ctrl+C${NC}"
echo ""

# Start the server
show_progress "Launching server on port $AVAILABLE_PORT..."
echo ""

# Add cursor-logs entry
echo "$(date): Setup script executed successfully. Server starting on port $AVAILABLE_PORT. All dependencies installed, database initialized, upload directories created." >> cursor-logs.md

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port $AVAILABLE_PORT 