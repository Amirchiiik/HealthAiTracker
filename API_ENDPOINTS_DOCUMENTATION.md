# AI Health Tracker - Complete API Endpoints Documentation

This document provides clear explanations for all API endpoints in the AI Health Tracker system, including authentication requirements, inputs, outputs, and access permissions.

## Authentication Endpoints (`/auth`)

### Register New User
**POST** `/auth/register`
- **Purpose**: Creates a new user account in the system
- **Input**: User details including full name, email, password, and role (patient or doctor)
- **Output**: User profile information with unique ID
- **Access**: Public (no authentication required)
- **Notes**: Passwords must be at least 8 characters with uppercase, lowercase, and digit

### User Login
**POST** `/auth/login`
- **Purpose**: Authenticates existing user and provides access token
- **Input**: Email address and password
- **Output**: JWT access token (valid for 30 minutes) and user profile
- **Access**: Public (no authentication required)
- **Notes**: Access token must be included in all subsequent API requests

### Get Current User Profile
**GET** `/auth/me`
- **Purpose**: Retrieves the authenticated user's profile information
- **Input**: None (uses authentication token)
- **Output**: Complete user profile including ID, name, email, and role
- **Access**: Authenticated users only (both doctors and patients)

### Update User Profile
**PUT** `/auth/me`
- **Purpose**: Updates limited user profile information
- **Input**: User data to update (currently only full name can be changed)
- **Output**: Updated user profile
- **Access**: Authenticated users only (both doctors and patients)

## Chat Communication Endpoints (`/chat`)

### Send Message
**POST** `/chat/send`
- **Purpose**: Sends a secure message between patient and doctor with optional file attachment
- **Input**: Recipient's user ID, message text (1-5000 characters), optional file (max 10MB)
- **Output**: Message details with attachment information if applicable
- **Access**: Authenticated users only
- **Restrictions**: Only patients can message doctors and vice versa (no patient-to-patient or doctor-to-doctor)

### Get Conversation History
**GET** `/chat/history`
- **Purpose**: Retrieves message history between current user and another specific user
- **Input**: Other user's ID, optional pagination parameters (limit, offset)
- **Output**: List of messages in chronological order with attachment details
- **Access**: Authenticated users only (can only see their own conversations)
- **Notes**: Automatically marks messages as read when retrieved

### Get All Conversations
**GET** `/chat/conversations`
- **Purpose**: Lists all conversations for the current user with summary information
- **Input**: None
- **Output**: List of conversation partners with unread message counts and last activity
- **Access**: Authenticated users only (both doctors and patients)

### Download File Attachment
**GET** `/chat/download/{message_id}`
- **Purpose**: Downloads a file attachment from a specific message
- **Input**: Message ID containing the attachment
- **Output**: File download with original filename
- **Access**: Only sender or recipient of the message can download
- **Security**: Validates user permissions before allowing download

### Mark Messages as Read
**PUT** `/chat/mark-read/{user_id}`
- **Purpose**: Marks all messages from a specific user as read
- **Input**: User ID whose messages should be marked as read
- **Output**: Confirmation message
- **Access**: Authenticated users only (can only mark their own received messages)

### Get Available Chat Users
**GET** `/chat/users`
- **Purpose**: Lists users available for starting new conversations
- **Input**: None
- **Output**: List of users with different roles (patients see doctors, doctors see patients)
- **Access**: Authenticated users only
- **Rules**: Patients can only see doctors, doctors can only see patients

### Delete Message
**DELETE** `/chat/message/{message_id}`
- **Purpose**: Deletes a message (only sender can delete their own messages)
- **Input**: Message ID to delete
- **Output**: Confirmation of deletion
- **Access**: Only the original sender of the message
- **Notes**: Also deletes any associated file attachment

## User History Management Endpoints (`/users`)

### Get Health Analysis History
**GET** `/users/me/analyses`
- **Purpose**: Retrieves all health analyses performed by the current user
- **Input**: Optional pagination parameters (limit, offset)
- **Output**: List of health analyses with metrics and results
- **Access**: Authenticated users only (users see their own history only)

### Get Specific Health Analysis
**GET** `/users/me/analyses/{analysis_id}`
- **Purpose**: Retrieves details of a specific health analysis by ID
- **Input**: Analysis ID
- **Output**: Complete analysis details including metrics and explanations
- **Access**: Authenticated users only (only their own analyses)

### Delete Health Analysis
**DELETE** `/users/me/analyses/{analysis_id}`
- **Purpose**: Permanently deletes a health analysis from user's history
- **Input**: Analysis ID to delete
- **Output**: Confirmation of deletion
- **Access**: Authenticated users only (only their own analyses)

### Get Chat Interaction History
**GET** `/users/me/chats`
- **Purpose**: Retrieves history of AI chat interactions
- **Input**: Optional pagination and interaction type filter
- **Output**: List of AI conversations with timestamps and types
- **Access**: Authenticated users only (users see their own chat history only)

### Get Complete User History
**GET** `/users/me/history`
- **Purpose**: Provides combined view of both health analyses and chat interactions
- **Input**: Optional limits for analyses and chats
- **Output**: Combined history with total counts for each category
- **Access**: Authenticated users only (comprehensive personal history)

### Get User Activity Summary
**GET** `/users/me/activity`
- **Purpose**: Shows recent user activity over specified time period
- **Input**: Number of days to analyze (default 30, max 365)
- **Output**: Activity summary with usage patterns and frequency
- **Access**: Authenticated users only (personal activity tracking)

### Get User Statistics
**GET** `/users/me/stats`
- **Purpose**: Provides detailed statistics about user's system usage
- **Input**: None
- **Output**: Total analyses, chats, engagement rates, and account age
- **Access**: Authenticated users only (personal usage statistics)

## Health Analysis Endpoints (`/analysis`)

### Analyze Text with Individual Explanations
**POST** `/analysis/text`
- **Purpose**: Analyzes raw medical text and provides individual explanations for each metric
- **Input**: Raw text containing medical data
- **Output**: Extracted metrics with individual explanations and overall summary
- **Access**: Authenticated users only (both doctors and patients)
- **Features**: Advanced AI analysis with metric-specific insights

### Explain Individual Metrics
**POST** `/analysis/metrics/explain`
- **Purpose**: Generates explanations for pre-extracted health metrics
- **Input**: List of health metrics with values and reference ranges
- **Output**: Each metric with detailed explanation and overall summary
- **Access**: Authenticated users only (both doctors and patients)

### Get Metrics by Status
**GET** `/analysis/metrics/status/{status}`
- **Purpose**: Filters metrics by their status (normal, low, high, elevated)
- **Input**: Status category and optional metrics list
- **Output**: Filtered metrics matching the specified status
- **Access**: Authenticated users only (both doctors and patients)

### Generate Metrics Summary
**POST** `/analysis/summary`
- **Purpose**: Creates detailed summary of all metrics without individual explanations
- **Input**: List of health metrics
- **Output**: Summary grouped by status with recommendations
- **Access**: Authenticated users only (both doctors and patients)

## File Processing Endpoints

### Upload Medical File
**POST** `/upload`
- **Purpose**: Uploads medical documents for processing
- **Input**: Medical file (PDF, PNG, JPG, JPEG, HEIC up to reasonable size)
- **Output**: Unique filename and upload confirmation
- **Access**: Authenticated users only (files stored in user-specific directories)
- **Security**: File type validation and user isolation

### Process OCR on File
**GET** `/ocr/{filename}`
- **Purpose**: Extracts text and analyzes health metrics from uploaded medical files
- **Input**: Filename of previously uploaded file
- **Output**: Extracted text, identified metrics, and basic analysis
- **Access**: Authenticated users only (can only process their own files)
- **Features**: Automatic save to user's health analysis history

### Enhanced OCR with Individual Explanations
**GET** `/ocr/{filename}/with-explanations`
- **Purpose**: Enhanced version that includes individual metric explanations
- **Input**: Filename of previously uploaded file
- **Output**: Complete analysis with individual metric explanations and summaries
- **Access**: Authenticated users only (can only process their own files)
- **Features**: Most comprehensive analysis option with detailed insights

## AI Explanation Endpoints

### Generate Text Explanation
**POST** `/explain`
- **Purpose**: Generates AI-powered explanations for medical text
- **Input**: Raw medical text or data
- **Output**: Comprehensive explanation in understandable language
- **Access**: Authenticated users only (both doctors and patients)
- **Features**: Background processing with timeout handling

### Check Explanation Status
**GET** `/explain/status/{request_id}`
- **Purpose**: Checks the status of a background explanation request
- **Input**: Request ID from previous explanation request
- **Output**: Explanation result or processing status
- **Access**: Available to all users with valid request ID

### Enhanced Metrics Explanation
**POST** `/explain/metrics`
- **Purpose**: Advanced explanation endpoint with individual metric insights
- **Input**: Raw medical text containing health metrics
- **Output**: Individual metric explanations plus overall summary
- **Access**: Authenticated users only (both doctors and patients)
- **Features**: Most advanced AI analysis with detailed metric-by-metric explanations

## System Endpoints

### Root Endpoint
**GET** `/`
- **Purpose**: Basic system status check
- **Input**: None
- **Output**: Welcome message confirming system is running
- **Access**: Public (no authentication required)

### Health Check
**GET** `/health`
- **Purpose**: Verifies system health and availability
- **Input**: None
- **Output**: System status confirmation
- **Access**: Public (no authentication required)
- **Usage**: Used by monitoring systems and load balancers

## Authentication & Authorization Summary

### Access Levels:
- **Public**: No authentication required (`/`, `/health`, `/auth/register`, `/auth/login`)
- **Authenticated Users**: Requires valid JWT token (all other endpoints)
- **Role-Based**: Some features have role-specific restrictions:
  - Chat communication: Only between patients and doctors
  - File access: Users can only access their own files
  - History access: Users can only see their own data

### Security Features:
- JWT token authentication with 30-minute expiration
- User data isolation (users can only access their own information)
- File upload validation and user-specific storage
- Role-based communication restrictions
- Secure file download with permission validation
- Password complexity requirements
- Audit trail for all user interactions

### Data Privacy:
- Complete user data isolation
- Secure file storage with user-specific directories
- Automatic history tracking for audit purposes
- HIPAA-compliant communication between patients and doctors
- Encrypted password storage using bcrypt hashing

This API provides a complete healthcare communication and analysis platform with robust security, comprehensive health metric analysis, and secure patient-doctor communication capabilities. 