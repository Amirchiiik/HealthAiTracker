# AI Health Tracker - Security Guide

## 🔐 Environment Variables & API Key Security

### ✅ Secure Implementation
The AI Health Tracker now properly loads the Groq API key from environment variables using a secure approach:

```python
# app/services/llm_service.py
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Securely load Groq API key from environment variables
api_key = os.getenv("GROQ_API_KEY")
```

### 🔑 Setting Up Your API Key

1. **Get Your Groq API Key**:
   - Visit [Groq Console](https://console.groq.com/)
   - Sign up or log in
   - Navigate to "API Keys" section
   - Create a new API key
   - Copy the key (starts with `gsk_...`)

2. **Configure Environment Variables**:
   ```bash
   # Option 1: Create .env file (recommended)
   echo "GROQ_API_KEY=your_actual_token_here" > .env
   
   # Option 2: Set in shell session
   export GROQ_API_KEY="your_actual_token_here"
   
   # Option 3: Add to shell profile (permanent)
   echo 'export GROQ_API_KEY="your_actual_token_here"' >> ~/.zshrc
   ```

3. **Using the Template**:
   ```bash
   # Copy the template and customize
   cp env.template .env
   # Edit .env and add your actual API key
   ```

### 🛡️ Security Best Practices

#### ✅ DO:
- ✅ Store API keys in `.env` files
- ✅ Use `os.getenv()` to load environment variables
- ✅ Add `.env` to `.gitignore`
- ✅ Use different API keys for development/production
- ✅ Rotate API keys regularly
- ✅ Validate API key format on startup
- ✅ Never log or print full API keys

#### ❌ DON'T:
- ❌ Hardcode API keys in source code
- ❌ Commit `.env` files to version control
- ❌ Share API keys in chat or email
- ❌ Use production keys in development
- ❌ Store keys in plain text files
- ❌ Include keys in error messages

### 🔍 API Key Validation

The system automatically validates your API key:

```python
# Validation checks implemented:
if not api_key:
    print("⚠️  Warning: GROQ_API_KEY not found in environment variables.")
elif not api_key.startswith("gsk_"):
    print("⚠️  Warning: GROQ_API_KEY does not appear to be a valid Groq API key.")
else:
    print(f"✅ Groq API key loaded successfully: {api_key[:10]}...")
```

### 📁 File Security

#### Protected Files (via .gitignore):
- `.env` - Environment variables
- `*.db` - Database files
- `uploads/` - User uploaded files
- `__pycache__/` - Python cache
- `venv/` - Virtual environment

#### Security Headers:
- JWT tokens for authentication
- CORS protection
- Request validation
- User data isolation

### 🚨 If Your API Key is Compromised

1. **Immediately revoke** the key in Groq Console
2. **Generate a new** API key
3. **Update your .env** file with the new key
4. **Restart your application**
5. **Check logs** for any unauthorized usage

### 🔧 Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GROQ_API_KEY` | ✅ Yes | Groq API authentication | `gsk_abc123...` |
| `JWT_SECRET_KEY` | ❌ Optional | JWT token signing | `your_secret_key` |
| `DATABASE_URL` | ❌ Optional | Database connection | `sqlite:///health.db` |
| `ENVIRONMENT` | ❌ Optional | App environment | `development` |

### 📊 Security Monitoring

The application includes security monitoring:
- Failed authentication attempts
- Invalid API key usage
- Unauthorized access attempts
- User activity logging

### 🏗️ Production Security

For production deployment:

1. **Use strong JWT secrets**:
   ```bash
   JWT_SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **Enable HTTPS only**
3. **Set secure headers**
4. **Use production database** (PostgreSQL)
5. **Implement rate limiting**
6. **Set up monitoring and alerts**

### ✅ Security Checklist

- [ ] API key stored in `.env` file
- [ ] `.env` added to `.gitignore`
- [ ] API key starts with `gsk_`
- [ ] No hardcoded secrets in code
- [ ] Different keys for dev/prod
- [ ] Regular key rotation scheduled
- [ ] Security monitoring enabled

Your AI Health Tracker is now securely configured with proper environment variable management! 🔐 