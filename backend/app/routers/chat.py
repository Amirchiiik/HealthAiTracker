from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, Query
from fastapi.responses import FileResponse
from typing import Optional, List
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, ChatMessage
from app.schemas import (
    ChatMessageCreate, 
    ChatMessageResponse, 
    ChatHistoryResponse,
    ChatConversationList,
    ChatParticipant
)
from app.services.chat_service import ChatService
from app.websocket import manager

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/send", response_model=ChatMessageResponse)
async def send_message(
    receiver_id: int = Form(...),
    message_text: str = Form(..., min_length=1, max_length=5000),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to another user with optional file attachment.
    
    - **receiver_id**: ID of the message recipient (must be doctor if sender is patient, or vice versa)
    - **message_text**: Text content of the message (1-5000 characters)
    - **file**: Optional file attachment (max 10MB, medical documents, images, etc.)
    
    Only patients can send to doctors and doctors can send to patients.
    """
    chat_service = ChatService(db)
    
    # Prepare message data
    message_data = ChatMessageCreate(
        receiver_id=receiver_id,
        message_text=message_text
    )
    
    # Handle file upload if provided
    file_info = None
    if file and file.filename:
        try:
            file_info = await chat_service.save_file_attachment(file, current_user.id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")
    
    # Send message
    try:
        message = chat_service.send_message(current_user.id, message_data, file_info)
        
        # Send real-time notification via WebSocket
        await manager.notify_new_message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            message_data={
                "id": message.id,
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "message_text": message.message_text,
                "attachment_filename": message.attachment_filename,
                "attachment_size": message.attachment_size,
                "attachment_type": message.attachment_type,
                "is_read": message.is_read,
                "created_at": message.created_at.isoformat(),
                "sender": {
                    "id": message.sender.id,
                    "full_name": message.sender.full_name,
                    "role": message.sender.role
                }
            }
        )
        
        return message
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send message: {str(e)}")

@router.get("/history", response_model=ChatHistoryResponse)
def get_chat_history(
    with_user: int = Query(..., description="ID of the user to get conversation history with"),
    limit: int = Query(50, ge=1, le=100, description="Number of messages to retrieve"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get conversation history with another user.
    
    - **with_user**: ID of the other user in the conversation
    - **limit**: Number of messages to retrieve (1-100)
    - **offset**: Number of messages to skip for pagination
    
    Messages are returned in descending order (newest first).
    Automatically marks messages as read for the current user.
    """
    chat_service = ChatService(db)
    
    try:
        return chat_service.get_conversation_history(
            user_id=current_user.id,
            other_user_id=with_user,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get chat history: {str(e)}")

@router.get("/conversations", response_model=ChatConversationList)
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all conversations for the current user.
    
    Returns a list of users the current user has had conversations with,
    including unread message counts and last message timestamps.
    Conversations are sorted by most recent activity.
    """
    chat_service = ChatService(db)
    
    try:
        conversations = chat_service.get_user_conversations(current_user.id)
        return ChatConversationList(conversations=conversations)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get conversations: {str(e)}")

@router.get("/download/{message_id}")
def download_attachment(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download file attachment from a message.
    
    - **message_id**: ID of the message containing the attachment
    
    Only the sender or receiver of the message can download the attachment.
    """
    chat_service = ChatService(db)
    
    try:
        file_path = chat_service.get_file_download_path(message_id, current_user.id)
        
        # Get the message to get original filename
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message or not message.attachment_filename:
            raise HTTPException(status_code=404, detail="Attachment not found")
        
        return FileResponse(
            path=file_path,
            filename=message.attachment_filename,
            media_type='application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.delete("/message/{message_id}")
def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a message (only the sender can delete their own messages).
    
    - **message_id**: ID of the message to delete
    
    This will also delete any file attachment associated with the message.
    """
    chat_service = ChatService(db)
    
    try:
        success = chat_service.delete_message(message_id, current_user.id)
        if success:
            return {"message": "Message deleted successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete message")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.put("/mark-read/{other_user_id}")
async def mark_conversation_read(
    other_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all messages from another user as read.
    
    - **other_user_id**: ID of the user whose messages should be marked as read
    """
    chat_service = ChatService(db)
    
    try:
        # Validate users can chat
        chat_service.validate_users_can_chat(current_user.id, other_user_id)
        
        # Mark messages as read
        marked_messages = chat_service.mark_messages_as_read(current_user.id, other_user_id)
        
        # Send WebSocket notification for each marked message
        for message_id in marked_messages:
            await manager.notify_message_read(
                reader_id=current_user.id,
                sender_id=other_user_id,
                message_id=message_id
            )
        
        return {"message": "Messages marked as read"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to mark messages as read: {str(e)}")

@router.get("/users", response_model=List[ChatParticipant])
def get_available_chat_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of users available for chatting.
    
    - Patients can see all doctors
    - Doctors can see all patients
    
    Does not include users the current user has already chatted with.
    """
    try:
        if current_user.role == 'patient':
            # Patients can chat with doctors
            available_users = db.query(User).filter(User.role == 'doctor', User.id != current_user.id).all()
        elif current_user.role == 'doctor':
            # Doctors can chat with patients
            available_users = db.query(User).filter(User.role == 'patient', User.id != current_user.id).all()
        else:
            raise HTTPException(status_code=403, detail="Invalid user role for chat")
        
        # Convert to ChatParticipant format
        participants = []
        for user in available_users:
            participants.append(ChatParticipant(
                user_id=user.id,
                full_name=user.full_name,
                role=user.role,
                last_message_at=None,
                unread_count=0
            ))
        
        return participants
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get available users: {str(e)}") 