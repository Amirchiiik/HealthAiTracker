# 🩺 Chat System Troubleshooting Guide

## 🚨 Issue: Cannot Click Chat Buttons

### Quick Fix Steps:

#### 1. **Verify Both Services are Running**
```bash
# Check if backend is running (port 8000)
curl http://localhost:8000/health

# Check if frontend is running (port 3000)
# Open browser to: http://localhost:3000
```

#### 2. **Login as Correct User Role**
- **Problem**: Patients can only chat with doctors, doctors can only chat with patients
- **Solution**: Make sure you're logged in as a doctor to see patients in the chat list
- **Test Credentials**:
  - Doctor: `doctor@example.com` / `Test123!`  
  - Patient: `test@example.com` / `Test123!`

#### 3. **Check Browser Console**
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Look for any red error messages
4. Refresh the page and check again

#### 4. **Check Network Tab**
1. Open Developer Tools → Network tab
2. Refresh the chat page
3. Look for failed API calls (red status codes)
4. Check if WebSocket connection is established

#### 5. **Test Button Click Debug**
The buttons now have debug logging. When you click a user button, you should see:
```
Button clicked for user: [Name] ID: [Number]
```
If you don't see this message, there's a UI issue.

#### 6. **WebSocket Connection**
- Green dot next to "Messages" = Connected ✅
- Red dot = Disconnected ❌
- Debug info shows connection status

### Common Issues & Solutions:

#### **Issue**: "No conversations yet"
- **Cause**: No existing chat history
- **Solution**: Click on a user from "Start a new conversation" section

#### **Issue**: Buttons not responding
- **Cause**: JavaScript errors or authentication issues
- **Check**: Browser console for errors
- **Try**: Refresh page, clear browser cache

#### **Issue**: Can't see other users
- **Cause**: Role mismatch (patients only see doctors, doctors only see patients)
- **Solution**: Login with correct role

#### **Issue**: WebSocket disconnected
- **Cause**: Backend not running or network issues
- **Solution**: Restart backend server

### Manual Testing Steps:

1. **Login as Doctor**:
   ```
   Email: doctor@example.com
   Password: Test123!
   ```

2. **Navigate to Messages** (chat icon in sidebar)

3. **Check Debug Info** shows:
   - Your user info
   - Available users count > 0
   - WebSocket connected (green)

4. **Click a User Button** and verify:
   - Console shows click message
   - Chat area opens with user's name in header
   - Message input appears at bottom

5. **Send a Test Message**:
   - Type "Hello, this is a test"
   - Click send button (should not be disabled)
   - Message appears in chat

### Backend API Endpoints:

- Health Check: `GET http://localhost:8000/health`
- WebSocket: `ws://localhost:8000/ws/{token}`
- Get Conversations: `GET http://localhost:8000/api/chat/conversations`
- Get Available Users: `GET http://localhost:8000/api/chat/users`

### Frontend Debug Info:

The chat page now shows debug information including:
- Current user and role
- Number of available users
- WebSocket connection status

### If All Else Fails:

1. **Restart Both Services**:
   ```bash
   # Backend
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Frontend (new terminal)
   cd frontend
   npm start
   ```

2. **Clear Browser Data**:
   - Clear cache and cookies
   - Try incognito mode

3. **Check User Database**:
   - Ensure test users exist with correct roles
   - Verify authentication tokens are valid

### Success Indicators:

✅ Backend health check returns `{"status":"ok"}`  
✅ Frontend loads at `http://localhost:3000`  
✅ Can login with test credentials  
✅ Chat page shows debug info correctly  
✅ WebSocket status shows connected  
✅ Available users count > 0  
✅ Button clicks show console debug messages  
✅ Chat interface opens when clicking user  
✅ Can send and receive messages  

---

**🏥 The Chat System is Working When:**
- You can see the list of available users
- Buttons respond to clicks (console logging)
- Chat conversation opens after clicking a user
- Message input and send button are functional
- Real-time messaging works between doctor and patient accounts 