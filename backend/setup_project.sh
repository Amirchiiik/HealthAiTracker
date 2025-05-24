#!/bin/bash

# =============================================================================
# AI Health Tracker Backend - Automated Setup Script
# =============================================================================
# This script automates the initial setup of the FastAPI-based backend project
# Usage: ./setup_project.sh [--skip-venv] [--skip-tests]
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="AI Health Tracker Backend"
PYTHON_VERSION="3.8"
VENV_NAME="venv"
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"

# Parse command line arguments
SKIP_VENV=false
SKIP_TESTS=false
FORCE_REINSTALL=false

for arg in "$@"; do
    case $arg in
        --skip-venv)
            SKIP_VENV=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --force-reinstall)
            FORCE_REINSTALL=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --skip-venv       Skip virtual environment setup"
            echo "  --skip-tests      Skip dependency testing"
            echo "  --force-reinstall Force reinstall all dependencies"
            echo "  --help, -h        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "\n${PURPLE}🚀 $1${NC}"
}

check_command() {
    if command -v $1 &> /dev/null; then
        log_success "$1 is available"
        return 0
    else
        log_error "$1 is not installed"
        return 1
    fi
}

check_python_version() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python is not installed"
        return 1
    fi

    PYTHON_VER=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
    log_info "Found Python $PYTHON_VER"
    
    # Check if version is >= 3.8
    if [[ "$(printf '%s\n' "$PYTHON_VERSION" "$PYTHON_VER" | sort -V | head -n1)" = "$PYTHON_VERSION" ]]; then
        log_success "Python version $PYTHON_VER is compatible (>= $PYTHON_VERSION)"
        return 0
    else
        log_error "Python version $PYTHON_VER is not compatible. Need >= $PYTHON_VERSION"
        return 1
    fi
}

setup_virtual_environment() {
    log_step "Setting up virtual environment"
    
    if [[ "$SKIP_VENV" == true ]]; then
        log_warning "Skipping virtual environment setup"
        return 0
    fi

    # Check if virtual environment already exists
    if [[ -d "$VENV_NAME" ]]; then
        if [[ "$FORCE_REINSTALL" == true ]]; then
            log_warning "Removing existing virtual environment"
            rm -rf "$VENV_NAME"
        else
            log_info "Virtual environment already exists"
            return 0
        fi
    fi

    # Create virtual environment
    log_info "Creating virtual environment with $PYTHON_CMD"
    $PYTHON_CMD -m venv $VENV_NAME

    # Verify virtual environment was created
    if [[ -d "$VENV_NAME" ]]; then
        log_success "Virtual environment created successfully"
    else
        log_error "Failed to create virtual environment"
        return 1
    fi
}

activate_virtual_environment() {
    log_step "Activating virtual environment"
    
    if [[ ! -d "$VENV_NAME" ]]; then
        log_error "Virtual environment not found. Run without --skip-venv first."
        return 1
    fi

    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    log_success "Virtual environment activated"
    
    # Verify we're in the virtual environment
    if [[ "$VIRTUAL_ENV" ]]; then
        log_info "Using Python: $(which python)"
        log_info "Python version: $(python --version)"
    else
        log_error "Failed to activate virtual environment"
        return 1
    fi
}

install_dependencies() {
    log_step "Installing Python dependencies"
    
    if [[ ! -f "requirements.txt" ]]; then
        log_error "requirements.txt not found"
        return 1
    fi

    # Upgrade pip first
    log_info "Upgrading pip"
    python -m pip install --upgrade pip

    # Install dependencies
    log_info "Installing dependencies from requirements.txt"
    if [[ "$FORCE_REINSTALL" == true ]]; then
        pip install --force-reinstall -r requirements.txt
    else
        pip install -r requirements.txt
    fi

    log_success "Dependencies installed successfully"
}

setup_environment_file() {
    log_step "Setting up environment configuration"
    
    if [[ -f "$ENV_FILE" ]]; then
        log_warning ".env file already exists"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Keeping existing .env file"
            return 0
        fi
    fi

    # Create .env file with template
    cat > "$ENV_FILE" << 'EOF'
# AI Health Tracker Backend Environment Configuration
# Update these values with your actual configuration

# ===============================
# Database Configuration
# ===============================
DATABASE_URL=sqlite:///./health_tracker.db

# ===============================
# JWT Authentication
# ===============================
SECRET_KEY=your-secret-key-here-change-in-production-make-it-long-and-random-$(date +%s)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ===============================
# AI Services API Keys
# ===============================
# Get your Groq API key from: https://console.groq.com/
GROQ_API_KEY=gsk_your_groq_api_key_here

# OpenRouter API (Optional, for enhanced AI analysis)
# Get your OpenRouter API key from: https://openrouter.ai/
OPENROUTER_API_KEY=sk-or-your_openrouter_api_key_here

# ===============================
# Email Configuration (Optional)
# ===============================
# Gmail Example
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
FROM_EMAIL=your-email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# ===============================
# File Upload Configuration
# ===============================
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads

# ===============================
# CORS Configuration
# ===============================
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000

# ===============================
# Development Settings
# ===============================
ENVIRONMENT=development
DEFAULT_LANGUAGE=ru
HOST=0.0.0.0
PORT=8001
EOF

    log_success ".env file created"
    log_warning "IMPORTANT: Update .env file with your actual API keys and configuration"
}

create_uploads_directory() {
    log_step "Creating uploads directory"
    
    if [[ ! -d "uploads" ]]; then
        mkdir -p uploads
        log_success "uploads directory created"
    else
        log_info "uploads directory already exists"
    fi

    # Create user-specific subdirectories
    mkdir -p uploads/users
    chmod 755 uploads
    log_success "Upload directories configured"
}

initialize_database() {
    log_step "Initializing database"
    
    # Check if database initialization is needed
    log_info "Database will be automatically created on first run"
    log_success "Database initialization prepared"
}

test_dependencies() {
    log_step "Testing dependencies"
    
    if [[ "$SKIP_TESTS" == true ]]; then
        log_warning "Skipping dependency tests"
        return 0
    fi

    # Create a simple test script
    cat > test_deps_temp.py << 'EOF'
import sys
import importlib

dependencies = [
    'fastapi', 'uvicorn', 'sqlalchemy', 'alembic', 'passlib', 'jose', 'jwt', 
    'bcrypt', 'requests', 'httpx', 'easyocr', 'PIL', 'cv2', 'fitz', 'groq',
    'pandas', 'numpy', 'sklearn', 'dotenv', 'pydantic', 'aiofiles', 'pytz',
    'dateutil', 'email_validator', 'pytest', 'gunicorn', 'loguru', 'jsonschema'
]

failed = []
for dep in dependencies:
    try:
        importlib.import_module(dep)
        print(f"✅ {dep}")
    except ImportError as e:
        print(f"❌ {dep} - {e}")
        failed.append(dep)

if failed:
    print(f"\n❌ {len(failed)} dependencies failed to import")
    sys.exit(1)
else:
    print(f"\n✅ All {len(dependencies)} dependencies imported successfully!")
    sys.exit(0)
EOF

    # Run the test
    if python test_deps_temp.py; then
        log_success "All dependencies are working correctly"
    else
        log_error "Some dependencies failed to import"
        rm -f test_deps_temp.py
        return 1
    fi

    # Clean up
    rm -f test_deps_temp.py
}

test_application() {
    log_step "Testing application startup"
    
    if [[ "$SKIP_TESTS" == true ]]; then
        log_warning "Skipping application tests"
        return 0
    fi

    # Test if the FastAPI app can be imported
    python -c "
from app.main import app
import uvicorn
print('✅ FastAPI application imports successfully')
print('✅ Application is ready to start')
" 2>/dev/null

    if [[ $? -eq 0 ]]; then
        log_success "Application startup test passed"
    else
        log_error "Application startup test failed"
        return 1
    fi
}

display_next_steps() {
    log_step "Setup Complete! 🎉"
    
    echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎯 ${PROJECT_NAME} Setup Complete!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    echo -e "\n${YELLOW}📋 Next Steps:${NC}"
    echo -e "${BLUE}1.${NC} ${YELLOW}Activate virtual environment:${NC}"
    echo -e "   source venv/bin/activate"
    
    echo -e "\n${BLUE}2.${NC} ${YELLOW}Update .env file with your API keys:${NC}"
    echo -e "   nano .env  # or use your preferred editor"
    echo -e "   ${RED}Required: GROQ_API_KEY${NC}"
    echo -e "   ${BLUE}Optional: OPENROUTER_API_KEY, SMTP credentials${NC}"
    
    echo -e "\n${BLUE}3.${NC} ${YELLOW}Start the development server:${NC}"
    echo -e "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001"
    echo -e "   ${BLUE}Or:${NC} python -m app.main"
    
    echo -e "\n${BLUE}4.${NC} ${YELLOW}Access the API documentation:${NC}"
    echo -e "   Swagger UI: ${BLUE}http://localhost:8001/docs${NC}"
    echo -e "   ReDoc:      ${BLUE}http://localhost:8001/redoc${NC}"
    
    echo -e "\n${BLUE}5.${NC} ${YELLOW}For production deployment:${NC}"
    echo -e "   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001"
    
    echo -e "\n${GREEN}📚 Documentation:${NC}"
    echo -e "   • Setup Guide: ${BLUE}README.md${NC}"
    echo -e "   • API Docs: ${BLUE}API_ENDPOINTS_DOCUMENTATION.md${NC}"
    echo -e "   • This Setup: ${BLUE}SETUP_VERIFICATION.md${NC}"
    
    echo -e "\n${GREEN}🌍 Language Support:${NC}"
    echo -e "   • Russian (ru) and English (en) localization available"
    echo -e "   • Add ${BLUE}\"language\": \"ru\"${NC} to intelligent agent requests"
    
    echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Main execution
main() {
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}🚀 ${PROJECT_NAME} - Automated Setup${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

    # Check prerequisites
    log_step "Checking prerequisites"
    check_command "python3" || check_command "python" || exit 1
    check_python_version || exit 1
    check_command "pip" || check_command "pip3" || exit 1

    # Setup steps
    setup_virtual_environment || exit 1
    activate_virtual_environment || exit 1
    install_dependencies || exit 1
    setup_environment_file || exit 1
    create_uploads_directory || exit 1
    initialize_database || exit 1
    test_dependencies || exit 1
    test_application || exit 1
    
    # Success!
    display_next_steps
}

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]] || [[ ! -d "app" ]]; then
    log_error "This script must be run from the backend project directory"
    log_info "Make sure you're in the directory containing requirements.txt and app/ folder"
    exit 1
fi

# Run main function
main "$@" 