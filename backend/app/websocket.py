from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Store active connections: {user_id: websocket}
        self.active_connections: Dict[int, WebSocket] = {}
        # Store user roles for authorization
        self.user_roles: Dict[int, str] = {}

    async def connect(self, websocket: WebSocket, user_id: int, user_role: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_roles[user_id] = user_role
        logger.info(f"User {user_id} ({user_role}) connected to WebSocket")
        
        # Notify other users that this user is online
        await self.broadcast_user_status(user_id, "online")

    def disconnect(self, user_id: int):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_roles:
            del self.user_roles[user_id]
        logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                # Remove broken connection
                self.disconnect(user_id)
                return False
        return False

    async def broadcast_user_status(self, user_id: int, status: str):
        """Broadcast user online/offline status to relevant users"""
        if user_id not in self.user_roles:
            return
            
        user_role = self.user_roles[user_id]
        target_role = "doctor" if user_role == "patient" else "patient"
        
        # Send status update to users of opposite role
        status_message = {
            "type": "user_status",
            "user_id": user_id,
            "status": status
        }
        
        for connected_user_id, role in self.user_roles.items():
            if role == target_role and connected_user_id != user_id:
                await self.send_personal_message(status_message, connected_user_id)

    async def notify_new_message(self, sender_id: int, receiver_id: int, message_data: dict):
        """Notify receiver of a new message"""
        notification = {
            "type": "new_message",
            "sender_id": sender_id,
            "message": message_data
        }
        
        success = await self.send_personal_message(notification, receiver_id)
        if success:
            logger.info(f"Notified user {receiver_id} of new message from {sender_id}")
        else:
            logger.warning(f"Failed to notify user {receiver_id} of new message")

    async def notify_message_read(self, reader_id: int, sender_id: int, message_id: int):
        """Notify sender that their message was read"""
        notification = {
            "type": "message_read",
            "reader_id": reader_id,
            "message_id": message_id
        }
        
        await self.send_personal_message(notification, sender_id)

    def get_online_users(self, for_user_role: str) -> List[int]:
        """Get list of online users that the given role can chat with"""
        target_role = "doctor" if for_user_role == "patient" else "patient"
        return [user_id for user_id, role in self.user_roles.items() if role == target_role]

# Global connection manager instance
manager = ConnectionManager() 