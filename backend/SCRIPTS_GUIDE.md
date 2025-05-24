# AI Health Tracker Backend - Scripts Guide

This document provides a comprehensive guide to all the automated scripts available for setting up, running, and deploying the AI Health Tracker backend.

## 📋 Available Scripts

### 1. 🚀 `setup_project.sh` - Initial Project Setup
**Purpose**: Automates the complete initial setup of the FastAPI backend project.

#### Usage
```bash
# Basic setup (recommended for first-time setup)
./setup_project.sh

# Skip virtual environment setup (if already exists)
./setup_project.sh --skip-venv

# Skip dependency testing
./setup_project.sh --skip-tests

# Force reinstall all dependencies
./setup_project.sh --force-reinstall

# Get help
./setup_project.sh --help
```

#### What it does
- ✅ **Prerequisite Checks**: Verifies Python 3.8+ and pip are installed
- ✅ **Virtual Environment**: Creates and activates Python virtual environment
- ✅ **Dependencies**: Installs all packages from `requirements.txt`
- ✅ **Environment Configuration**: Creates `.env` file with template configuration
- ✅ **Directory Setup**: Creates `uploads/` and `uploads/users/` directories
- ✅ **Database Preparation**: Prepares database initialization
- ✅ **Testing**: Verifies all 28 core dependencies can be imported
- ✅ **Application Test**: Confirms FastAPI app can start successfully

#### When to use
- 🆕 **First-time setup** of the project
- 🔄 **Fresh installation** on a new machine
- 🛠️ **Fixing corrupted environment** with `--force-reinstall`

---

### 2. 🏃 `start_dev.sh` - Development Server
**Purpose**: Quick start script for daily development with automatic environment setup.

#### Usage
```bash
# Start with default settings (host: 0.0.0.0, port: 8001)
./start_dev.sh

# Custom port
./start_dev.sh --port 8080

# Custom host
./start_dev.sh --host 127.0.0.1

# Custom host and port
./start_dev.sh --host 0.0.0.0 --port 3001

# Get help
./start_dev.sh --help
```

#### What it does
- ✅ **Environment Check**: Verifies virtual environment and dependencies
- ✅ **Auto-activation**: Activates virtual environment automatically
- ✅ **Dependency Check**: Installs missing dependencies if needed
- ✅ **Directory Setup**: Creates uploads directory if missing
- ✅ **Configuration Check**: Creates basic `.env` if missing
- ✅ **Development Server**: Starts uvicorn with hot-reload enabled

#### When to use
- 📅 **Daily development** work
- 🔄 **Quick testing** of changes
- 🐛 **Debugging** with hot-reload
- 🔧 **Local API testing**

---

### 3. 🏭 `start_prod.sh` - Production Server
**Purpose**: Production-ready server deployment with Gunicorn and performance optimizations.

#### Usage
```bash
# Start with default settings (4 workers, port 8001)
./start_prod.sh

# Custom number of workers
./start_prod.sh --workers 8

# Custom port for production
./start_prod.sh --port 80

# Custom configuration
./start_prod.sh --workers 6 --port 8080 --host 0.0.0.0

# Get help
./start_prod.sh --help
```

#### What it does
- ✅ **Production Checks**: Validates production configuration
- ✅ **Security Verification**: Checks for proper SECRET_KEY and API keys
- ✅ **Gunicorn Server**: Multi-worker ASGI server with uvicorn workers
- ✅ **Logging**: Access and error logs in `logs/gunicorn.log`
- ✅ **Performance**: Optimized worker configuration and request handling
- ✅ **Monitoring**: Process management and automatic restarts

#### When to use
- 🚀 **Production deployment**
- 🏢 **Staging environment**
- 📊 **Load testing**
- 🔒 **Secure hosting**

---

## 🛠️ Script Options Summary

| Script | Primary Use | Key Options | Output |
|--------|-------------|-------------|---------|
| `setup_project.sh` | Initial setup | `--skip-venv`, `--force-reinstall` | Complete project setup |
| `start_dev.sh` | Development | `--port`, `--host` | Hot-reload server |
| `start_prod.sh` | Production | `--workers`, `--port`, `--host` | Multi-worker server |

## 🎯 Quick Start Workflow

### First Time Setup
```bash
# 1. Make scripts executable (if needed)
chmod +x *.sh

# 2. Run initial setup
./setup_project.sh

# 3. Edit .env file with your API keys
nano .env  # or use your preferred editor

# 4. Start development server
./start_dev.sh
```

### Daily Development
```bash
# Activate environment and start server
./start_dev.sh
```

### Production Deployment
```bash
# Start production server
./start_prod.sh
```

## 📁 Directory Structure After Setup

```
backend/
├── app/                        # FastAPI application
├── venv/                       # Virtual environment
├── uploads/                    # File upload directory
│   └── users/                  # User-specific uploads
├── logs/                       # Production logs (created by start_prod.sh)
├── .env                        # Environment configuration
├── requirements.txt            # Dependencies
├── setup_project.sh           # Initial setup script
├── start_dev.sh               # Development server script
├── start_prod.sh              # Production server script
└── SCRIPTS_GUIDE.md           # This documentation
```

## 🔧 Configuration Files

### `.env` File Structure
```env
# Core configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./health_tracker.db
GROQ_API_KEY=gsk_your_actual_api_key

# Optional configuration
OPENROUTER_API_KEY=sk-or-your_key
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Server settings
HOST=0.0.0.0
PORT=8001
ENVIRONMENT=development
DEFAULT_LANGUAGE=ru
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Permission Denied
```bash
# Make scripts executable
chmod +x setup_project.sh start_dev.sh start_prod.sh
```

#### 2. Python Version Issues
```bash
# Check Python version
python3 --version

# If Python 3.8+ not available, install it
# macOS: brew install python@3.9
# Ubuntu: sudo apt install python3.9
```

#### 3. Virtual Environment Issues
```bash
# Reset virtual environment
rm -rf venv
./setup_project.sh --force-reinstall
```

#### 4. Port Already in Use
```bash
# Use different port
./start_dev.sh --port 8002

# Or kill process using port 8001
lsof -ti:8001 | xargs kill -9
```

#### 5. Missing Dependencies
```bash
# Reinstall dependencies
./setup_project.sh --force-reinstall

# Or manually install
source venv/bin/activate
pip install -r requirements.txt
```

#### 6. API Key Issues
```bash
# Verify .env file exists and has correct keys
cat .env | grep GROQ_API_KEY

# Update with actual key
nano .env
```

## 🔍 Script Features

### Error Handling
- ✅ **Exit on Error**: All scripts use `set -e` for immediate error exit
- ✅ **Prerequisite Checks**: Verify environment before proceeding
- ✅ **Clear Error Messages**: Colored output with specific error details
- ✅ **Recovery Suggestions**: Helpful hints for fixing common issues

### User Experience
- 🎨 **Colored Output**: Visual feedback with emojis and colors
- 📊 **Progress Indicators**: Clear step-by-step progress
- ⚙️ **Flexible Options**: Command-line arguments for customization
- 📚 **Help Documentation**: Built-in help with `--help` flag

### Production Ready
- 🔒 **Security Checks**: Validates production configuration
- 📈 **Performance Optimization**: Gunicorn with optimal worker settings
- 📋 **Logging**: Comprehensive access and error logging
- 🔄 **Process Management**: Automatic restarts and health monitoring

## 🌐 URLs and Endpoints

### Development (default: localhost:8001)
- **Application**: http://localhost:8001
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

### Production (configurable)
- **Application**: http://your-domain:8001
- **API Documentation**: http://your-domain:8001/docs
- **Monitoring**: Check `logs/gunicorn.log`

## 📞 Support

### Getting Help
1. **Script Help**: Run any script with `--help` flag
2. **Documentation**: Check `README.md` and `API_ENDPOINTS_DOCUMENTATION.md`
3. **Logs**: Check `logs/gunicorn.log` for production issues
4. **Dependencies**: Run `./setup_project.sh --force-reinstall` for dependency issues

### Advanced Usage
- **Docker**: Scripts can be integrated into Docker containers
- **CI/CD**: Use in automated deployment pipelines
- **Monitoring**: Integrate with process managers like systemd
- **Load Balancing**: Use with nginx or other reverse proxies

---

**🎉 Your AI Health Tracker backend is now ready for development and production deployment!** 