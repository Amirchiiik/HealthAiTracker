import os
import uuid
import shutil
from typing import List, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.models import ChatMessage, User
from app.schemas import ChatMessageCreate, ChatMessageResponse, ChatHistoryResponse

# Configuration
CHAT_UPLOAD_DIR = "uploads/chat"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = {
    # Medical documents
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    # Images
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/bmp',
    'image/tiff',
    # Text files
    'text/plain',
    'text/csv',
    # Spreadsheets
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self._ensure_upload_directory()
    
    def _ensure_upload_directory(self):
        """Ensure chat upload directory exists"""
        if not os.path.exists(CHAT_UPLOAD_DIR):
            os.makedirs(CHAT_UPLOAD_DIR, exist_ok=True)
    
    def validate_users_can_chat(self, sender_id: int, receiver_id: int) -> Tuple[User, User]:
        """Validate that two users can chat (patient <-> doctor only)"""
        sender = self.db.query(User).filter(User.id == sender_id).first()
        receiver = self.db.query(User).filter(User.id == receiver_id).first()
        
        if not sender:
            raise HTTPException(status_code=404, detail="Sender not found")
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver not found")
        
        # Check if roles are compatible (patient <-> doctor)
        valid_combinations = [
            (sender.role == 'patient' and receiver.role == 'doctor'),
            (sender.role == 'doctor' and receiver.role == 'patient')
        ]
        
        if not any(valid_combinations):
            raise HTTPException(
                status_code=403, 
                detail="Only patients and doctors can chat with each other"
            )
        
        return sender, receiver
    
    async def save_file_attachment(self, file: UploadFile, sender_id: int) -> dict:
        """Save uploaded file and return file information"""
        # Validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Validate file type
        if file.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"File type '{file.content_type}' not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
            )
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ''
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create user-specific directory
        user_upload_dir = os.path.join(CHAT_UPLOAD_DIR, f"user_{sender_id}")
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(user_upload_dir, unique_filename)
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        return {
            "filename": file.filename,
            "stored_filename": unique_filename,
            "file_path": file_path,
            "file_size": len(content),
            "content_type": file.content_type
        }
    
    def send_message(
        self, 
        sender_id: int, 
        message_data: ChatMessageCreate, 
        file_info: Optional[dict] = None
    ) -> ChatMessage:
        """Send a new chat message with optional file attachment"""
        # Validate users can chat
        sender, receiver = self.validate_users_can_chat(sender_id, message_data.receiver_id)
        
        # Create message
        chat_message = ChatMessage(
            sender_id=sender_id,
            receiver_id=message_data.receiver_id,
            message_text=message_data.message_text,
            attachment_filename=file_info["filename"] if file_info else None,
            attachment_path=file_info["file_path"] if file_info else None,
            attachment_size=file_info["file_size"] if file_info else None,
            attachment_type=file_info["content_type"] if file_info else None
        )
        
        self.db.add(chat_message)
        self.db.commit()
        self.db.refresh(chat_message)
        
        return chat_message
    
    def get_conversation_history(
        self, 
        user_id: int, 
        other_user_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> ChatHistoryResponse:
        """Get conversation history between two users"""
        # Validate users can chat
        user, other_user = self.validate_users_can_chat(user_id, other_user_id)
        
        # Query messages between the two users
        messages_query = self.db.query(ChatMessage).filter(
            or_(
                and_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == other_user_id),
                and_(ChatMessage.sender_id == other_user_id, ChatMessage.receiver_id == user_id)
            )
        ).order_by(desc(ChatMessage.created_at))
        
        # Get total count
        total_count = messages_query.count()
        
        # Get paginated messages
        messages = messages_query.offset(offset).limit(limit).all()
        
        # Mark messages as read for the current user
        self.mark_messages_as_read(user_id, other_user_id)
        
        return ChatHistoryResponse(
            messages=messages,
            total_count=total_count,
            has_more=total_count > (offset + len(messages))
        )
    
    def mark_messages_as_read(self, user_id: int, sender_id: int):
        """Mark all messages from sender to user as read"""
        unread_messages = self.db.query(ChatMessage).filter(
            and_(
                ChatMessage.receiver_id == user_id,
                ChatMessage.sender_id == sender_id,
                ChatMessage.is_read == 'false'
            )
        ).all()
        
        for message in unread_messages:
            message.is_read = 'true'
        
        self.db.commit()
    
    def get_user_conversations(self, user_id: int) -> List[dict]:
        """Get list of all conversations for a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all unique conversation partners
        sent_to = self.db.query(ChatMessage.receiver_id).filter(ChatMessage.sender_id == user_id).distinct()
        received_from = self.db.query(ChatMessage.sender_id).filter(ChatMessage.receiver_id == user_id).distinct()
        
        # Combine and get unique user IDs
        conversation_partner_ids = set()
        for result in sent_to:
            conversation_partner_ids.add(result[0])
        for result in received_from:
            conversation_partner_ids.add(result[0])
        
        conversations = []
        for partner_id in conversation_partner_ids:
            partner = self.db.query(User).filter(User.id == partner_id).first()
            if partner:
                # Get last message timestamp
                last_message = self.db.query(ChatMessage).filter(
                    or_(
                        and_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == partner_id),
                        and_(ChatMessage.sender_id == partner_id, ChatMessage.receiver_id == user_id)
                    )
                ).order_by(desc(ChatMessage.created_at)).first()
                
                # Count unread messages from this partner
                unread_count = self.db.query(ChatMessage).filter(
                    and_(
                        ChatMessage.sender_id == partner_id,
                        ChatMessage.receiver_id == user_id,
                        ChatMessage.is_read == 'false'
                    )
                ).count()
                
                conversations.append({
                    "user_id": partner.id,
                    "full_name": partner.full_name,
                    "role": partner.role,
                    "last_message_at": last_message.created_at if last_message else None,
                    "unread_count": unread_count
                })
        
        # Sort by last message time (most recent first)
        conversations.sort(key=lambda x: x["last_message_at"] or datetime.min, reverse=True)
        
        return conversations
    
    def get_file_download_path(self, message_id: int, user_id: int) -> str:
        """Get file path for download, ensuring user has access"""
        message = self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Check if user has access to this message
        if user_id not in [message.sender_id, message.receiver_id]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not message.attachment_path:
            raise HTTPException(status_code=404, detail="No attachment found")
        
        if not os.path.exists(message.attachment_path):
            raise HTTPException(status_code=404, detail="File not found on server")
        
        return message.attachment_path
    
    def delete_message(self, message_id: int, user_id: int) -> bool:
        """Delete a message (only sender can delete)"""
        message = self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Only sender can delete their message
        if message.sender_id != user_id:
            raise HTTPException(status_code=403, detail="Only the sender can delete this message")
        
        # Delete file if exists
        if message.attachment_path and os.path.exists(message.attachment_path):
            try:
                os.remove(message.attachment_path)
            except OSError:
                pass  # File deletion failed, but continue with message deletion
        
        self.db.delete(message)
        self.db.commit()
        
        return True 