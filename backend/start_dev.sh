#!/bin/bash

# =============================================================================
# AI Health Tracker Backend - Quick Development Start Script
# =============================================================================
# This script quickly starts the development server with proper environment
# Usage: ./start_dev.sh [--port PORT] [--host HOST]
# =============================================================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8001"
HOST="$DEFAULT_HOST"
PORT="$DEFAULT_PORT"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --port PORT       Port to run the server on (default: 8001)"
            echo "  --host HOST       Host to bind to (default: 0.0.0.0)"
            echo "  --help, -h        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
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

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]] || [[ ! -d "app" ]]; then
    log_error "This script must be run from the backend project directory"
    log_info "Make sure you're in the directory containing requirements.txt and app/ folder"
    exit 1
fi

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    log_error "Virtual environment not found"
    log_info "Run ./setup_project.sh first to set up the project"
    exit 1
fi

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    log_warning ".env file not found"
    log_info "Creating basic .env file. Remember to update it with your API keys!"
    
    cat > .env << 'EOF'
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///./health_tracker.db
GROQ_API_KEY=gsk_your_groq_api_key_here
HOST=0.0.0.0
PORT=8001
ENVIRONMENT=development
DEFAULT_LANGUAGE=ru
EOF
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate

if [[ ! "$VIRTUAL_ENV" ]]; then
    log_error "Failed to activate virtual environment"
    exit 1
fi

log_success "Virtual environment activated"

# Check if dependencies are installed
log_info "Checking core dependencies..."
python -c "import fastapi, uvicorn, groq" 2>/dev/null
if [[ $? -ne 0 ]]; then
    log_warning "Some dependencies may be missing"
    log_info "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
fi

# Create uploads directory if it doesn't exist
if [[ ! -d "uploads" ]]; then
    log_info "Creating uploads directory..."
    mkdir -p uploads/users
    chmod 755 uploads
fi

# Display startup information
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 Starting AI Health Tracker Backend${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📍 Server URL:${NC} http://$HOST:$PORT"
echo -e "${BLUE}📚 API Docs:${NC}  http://$HOST:$PORT/docs"
echo -e "${BLUE}📖 ReDoc:${NC}     http://$HOST:$PORT/redoc"
echo -e "${BLUE}🌍 Language:${NC}  Russian (ru) and English (en) support enabled"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Check API key
if grep -q "gsk_your_groq_api_key_here" .env; then
    log_warning "Remember to update your GROQ_API_KEY in .env file for full functionality"
fi

log_info "Starting development server..."
log_info "Press Ctrl+C to stop the server"

# Start the server
uvicorn app.main:app --reload --host "$HOST" --port "$PORT" 