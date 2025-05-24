# Groq API Setup Guide

## Quick Start

The AI Health Tracker has been successfully migrated from OpenRouter to Groq API. To use the system, you need to set up your Groq API key.

### 1. Get Your Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key (starts with `gsk_...`)

### 2. Set Environment Variable

**For Unix/Linux/macOS:**
```bash
export GROQ_API_KEY=your_groq_api_key_here
```

**For Windows:**
```cmd
set GROQ_API_KEY=your_groq_api_key_here
```

**For permanent setup, add to your shell profile:**
```bash
echo 'export GROQ_API_KEY=your_groq_api_key_here' >> ~/.bashrc
# or for zsh
echo 'export GROQ_API_KEY=your_groq_api_key_here' >> ~/.zshrc
```

### 3. Verify Setup

Run the test script to verify everything is working:

```bash
python test_groq_api_migration.py
```

### 4. Start the Server

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Migration Details

### What Changed

✅ **API Provider**: OpenRouter → Groq API  
✅ **Model**: `mistralai/mistral-7b-instruct` → `meta-llama/llama-4-scout-17b-16e-instruct`  
✅ **Environment Variable**: `OPENROUTER_API_KEY` → `GROQ_API_KEY`  
✅ **Endpoint**: Updated to Groq's API endpoint  
✅ **Performance**: Faster response times with optimized infrastructure  

### What Stayed the Same

✅ **All API endpoints** remain unchanged  
✅ **Authentication system** works exactly the same  
✅ **Individual metric explanations** function identically  
✅ **Caching and error handling** preserved  
✅ **User interface** and responses unchanged  

## Testing

### Test the Migration

Run the comprehensive test suite:

```bash
# Test all functionality
python test_groq_api_migration.py

# Test authentication (optional)
python test_authentication_system.py
```

### Manual Testing

1. **Register a user:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123",
    "role": "patient"
  }'
```

2. **Login:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

3. **Test explanation with your token:**
```bash
curl -X POST "http://127.0.0.1:8000/explain/metrics" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Гемоглобин: 140 г/л (норма: 120-160)"
  }'
```

## Troubleshooting

### Common Issues

**1. "GROQ_API_KEY environment variable not set"**
- Make sure you've exported the GROQ_API_KEY variable
- Restart your terminal/shell after setting it
- Verify with: `echo $GROQ_API_KEY`

**2. "Groq API error: 401"**
- Check that your API key is correct
- Ensure the key has proper permissions
- Verify the key hasn't expired

**3. "Groq API request timed out"**
- Check your internet connectivity
- Groq API might be experiencing high load
- The system will use fallback responses automatically

**4. Server startup issues**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that the server port isn't already in use
- Verify Python environment is activated

### Getting Help

- Check the server logs for detailed error messages
- Run the test scripts to isolate issues
- Verify your Groq API key status in the Groq Console

## Benefits of Groq API

🚀 **Performance**: Significantly faster inference times  
🔧 **Reliability**: More stable API with better uptime  
🤖 **Model**: Meta-Llama model optimized for medical text  
💰 **Cost-effective**: Competitive pricing for API calls  
📊 **Monitoring**: Better API usage analytics and monitoring  

The migration maintains 100% compatibility with your existing setup while providing better performance and reliability. 