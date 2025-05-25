# 🚀 AI Health Tracker - Quick Start

## **Run Both Backend + Frontend in 30 seconds**

### **For macOS/Linux Users:**
```bash
# 1. Make the script executable (one-time only)
chmod +x start-dev.sh

# 2. Run the application
./start-dev.sh
```

### **For Windows Users:**
```cmd
# Run the application
start-dev.bat
```

### **Manual Method (All Platforms):**

**Terminal 1 - Backend:**
```bash
# Activate Python environment and start backend
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
# Start React frontend
cd frontend
npm start
```

---

## **Access Your Application:**

- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000  
- 📚 **API Docs**: http://localhost:8000/docs

---

## **First Time Setup (Automatic)**

The `start-dev.sh` script automatically handles:
- ✅ Creates Python virtual environment
- ✅ Installs backend dependencies
- ✅ Installs frontend dependencies  
- ✅ Creates environment files (.env)
- ✅ Initializes database
- ✅ Installs process manager (concurrently)

**Just run the script and you're ready to go!**

---

## **Environment Variables**

### **Backend (.env)**
```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=dev-secret-key-change-in-production
GROQ_API_KEY=your-groq-api-key-here
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

### **Frontend (frontend/.env)**
```env
REACT_APP_API_URL=http://localhost:8000
```

---

## **What You Can Test:**

1. **Register/Login** at http://localhost:3000
2. **Upload Medical Files** - Try the enhanced OCR with individual explanations
3. **Text Analysis** - Paste medical text directly for analysis
4. **API Documentation** - Explore endpoints at http://localhost:8000/docs

---

## **Troubleshooting:**

**Port conflicts:**
```bash
# Kill processes on conflicting ports
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

**CORS errors:**
- Ensure backend .env has correct CORS_ORIGINS
- Check that both services are running

**Dependencies issues:**
```bash
# Reinstall backend
pip install -r backend/requirements.txt --force-reinstall

# Reinstall frontend
cd frontend && rm -rf node_modules && npm install
```

---

**🎉 You're ready to develop with AI Health Tracker!**

For detailed setup instructions, see `DEVELOPMENT_SETUP.md` 