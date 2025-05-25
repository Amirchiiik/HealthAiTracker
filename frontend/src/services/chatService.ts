import { apiClient, API_ENDPOINTS } from '../config/api';
import { ChatMessage, User } from '../types';

export interface ChatConversation {
  user_id: number;
  full_name: string;
  role: string;
  last_message_at?: string;
  unread_count: number;
}

export interface ChatHistoryResponse {
  messages: ChatMessage[];
  total_count: number;
  has_more: boolean;
}

export interface SendMessageRequest {
  receiver_id: number;
  message_text: string;
  file?: File;
}

export const chatService = {
  async getConversations(): Promise<ChatConversation[]> {
    const response = await apiClient.get('/chat/conversations');
    return response.data.conversations;
  },

  async getChatHistory(userId: number, limit = 50, offset = 0): Promise<ChatHistoryResponse> {
    const response = await apiClient.get('/chat/history', {
      params: {
        with_user: userId,
        limit,
        offset
      }
    });
    return response.data;
  },

  async sendMessage(data: SendMessageRequest): Promise<ChatMessage> {
    const formData = new FormData();
    formData.append('receiver_id', data.receiver_id.toString());
    formData.append('message_text', data.message_text);
    
    if (data.file) {
      formData.append('file', data.file);
    }

    const response = await apiClient.post('/chat/send', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async markAsRead(otherUserId: number): Promise<void> {
    await apiClient.put(`/chat/mark-read/${otherUserId}`);
  },

  async deleteMessage(messageId: number): Promise<void> {
    await apiClient.delete(`/chat/message/${messageId}`);
  },

  async getAvailableUsers(): Promise<User[]> {
    const response = await apiClient.get('/chat/users');
    return response.data;
  },

  async downloadAttachment(messageId: number): Promise<Blob> {
    const response = await apiClient.get(`/chat/download/${messageId}`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Helper functions for real-time updates (will be enhanced later)
  onNewMessage(callback: (message: ChatMessage) => void) {
    // Placeholder for WebSocket integration
    console.log('Real-time messaging will be added later');
  },

  onUserStatusChange(callback: (userId: number, isOnline: boolean) => void) {
    // Placeholder for WebSocket integration
    console.log('User status updates will be added later');
  },

  formatMessageTime(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 48) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString();
    }
  },

  getMessageStatusIcon(isRead: boolean, isSent: boolean): string {
    if (!isSent) return '⏳'; // Sending
    if (isRead) return '✓✓'; // Read
    return '✓'; // Delivered
  }
}; 