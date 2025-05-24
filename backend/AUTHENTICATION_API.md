# AI Health Tracker - Authentication & User Management API

## Overview
The AI Health Tracker now includes comprehensive authentication and user management with role-based access control, personal data history tracking, and secure JWT token authentication.

## Security Features

### 🔐 Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter  
- At least one digit
- Bcrypt hashing with salt

### 🎫 JWT Token Authentication
- 30-minute token expiration
- Bearer token format
- Required for all protected endpoints

### 👥 Role-Based Access Control
- **Patient**: Can only access their own data
- **Doctor**: Can access their own data

## Authentication Endpoints

### Register User
**POST** `/auth/register`

```json
{
  "full_name": "John Doe",
  "email": "john@example.com", 
  "password": "SecurePass123",
  "role": "patient"
}
```

### Login User
**POST** `/auth/login`

```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

Returns JWT token and user info.

### Get Profile
**GET** `/auth/me`

Get current authenticated user's profile.

## Protected Endpoints

All endpoints now require authentication with Bearer token:
```
Authorization: Bearer <your-jwt-token>
```

### File Operations
- **POST** `/upload` - Upload medical documents
- **GET** `/ocr/{filename}` - Process OCR and save to history
- **GET** `/ocr/{filename}/with-explanations` - Enhanced OCR with explanations

### User History
- **GET** `/users/me/analyses` - Get health analysis history
- **GET** `/users/me/chats` - Get AI chat interaction history
- **GET** `/users/me/history` - Get complete user history
- **GET** `/users/me/stats` - Get user statistics

### Data Management
- **GET** `/users/me/analyses/{id}` - Get specific analysis
- **DELETE** `/users/me/analyses/{id}` - Delete analysis

## Key Features

### Personal Data History
- All health analyses are saved to user accounts
- Chat interactions with AI are tracked
- Complete audit trail of user activities

### Role-Based Security
- Users can only access their own data
- JWT tokens include role information
- Proper authorization checks on all endpoints

### Data Privacy
- User-specific file storage
- Encrypted passwords
- Secure session management

## Usage Example

```bash
# Register
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "John Patient", "email": "patient@test.com", "password": "SecurePass123", "role": "patient"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "patient@test.com", "password": "SecurePass123"}'

# Use protected endpoint
curl -X GET "http://localhost:8000/users/me/analyses" \
  -H "Authorization: Bearer <token>"
```

This system ensures secure, personalized health tracking with complete data history and role-based access control.

## API Updates - Groq Integration

### Latest Migration: OpenRouter → Groq API

The system has been migrated from OpenRouter to Groq API for improved performance and reliability:

**Key Changes:**
- **API Provider**: Now using Groq API instead of OpenRouter
- **Model**: Updated to `meta-llama/llama-4-scout-17b-16e-instruct`
- **Environment Variable**: `GROQ_API_KEY` required instead of `OPENROUTER_API_KEY`
- **Performance**: Faster response times with Groq's optimized infrastructure

**Setup Requirements:**
```bash
# Set your Groq API key
export GROQ_API_KEY=your_groq_api_key_here
```

All existing functionality remains the same - only the underlying AI provider has changed for better performance. 