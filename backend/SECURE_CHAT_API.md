# Secure Chat System API Documentation

## Overview

The AI Health Tracker includes a secure chat system that enables private communication between patients and doctors. This system ensures HIPAA-compliant messaging with file attachments for sharing medical documents and lab results.

## 🔐 Security Features

- **Role-Based Communication**: Only patients can message doctors and vice versa
- **JWT Authentication**: All endpoints require valid authentication tokens
- **File Upload Security**: Validated file types and size limits (10MB max)
- **Private Conversations**: Users can only access their own messages
- **User Data Isolation**: Messages and files stored in user-specific directories
- **Read Receipt Tracking**: Track message read status
- **Audit Trail**: Complete history of all communications

## 🏥 Supported Communication

| User Type | Can Message | Cannot Message |
|-----------|-------------|----------------|
| **Patient** | ✅ Doctors | ❌ Other Patients |
| **Doctor** | ✅ Patients | ❌ Other Doctors |

## 📋 API Endpoints

### 1. Send Message

**POST** `/chat/send`

Send a message with optional file attachment.

#### Request Format
```http
POST /chat/send
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data

receiver_id: {user_id}
message_text: {message_content}
file: {optional_file_upload}
```

#### Parameters
- **receiver_id** (required): ID of the message recipient
- **message_text** (required): Message content (1-5000 characters)
- **file** (optional): File attachment (max 10MB)

#### Supported File Types
- **Medical Documents**: PDF, DOC, DOCX
- **Images**: JPEG, PNG, GIF, BMP, TIFF
- **Text Files**: TXT, CSV
- **Spreadsheets**: XLS, XLSX

#### Example Request
```bash
curl -X POST "http://127.0.0.1:8001/chat/send" \
  -H "Authorization: Bearer your_jwt_token" \
  -F "receiver_id=2" \
  -F "message_text=Hello Doctor, please review my lab results" \
  -F "file=@lab_results.pdf"
```

#### Response
```json
{
  "id": 1,
  "sender_id": 1,
  "receiver_id": 2,
  "message_text": "Hello Doctor, please review my lab results",
  "attachment_filename": "lab_results.pdf",
  "attachment_size": 245760,
  "attachment_type": "application/pdf",
  "is_read": "false",
  "created_at": "2024-01-15T10:30:00Z",
  "sender": {
    "id": 1,
    "full_name": "John Patient",
    "email": "patient@example.com",
    "role": "patient",
    "created_at": "2024-01-15T09:00:00Z"
  },
  "receiver": {
    "id": 2,
    "full_name": "Dr. Smith",
    "email": "doctor@example.com",
    "role": "doctor",
    "created_at": "2024-01-15T08:00:00Z"
  }
}
```

### 2. Get Conversation History

**GET** `/chat/history?with_user={user_id}&limit={limit}&offset={offset}`

Retrieve conversation history with another user.

#### Parameters
- **with_user** (required): ID of the other user
- **limit** (optional): Number of messages (1-100, default: 50)
- **offset** (optional): Skip messages for pagination (default: 0)

#### Example Request
```bash
curl -X GET "http://127.0.0.1:8001/chat/history?with_user=2&limit=20" \
  -H "Authorization: Bearer your_jwt_token"
```

#### Response
```json
{
  "messages": [
    {
      "id": 2,
      "sender_id": 2,
      "receiver_id": 1,
      "message_text": "Thank you for sharing the results. Everything looks normal.",
      "attachment_filename": null,
      "is_read": "true",
      "created_at": "2024-01-15T11:00:00Z",
      "sender": { ... },
      "receiver": { ... }
    },
    {
      "id": 1,
      "sender_id": 1,
      "receiver_id": 2,
      "message_text": "Hello Doctor, please review my lab results",
      "attachment_filename": "lab_results.pdf",
      "is_read": "true",
      "created_at": "2024-01-15T10:30:00Z",
      "sender": { ... },
      "receiver": { ... }
    }
  ],
  "total_count": 2,
  "has_more": false
}
```

### 3. Get All Conversations

**GET** `/chat/conversations`

Get list of all conversations for the current user.

#### Example Request
```bash
curl -X GET "http://127.0.0.1:8001/chat/conversations" \
  -H "Authorization: Bearer your_jwt_token"
```

#### Response
```json
{
  "conversations": [
    {
      "user_id": 2,
      "full_name": "Dr. Smith",
      "role": "doctor",
      "last_message_at": "2024-01-15T11:00:00Z",
      "unread_count": 0
    },
    {
      "user_id": 3,
      "full_name": "Dr. Johnson",
      "role": "doctor",
      "last_message_at": "2024-01-14T15:30:00Z",
      "unread_count": 2
    }
  ]
}
```

### 4. Download File Attachment

**GET** `/chat/download/{message_id}`

Download file attachment from a message.

#### Example Request
```bash
curl -X GET "http://127.0.0.1:8001/chat/download/1" \
  -H "Authorization: Bearer your_jwt_token" \
  -o downloaded_file.pdf
```

### 5. Mark Messages as Read

**PUT** `/chat/mark-read/{other_user_id}`

Mark all messages from another user as read.

#### Example Request
```bash
curl -X PUT "http://127.0.0.1:8001/chat/mark-read/2" \
  -H "Authorization: Bearer your_jwt_token"
```

#### Response
```json
{
  "message": "Messages marked as read"
}
```

### 6. Get Available Chat Users

**GET** `/chat/users`

Get list of users available for starting new conversations.

#### Example Request
```bash
curl -X GET "http://127.0.0.1:8001/chat/users" \
  -H "Authorization: Bearer your_jwt_token"
```

#### Response
```json
[
  {
    "user_id": 2,
    "full_name": "Dr. Smith",
    "role": "doctor",
    "last_message_at": null,
    "unread_count": 0
  },
  {
    "user_id": 3,
    "full_name": "Dr. Johnson",
    "role": "doctor",
    "last_message_at": null,
    "unread_count": 0
  }
]
```

### 7. Delete Message

**DELETE** `/chat/message/{message_id}`

Delete a message (only the sender can delete their own messages).

#### Example Request
```bash
curl -X DELETE "http://127.0.0.1:8001/chat/message/1" \
  -H "Authorization: Bearer your_jwt_token"
```

#### Response
```json
{
  "message": "Message deleted successfully"
}
```

## 🔧 Error Responses

### Common Error Codes

| Status Code | Description | Example |
|-------------|-------------|---------|
| **400** | Bad Request | Invalid message format |
| **401** | Unauthorized | Missing or invalid JWT token |
| **403** | Forbidden | Role validation failed |
| **404** | Not Found | User or message not found |
| **413** | Payload Too Large | File exceeds 10MB limit |
| **415** | Unsupported Media Type | Invalid file type |

### Example Error Response
```json
{
  "detail": "Only patients and doctors can chat with each other"
}
```

## 📱 Usage Examples

### Patient-Doctor Communication Flow

1. **Patient sends initial message with lab results**:
```bash
curl -X POST "http://127.0.0.1:8001/chat/send" \
  -H "Authorization: Bearer patient_token" \
  -F "receiver_id=2" \
  -F "message_text=Hello Dr. Smith, I received my blood test results and have some questions. Could you please review them?" \
  -F "file=@blood_test_results.pdf"
```

2. **Doctor reviews and responds**:
```bash
curl -X POST "http://127.0.0.1:8001/chat/send" \
  -H "Authorization: Bearer doctor_token" \
  -F "receiver_id=1" \
  -F "message_text=Thank you for sharing your results. Your cholesterol levels are slightly elevated. I recommend dietary changes and a follow-up in 3 months."
```

3. **Patient checks conversation history**:
```bash
curl -X GET "http://127.0.0.1:8001/chat/history?with_user=2" \
  -H "Authorization: Bearer patient_token"
```

### File Sharing Best Practices

1. **Supported Medical Documents**:
   - Lab results (PDF, images)
   - Medical reports (DOC, DOCX)
   - X-rays and scans (JPEG, PNG, TIFF)
   - Prescription records (PDF, images)

2. **File Size Optimization**:
   - Compress large images before uploading
   - Use PDF format for text documents
   - Maximum file size: 10MB

3. **Security Considerations**:
   - Files are stored in user-specific directories
   - Only sender and receiver can download attachments
   - Files are automatically deleted when messages are deleted

## 🔐 Authentication Requirements

All chat endpoints require JWT authentication:

1. **Register** a user account (`/auth/register`)
2. **Login** to get JWT token (`/auth/login`)
3. **Include token** in Authorization header: `Bearer {token}`

## 📊 Database Schema

### ChatMessage Table
```sql
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    message_text TEXT NOT NULL,
    attachment_filename VARCHAR(255),
    attachment_path VARCHAR(500),
    attachment_size INTEGER,
    attachment_type VARCHAR(50),
    is_read VARCHAR(10) DEFAULT 'false',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_chat_system.py
```

The test suite covers:
- User authentication and role validation
- Message sending with and without files
- Conversation history retrieval
- Security and access control
- File upload and download
- Read receipt functionality

## 🚀 Production Deployment

### Security Checklist
- [ ] HTTPS enabled for all communication
- [ ] File upload directory permissions properly set
- [ ] Regular database backups configured
- [ ] Rate limiting implemented
- [ ] Audit logging enabled
- [ ] CORS properly configured for production domains

### Performance Optimization
- [ ] Database indexes on sender_id, receiver_id, created_at
- [ ] File cleanup scheduled task for deleted messages
- [ ] Message pagination implemented
- [ ] Caching for conversation lists

## 🏥 HIPAA Compliance Features

- **Encryption**: All communications encrypted in transit (HTTPS)
- **Access Control**: Role-based access with authentication
- **Audit Trail**: Complete logging of all communications
- **Data Isolation**: User-specific data storage
- **Secure File Handling**: Validated uploads with access control
- **Automatic Cleanup**: Configurable message retention policies

The secure chat system provides a robust foundation for patient-doctor communication while maintaining the highest security and privacy standards required for healthcare applications.

## 🔗 Integration with AI Health Analysis

The chat system seamlessly integrates with the existing AI health analysis features:

- Patients can share OCR-processed lab results directly in chat
- Doctors can review AI-generated health explanations
- Chat history preserves all medical communications for reference
- File attachments can be processed through the OCR system

This creates a complete healthcare communication ecosystem within the AI Health Tracker platform. 