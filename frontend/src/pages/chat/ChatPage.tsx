import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  MessageCircle,
  Send,
  Paperclip,
  Search,
  MoreVertical,
  Download,
  Trash2,
  Check,
  CheckCheck,
  Clock,
  User as UserIcon,
  Phone,
  Video,
  Info,
  X,
  Image,
  FileText,
  Smile
} from 'lucide-react';
import Navigation from '../../components/layout/Navigation';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';
import { useWebSocket } from '../../hooks/useWebSocket';
import { chatService, ChatConversation } from '../../services/chatService';
import { ChatMessage, User } from '../../types';

const ChatPage: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const { isConnected, lastMessage } = useWebSocket();
  const [selectedConversation, setSelectedConversation] = useState<number | null>(null);
  const [messageText, setMessageText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showUserInfo, setShowUserInfo] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState<number[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch conversations
  const { data: conversations, isLoading: conversationsLoading } = useQuery({
    queryKey: ['chat-conversations'],
    queryFn: chatService.getConversations,
    refetchInterval: 30000, // Refetch every 30 seconds for new messages
  });

  // Fetch available users for new conversations
  const { data: availableUsers } = useQuery({
    queryKey: ['chat-users'],
    queryFn: chatService.getAvailableUsers,
  });

  // Fetch chat history for selected conversation
  const { data: chatHistory, isLoading: messagesLoading } = useQuery({
    queryKey: ['chat-history', selectedConversation],
    queryFn: () => selectedConversation ? chatService.getChatHistory(selectedConversation) : null,
    enabled: !!selectedConversation,
    refetchInterval: 5000, // Refetch every 5 seconds for real-time effect
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: chatService.sendMessage,
    onSuccess: () => {
      setMessageText('');
      setSelectedFile(null);
      queryClient.invalidateQueries({ queryKey: ['chat-history'] });
      queryClient.invalidateQueries({ queryKey: ['chat-conversations'] });
      scrollToBottom();
    },
    onError: (error) => {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
    }
  });

  // Mark as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: chatService.markAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-conversations'] });
    }
  });

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Auto-scroll when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [chatHistory?.messages]);

  // Mark conversation as read when opened
  useEffect(() => {
    if (selectedConversation) {
      markAsReadMutation.mutate(selectedConversation);
    }
  }, [selectedConversation]);

  // Debug: Log when selectedConversation changes
  useEffect(() => {
    console.log('🎯 selectedConversation changed to:', selectedConversation);
  }, [selectedConversation]);

  // Handle send message
  const handleSendMessage = () => {
    if ((!messageText.trim() && !selectedFile) || !selectedConversation) return;

    sendMessageMutation.mutate({
      receiver_id: selectedConversation,
      message_text: messageText.trim(),
      file: selectedFile || undefined
    });
  };

  // Handle file selection
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        alert('File size must be less than 10MB');
        return;
      }
      setSelectedFile(file);
    }
  };

  // Handle key press in message input
  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  // Get selected user details
  const selectedUser = conversations?.find(conv => conv.user_id === selectedConversation);

  // Filter conversations based on search
  const filteredConversations = conversations?.filter(conv =>
    conv.full_name.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      console.log('🔔 Received WebSocket message:', lastMessage);
      
      switch (lastMessage.type) {
        case 'new_message':
          const messageData = lastMessage.message;
          const senderId = lastMessage.sender_id;
          const receiverId = messageData?.receiver_id;
          
          console.log('📨 New message:', { senderId, receiverId, currentUserId: user?.id });
          
          // Only update if this message involves the current user
          if (user && (senderId === user.id || receiverId === user.id)) {
            console.log('✅ Message is for current user, updating UI');
            
            // Only invalidate the specific conversation's chat history
            if (selectedConversation && (senderId === selectedConversation || receiverId === selectedConversation)) {
              queryClient.invalidateQueries({ 
                queryKey: ['chat-history', selectedConversation] 
              });
            }
            
            // Always update conversations list to show new unread count
            queryClient.invalidateQueries({ queryKey: ['chat-conversations'] });
            
            // Auto-scroll to bottom if this is the current conversation
            if (selectedConversation && (senderId === selectedConversation || receiverId === selectedConversation)) {
              setTimeout(scrollToBottom, 100);
            }
          } else {
            console.log('❌ Message is not for current user, ignoring');
          }
          break;
          
        case 'message_read':
          // Only update if this involves the current user
          if (user && (lastMessage.reader_id === user.id || 
                     (selectedConversation && lastMessage.reader_id === selectedConversation))) {
            queryClient.invalidateQueries({ 
              queryKey: ['chat-history', selectedConversation] 
            });
          }
          break;
          
        case 'user_status':
          // Update online users list
          if (lastMessage.status === 'online') {
            setOnlineUsers(prev => [...prev.filter(id => id !== lastMessage.user_id), lastMessage.user_id]);
          } else {
            setOnlineUsers(prev => prev.filter(id => id !== lastMessage.user_id));
          }
          break;
          
        default:
          console.log('📥 Unknown WebSocket message type:', lastMessage.type);
      }
    }
  }, [lastMessage, queryClient, user, selectedConversation]);

  return (
    <Navigation>
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        {/* Conversations Sidebar */}
        <div className="w-1/3 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
              <MessageCircle className="w-6 h-6 mr-2" />
              Messages
              {/* WebSocket Status Indicator */}
              <div className={`ml-2 w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} 
                   title={isConnected ? 'Connected' : 'Disconnected'}>
              </div>
            </h1>
            
            {/* Search */}
            <div className="mt-4 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search conversations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          {/* Conversations List */}
          <div className="overflow-y-auto h-full">
            {conversationsLoading ? (
              <div className="p-4 text-center">
                <LoadingSpinner size="sm" />
                <p className="text-sm text-gray-500 mt-2">Loading conversations...</p>
              </div>
            ) : filteredConversations.length === 0 ? (
              <div className="p-4 text-center">
                <MessageCircle className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500 dark:text-gray-400">No conversations yet</p>
                <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
                  Start a conversation with a {user?.role === 'patient' ? 'doctor' : 'patient'}
                </p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredConversations.map((conversation) => (
                  <div
                    key={conversation.user_id}
                    onClick={() => setSelectedConversation(conversation.user_id)}
                    className={`p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                      selectedConversation === conversation.user_id ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="relative">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                          <UserIcon className="w-6 h-6 text-white" />
                        </div>
                        {/* Online indicator */}
                        <div className={`absolute bottom-0 right-0 w-3 h-3 border-2 border-white dark:border-gray-800 rounded-full ${
                          onlineUsers.includes(conversation.user_id) ? 'bg-green-500' : 'bg-gray-400'
                        }`}></div>
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h3 className="font-medium text-gray-900 dark:text-white truncate">
                            {conversation.full_name}
                          </h3>
                          {conversation.last_message_at && (
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {chatService.formatMessageTime(conversation.last_message_at)}
                            </span>
                          )}
                        </div>
                        
                        <div className="flex items-center justify-between mt-1">
                          <span className="text-sm text-gray-600 dark:text-gray-300 capitalize">
                            {conversation.role}
                          </span>
                          {conversation.unread_count > 0 && (
                            <span className="bg-blue-500 text-white text-xs rounded-full px-2 py-0.5 min-w-[20px] text-center">
                              {conversation.unread_count}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {selectedConversation ? (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <UserIcon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h2 className="font-semibold text-gray-900 dark:text-white">
                        {selectedUser?.full_name}
                      </h2>
                      <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">
                        {selectedUser?.role} • Online
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors">
                      <Phone className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    </button>
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors">
                      <Video className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    </button>
                    <button 
                      onClick={() => setShowUserInfo(!showUserInfo)}
                      className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                    >
                      <Info className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
                {messagesLoading ? (
                  <div className="flex justify-center items-center h-full">
                    <LoadingSpinner size="lg" />
                  </div>
                ) : chatHistory?.messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <MessageCircle className="w-16 h-16 text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      No messages yet
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400">
                      Start the conversation by sending a message below
                    </p>
                  </div>
                ) : (
                  chatHistory?.messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.sender_id === user?.id
                          ? 'bg-blue-500 text-white'
                          : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
                      }`}>
                        {/* Message Text */}
                        <p className="whitespace-pre-wrap">{message.message_text}</p>
                        
                        {/* File Attachment */}
                        {message.attachment_filename && (
                          <div className="mt-2 p-2 bg-black/10 rounded border">
                            <div className="flex items-center space-x-2">
                              {message.attachment_type?.startsWith('image/') ? (
                                <Image className="w-4 h-4" />
                              ) : (
                                <FileText className="w-4 h-4" />
                              )}
                              <span className="text-sm">{message.attachment_filename}</span>
                              <button 
                                onClick={() => chatService.downloadAttachment(message.id)}
                                className="p-1 hover:bg-black/10 rounded"
                              >
                                <Download className="w-3 h-3" />
                              </button>
                            </div>
                          </div>
                        )}
                        
                        {/* Message Status & Time */}
                        <div className={`flex items-center justify-between mt-2 text-xs ${
                          message.sender_id === user?.id ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
                        }`}>
                          <span>{chatService.formatMessageTime(message.created_at)}</span>
                          {message.sender_id === user?.id && (
                            <span className="ml-2">
                              {message.is_read ? <CheckCheck className="w-3 h-3" /> : <Check className="w-3 h-3" />}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                {/* File Preview */}
                {selectedFile && (
                  <div className="mb-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <FileText className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">{selectedFile.name}</span>
                      <span className="text-xs text-gray-500">
                        ({Math.round(selectedFile.size / 1024)} KB)
                      </span>
                    </div>
                    <button 
                      onClick={() => setSelectedFile(null)}
                      className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                    >
                      <X className="w-4 h-4 text-gray-500" />
                    </button>
                  </div>
                )}
                
                <div className="flex items-end space-x-2">
                  {/* File Input */}
                  <input
                    ref={fileInputRef}
                    type="file"
                    onChange={handleFileSelect}
                    className="hidden"
                    accept="image/*,.pdf,.doc,.docx,.txt"
                  />
                  
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                  >
                    <Paperclip className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </button>
                  
                  {/* Message Input */}
                  <div className="flex-1 relative">
                    <textarea
                      value={messageText}
                      onChange={(e) => setMessageText(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type your message..."
                      rows={1}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>
                  
                  {/* Send Button */}
                  <button
                    onClick={handleSendMessage}
                    disabled={(!messageText.trim() && !selectedFile) || sendMessageMutation.isPending}
                    className="p-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed rounded-full transition-colors"
                  >
                    {sendMessageMutation.isPending ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <Send className="w-5 h-5 text-white" />
                    )}
                  </button>
                </div>
              </div>
            </>
          ) : (
            /* No Conversation Selected */
            <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
              <div className="text-center">
                <MessageCircle className="w-20 h-20 text-gray-400 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Welcome to Medical Chat
                </h2>
                <p className="text-gray-500 dark:text-gray-400 mb-6">
                  Select a conversation to start messaging with healthcare professionals
                </p>
                
                {/* Debug Info */}
                <div className="text-xs text-gray-400 mb-4 p-2 bg-gray-100 dark:bg-gray-800 rounded">
                  <p>Current user: {user?.full_name} ({user?.role})</p>
                  <p>Available users: {availableUsers?.length || 0}</p>
                  <p>WebSocket: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}</p>
                </div>
                
                {availableUsers && availableUsers.length > 0 && (
                  <div className="max-w-md mx-auto">
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Start a new conversation:
                    </h3>
                    <div className="space-y-2">
                      {availableUsers.slice(0, 3).map((availableUser) => (
                        <div key={availableUser.id} className="w-full">
                          <button
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              console.log('🔥 BUTTON CLICKED!');
                              console.log('User:', availableUser.full_name);
                              console.log('ID:', availableUser.id);
                              console.log('Role:', availableUser.role);
                              alert(`Clicked on ${availableUser.full_name}!`);
                              setSelectedConversation(availableUser.id);
                            }}
                            style={{ 
                              zIndex: 1000,
                              position: 'relative',
                              pointerEvents: 'auto',
                              cursor: 'pointer'
                            }}
                            className="w-full p-3 border-2 border-blue-300 bg-white hover:bg-blue-50 rounded-lg transition-colors text-left shadow-md"
                          >
                            <div className="flex items-center space-x-3">
                              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                                <UserIcon className="w-4 h-4 text-white" />
                              </div>
                              <div>
                                <p className="font-medium text-gray-900">
                                  ✨ {availableUser.full_name} ✨
                                </p>
                                <p className="text-sm text-blue-600 font-semibold uppercase">
                                  Click to Chat → {availableUser.role}
                                </p>
                              </div>
                            </div>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </Navigation>
  );
};

export default ChatPage; 