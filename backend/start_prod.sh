#!/bin/bash

# =============================================================================
# AI Health Tracker Backend - Production Start Script
# =============================================================================
# This script starts the production server with Gunicorn
# Usage: ./start_prod.sh [--workers N] [--port PORT] [--host HOST]
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
DEFAULT_WORKERS="4"
HOST="$DEFAULT_HOST"
PORT="$DEFAULT_PORT"
WORKERS="$DEFAULT_WORKERS"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --workers)
            WORKERS="$2"
            shift 2
            ;;
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
            echo "  --workers N       Number of worker processes (default: 4)"
            echo "  --port PORT       Port to run the server on (default: 8001)"
            echo "  --host HOST       Host to bind to (default: 0.0.0.0)"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Production requirements:"
            echo "  • Set ENVIRONMENT=production in .env"
            echo "  • Configure proper SECRET_KEY"
            echo "  • Set up PostgreSQL (optional, SQLite works too)"
            echo "  • Configure SMTP settings for email notifications"
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
    log_error ".env file not found"
    log_info "Create .env file with production configuration first"
    exit 1
fi

# Production environment checks
log_info "Checking production configuration..."

# Check for production SECRET_KEY
if grep -q "your-secret-key-here" .env || grep -q "dev-secret-key" .env; then
    log_warning "Using development SECRET_KEY in production!"
    log_info "Generate a secure SECRET_KEY for production"
fi

# Check if GROQ_API_KEY is set
if grep -q "gsk_your_groq_api_key_here" .env; then
    log_error "GROQ_API_KEY not configured"
    log_info "Set your actual Groq API key in .env file"
    exit 1
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate

if [[ ! "$VIRTUAL_ENV" ]]; then
    log_error "Failed to activate virtual environment"
    exit 1
fi

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    log_error "Gunicorn not found"
    log_info "Installing gunicorn..."
    pip install gunicorn
fi

# Check core dependencies
log_info "Verifying dependencies..."
python -c "import fastapi, uvicorn, groq, gunicorn" 2>/dev/null
if [[ $? -ne 0 ]]; then
    log_error "Some required dependencies are missing"
    log_info "Run: pip install -r requirements.txt"
    exit 1
fi

# Create uploads directory if it doesn't exist
if [[ ! -d "uploads" ]]; then
    log_info "Creating uploads directory..."
    mkdir -p uploads/users
    chmod 755 uploads
fi

# Create logs directory
if [[ ! -d "logs" ]]; then
    log_info "Creating logs directory..."
    mkdir -p logs
fi

# Display production startup information
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🏭 Starting AI Health Tracker Backend (Production Mode)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📍 Server URL:${NC} http://$HOST:$PORT"
echo -e "${BLUE}👥 Workers:${NC}    $WORKERS processes"
echo -e "${BLUE}📚 API Docs:${NC}  http://$HOST:$PORT/docs"
echo -e "${BLUE}🌍 Language:${NC}  Russian (ru) and English (en) support enabled"
echo -e "${BLUE}📋 Logs:${NC}      logs/gunicorn.log"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

log_success "Production environment verified"
log_info "Starting production server with Gunicorn..."
log_info "Press Ctrl+C to stop the server"

# Start the production server with Gunicorn
exec gunicorn app.main:app \
    --workers "$WORKERS" \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind "$HOST:$PORT" \
    --access-logfile logs/gunicorn.log \
    --error-logfile logs/gunicorn.log \
    --log-level info \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload 