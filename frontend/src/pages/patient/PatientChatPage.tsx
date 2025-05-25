import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  MessageCircle,
  Send,
  Paperclip,
  Image,
  FileText,
  Camera,
  Mic,
  Search,
  Phone,
  Video,
  Info,
  X,
  Download,
  Upload,
  Plus,
  AlertCircle,
  Clock,
  CheckCircle,
  User as UserIcon,
  Stethoscope,
  Heart,
  Activity,
  HelpCircle,
  Star,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import Navigation from '../../components/layout/Navigation';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';
import { useWebSocket } from '../../hooks/useWebSocket';
import { chatService } from '../../services/chatService';

interface Doctor {
  id: number;
  full_name: string;
  specialization?: string;
  rating?: number;
  availability: 'online' | 'offline' | 'busy';
  last_seen?: string;
}

interface ChatMessage {
  id: number;
  sender_id: number;
  receiver_id: number;
  message_text: string;
  attachment_filename?: string;
  attachment_type?: string;
  attachment_url?: string;
  is_read: boolean;
  created_at: string;
  message_type?: 'text' | 'image' | 'file' | 'audio' | 'question';
}

const PatientChatPage: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const { isConnected } = useWebSocket();
  const [selectedDoctor, setSelectedDoctor] = useState<number | null>(null);
  const [messageText, setMessageText] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [showQuestionTemplates, setShowQuestionTemplates] = useState(false);
  const [messageType, setMessageType] = useState<'text' | 'question' | 'urgent'>('text');
  const [searchTerm, setSearchTerm] = useState('');
  const [demoMode, setDemoMode] = useState(true);
  const [demoMessages, setDemoMessages] = useState<any[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropZoneRef = useRef<HTMLDivElement>(null);

  // Quick question templates for patients
  const questionTemplates = [
    "I'm experiencing symptoms and would like to discuss them",
    "I have questions about my medication",
    "I need to schedule a follow-up appointment",
    "I'd like to share my test results",
    "I'm having side effects from treatment",
    "I need medical advice for my condition",
    "I want to discuss my lab results",
    "I have concerns about my symptoms"
  ];

  // Fetch available doctors
  const { data: doctors, isLoading: doctorsLoading } = useQuery({
    queryKey: ['available-doctors'],
    queryFn: async (): Promise<Doctor[]> => {
      if (demoMode) {
        // Demo data - showcasing the interface
        return [
          {
            id: 1,
            full_name: 'Dr. Amina Johnson',
            specialization: 'General Practice',
            rating: 4.8,
            availability: 'online',
            last_seen: new Date().toISOString()
          },
          {
            id: 2,
            full_name: 'Dr. Michael Chen',
            specialization: 'Cardiology',
            rating: 4.9,
            availability: 'online',
            last_seen: new Date().toISOString()
          },
          {
            id: 3,
            full_name: 'Dr. Sarah Williams',
            specialization: 'Internal Medicine',
            rating: 4.7,
            availability: 'busy',
            last_seen: '2024-01-15T10:30:00Z'
          }
        ];
      }
      // Real API call would go here
      return [];
    }
  });

  // Fetch chat history
  const { data: chatHistory, isLoading: messagesLoading } = useQuery({
    queryKey: ['patient-chat-history', selectedDoctor],
    queryFn: () => {
      if (demoMode && selectedDoctor) {
        return {
          messages: demoMessages,
          total_count: demoMessages.length,
          has_more: false
        };
      }
      // Real API call: return selectedDoctor ? chatService.getChatHistory(selectedDoctor) : null;
      return { messages: [], total_count: 0, has_more: false };
    },
    enabled: !!selectedDoctor,
    refetchInterval: demoMode ? undefined : 5000
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (data: any) => {
      if (demoMode) {
        // Demo function
        const newMessage = {
          id: Date.now(),
          sender_id: user?.id || 1,
          receiver_id: data.receiver_id,
          message_text: data.message_text,
          attachment_filename: data.files?.[0]?.name || null,
          attachment_type: data.files?.[0]?.type || null,
          is_read: false,
          created_at: new Date().toISOString()
        };
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Add message to demo messages
        setDemoMessages(prev => [...prev, newMessage]);
        
        return newMessage;
      } else {
        // Real API function
        return chatService.sendMessage(data);
      }
    },
    onSuccess: () => {
      setMessageText('');
      setSelectedFiles([]);
      setMessageType('text');
      if (!demoMode) {
        queryClient.invalidateQueries({ queryKey: ['patient-chat-history'] });
      }
      scrollToBottom();
    },
    onError: (error) => {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
    }
  });

  // Handle file upload
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    addFiles(files);
  };

  const addFiles = (files: File[]) => {
    const validFiles = files.filter(file => {
      if (file.size > 10 * 1024 * 1024) {
        alert(`File ${file.name} is too large. Maximum size is 10MB.`);
        return false;
      }
      return true;
    });

    setSelectedFiles(prev => [...prev, ...validFiles].slice(0, 5)); // Max 5 files
  };

  // Drag and drop handlers
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    if (!dropZoneRef.current?.contains(e.relatedTarget as Node)) {
      setIsDragOver(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
  };

  // Send message
  const handleSendMessage = () => {
    if ((!messageText.trim() && selectedFiles.length === 0) || !selectedDoctor) return;

    const messageData = {
      receiver_id: selectedDoctor,
      message_text: messageText.trim(),
      files: selectedFiles,
      message_type: messageType
    };

    sendMessageMutation.mutate(messageData);
  };

  // Use question template
  const selectQuestionTemplate = (template: string) => {
    setMessageText(template);
    setMessageType('question');
    setShowQuestionTemplates(false);
  };

  // Remove file
  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory?.messages]);

  // Get selected doctor details
  const selectedDoctorDetails = doctors?.find(doc => doc.id === selectedDoctor);

  // Filter doctors based on search
  const filteredDoctors = doctors?.filter(doctor =>
    doctor.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doctor.specialization?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const getAvailabilityColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'busy': return 'bg-yellow-500';
      case 'offline': return 'bg-gray-400';
      default: return 'bg-gray-400';
    }
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return <Image className="w-4 h-4" />;
    if (file.type.includes('pdf')) return <FileText className="w-4 h-4 text-red-500" />;
    return <FileText className="w-4 h-4" />;
  };

  // Add demo doctor response after patient sends message
  useEffect(() => {
    if (demoMode && demoMessages.length > 0) {
      const lastMessage = demoMessages[demoMessages.length - 1];
      if (lastMessage.sender_id === (user?.id || 1)) {
        // Add doctor response after delay
        setTimeout(() => {
          const doctorResponse = {
            id: Date.now() + 1,
            sender_id: selectedDoctor || 2,
            receiver_id: user?.id || 1,
            message_text: getDemoResponse(lastMessage.message_text, messageType),
            attachment_filename: null,
            attachment_type: null,
            is_read: false,
            created_at: new Date().toISOString()
          };
          setDemoMessages(prev => [...prev, doctorResponse]);
        }, 2000);
      }
    }
  }, [demoMessages, selectedDoctor, user?.id, messageType, demoMode]);

  // Demo response generator
  const getDemoResponse = (patientMessage: string, type: string) => {
    const responses = {
      question: [
        "Thank you for your question. Based on what you've described, I'd recommend scheduling an in-person consultation to better assess your condition.",
        "I understand your concern. Let me review your symptoms and medical history. Can you provide more details about when this started?",
        "This is a common concern among my patients. Let me explain what might be happening and our next steps."
      ],
      urgent: [
        "I've received your urgent message. Please call our emergency line at (555) 123-4567 immediately if this is a medical emergency.",
        "Thank you for marking this as urgent. I'm reviewing your message now and will respond within the next hour.",
        "I see this is marked urgent. If you're experiencing severe symptoms, please go to the nearest emergency room."
      ],
      text: [
        "Thank you for your message. I've reviewed the information you provided and will get back to you with recommendations.",
        "I appreciate you sharing this information. Let me review your case and provide you with a detailed response.",
        "Thank you for the update. I'll incorporate this into your treatment plan and follow up with you soon."
      ]
    };
    
    const typeResponses = responses[type as keyof typeof responses] || responses.text;
    return typeResponses[Math.floor(Math.random() * typeResponses.length)];
  };

  return (
    <Navigation>
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        
        {/* Doctors Sidebar */}
        <div className="w-1/3 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
              <Stethoscope className="w-6 h-6 mr-2 text-blue-600" />
              Medical Chat
              <div className={`ml-2 w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            </h1>
            
            {/* Demo Mode Toggle */}
            <div className="mt-2 flex items-center space-x-2">
              <button
                onClick={() => setDemoMode(!demoMode)}
                className={`px-2 py-1 text-xs rounded-full ${
                  demoMode ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}
              >
                {demoMode ? '🎭 Demo Mode' : '🔗 Live Mode'}
              </button>
              {demoMode && (
                <span className="text-xs text-gray-500">
                  Showcasing interface features
                </span>
              )}
            </div>
            
            {/* Search Doctors */}
            <div className="mt-4 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search doctors..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          {/* Doctors List */}
          <div className="overflow-y-auto h-full">
            {doctorsLoading ? (
              <div className="p-4 text-center">
                <LoadingSpinner size="sm" />
                <p className="text-sm text-gray-500 mt-2">Loading doctors...</p>
              </div>
            ) : filteredDoctors.length === 0 ? (
              <div className="p-4 text-center">
                <Stethoscope className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500 dark:text-gray-400">No doctors available</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredDoctors.map((doctor) => (
                  <div
                    key={doctor.id}
                    onClick={() => setSelectedDoctor(doctor.id)}
                    className={`p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                      selectedDoctor === doctor.id ? 'bg-blue-50 dark:bg-blue-900/20 border-r-4 border-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="relative">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-green-500 rounded-full flex items-center justify-center">
                          <Stethoscope className="w-6 h-6 text-white" />
                        </div>
                        <div className={`absolute bottom-0 right-0 w-3 h-3 border-2 border-white rounded-full ${getAvailabilityColor(doctor.availability)}`} />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-gray-900 dark:text-white truncate">
                          {doctor.full_name}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                          {doctor.specialization}
                        </p>
                        <div className="flex items-center mt-1">
                          <div className="flex items-center">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                className={`w-3 h-3 ${
                                  i < Math.floor(doctor.rating || 0)
                                    ? 'text-yellow-400 fill-current'
                                    : 'text-gray-300'
                                }`}
                              />
                            ))}
                            <span className="text-xs text-gray-500 ml-1">{doctor.rating}</span>
                          </div>
                          <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${
                            doctor.availability === 'online' ? 'bg-green-100 text-green-800' :
                            doctor.availability === 'busy' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {doctor.availability}
                          </span>
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
          {selectedDoctor ? (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-green-500 rounded-full flex items-center justify-center">
                      <Stethoscope className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h2 className="font-semibold text-gray-900 dark:text-white">
                        {selectedDoctorDetails?.full_name}
                      </h2>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {selectedDoctorDetails?.specialization} • {selectedDoctorDetails?.availability}
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
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors">
                      <Info className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Messages Area */}
              <div 
                ref={dropZoneRef}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                className={`flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900 relative ${
                  isDragOver ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                }`}
              >
                {isDragOver && (
                  <div className="absolute inset-0 bg-blue-500/10 border-2 border-dashed border-blue-500 rounded-lg flex items-center justify-center z-10">
                    <div className="text-center">
                      <Upload className="w-12 h-12 text-blue-500 mx-auto mb-2" />
                      <p className="text-blue-600 font-medium">Drop files here to share with doctor</p>
                    </div>
                  </div>
                )}
                
                {messagesLoading ? (
                  <div className="flex justify-center items-center h-full">
                    <LoadingSpinner size="lg" />
                  </div>
                ) : chatHistory?.messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <Heart className="w-16 h-16 text-blue-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      Start your medical consultation
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400 mb-4">
                      Ask questions, share symptoms, or upload medical files
                    </p>
                    <button
                      onClick={() => setShowQuestionTemplates(!showQuestionTemplates)}
                      className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
                    >
                      <HelpCircle className="w-4 h-4" />
                      <span>Quick Questions</span>
                    </button>
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
                        {/* Message Type Indicator */}
                        {(message as any).message_type === 'question' && (
                          <div className="flex items-center space-x-1 mb-1">
                            <HelpCircle className="w-3 h-3" />
                            <span className="text-xs opacity-75">Question</span>
                          </div>
                        )}
                        
                        <p className="whitespace-pre-wrap">{message.message_text}</p>
                        
                        {/* File Attachment */}
                        {message.attachment_filename && (
                          <div className="mt-2 p-2 bg-black/10 rounded border">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                {message.attachment_type?.startsWith('image/') ? (
                                  <Image className="w-4 h-4" />
                                ) : (
                                  <FileText className="w-4 h-4" />
                                )}
                                <span className="text-sm">{message.attachment_filename}</span>
                              </div>
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
                            <div className="flex items-center space-x-1">
                              {message.is_read ? (
                                <CheckCircle className="w-3 h-3" />
                              ) : (
                                <Clock className="w-3 h-3" />
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input Area */}
              <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                
                {/* Question Templates */}
                {showQuestionTemplates && (
                  <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">Quick Questions</h4>
                      <button
                        onClick={() => setShowQuestionTemplates(false)}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="grid grid-cols-1 gap-2">
                      {questionTemplates.map((template, index) => (
                        <button
                          key={index}
                          onClick={() => selectQuestionTemplate(template)}
                          className="text-left p-2 hover:bg-blue-100 dark:hover:bg-blue-800 rounded text-sm text-gray-700 dark:text-gray-300"
                        >
                          {template}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* File Previews */}
                {selectedFiles.length > 0 && (
                  <div className="mb-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Files to Send ({selectedFiles.length}/5)
                    </h4>
                    <div className="space-y-2">
                      {selectedFiles.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-white dark:bg-gray-600 rounded border">
                          <div className="flex items-center space-x-2">
                            {getFileIcon(file)}
                            <span className="text-sm text-gray-700 dark:text-gray-300">{file.name}</span>
                            <span className="text-xs text-gray-500">
                              ({Math.round(file.size / 1024)} KB)
                            </span>
                          </div>
                          <button 
                            onClick={() => removeFile(index)}
                            className="p-1 hover:bg-gray-200 dark:hover:bg-gray-500 rounded"
                          >
                            <X className="w-4 h-4 text-gray-500" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Message Type Selector */}
                <div className="flex items-center space-x-2 mb-3">
                  <button
                    onClick={() => setMessageType('text')}
                    className={`px-3 py-1 rounded-full text-xs ${
                      messageType === 'text' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    Message
                  </button>
                  <button
                    onClick={() => setMessageType('question')}
                    className={`px-3 py-1 rounded-full text-xs ${
                      messageType === 'question' ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    Question
                  </button>
                  <button
                    onClick={() => setMessageType('urgent')}
                    className={`px-3 py-1 rounded-full text-xs ${
                      messageType === 'urgent' ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    Urgent
                  </button>
                </div>
                
                {/* Input Area */}
                <div className="flex items-end space-x-2">
                  {/* File Upload Button */}
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    onChange={handleFileSelect}
                    className="hidden"
                    accept="image/*,.pdf,.doc,.docx,.txt"
                  />
                  
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                    title="Upload files"
                  >
                    <Paperclip className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </button>

                  {/* Quick Questions Button */}
                  <button
                    onClick={() => setShowQuestionTemplates(!showQuestionTemplates)}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                    title="Quick questions"
                  >
                    <HelpCircle className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </button>
                  
                  {/* Message Input */}
                  <div className="flex-1 relative">
                    <textarea
                      value={messageText}
                      onChange={(e) => setMessageText(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      placeholder="Type your message, ask a question, or describe your symptoms..."
                      rows={1}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>
                  
                  {/* Send Button */}
                  <button
                    onClick={handleSendMessage}
                    disabled={(!messageText.trim() && selectedFiles.length === 0) || sendMessageMutation.isPending}
                    className={`p-2 rounded-full transition-colors ${
                      messageType === 'urgent' ? 'bg-red-500 hover:bg-red-600' :
                      messageType === 'question' ? 'bg-green-500 hover:bg-green-600' :
                      'bg-blue-500 hover:bg-blue-600'
                    } disabled:bg-gray-300 disabled:cursor-not-allowed`}
                  >
                    {sendMessageMutation.isPending ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <Send className="w-5 h-5 text-white" />
                    )}
                  </button>
                </div>
                
                {/* Help Text */}
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  💡 Drag & drop files, use quick questions, or type your message. 
                  {selectedFiles.length > 0 && ` ${selectedFiles.length} file(s) ready to send.`}
                </p>
              </div>
            </>
          ) : (
            /* No Doctor Selected */
            <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
              <div className="text-center max-w-md">
                <Heart className="w-20 h-20 text-blue-400 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Welcome to Medical Chat
                </h2>
                <p className="text-gray-500 dark:text-gray-400 mb-6">
                  Select a doctor to start your medical consultation
                </p>
                
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-2">You can:</h3>
                  <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1 text-left">
                    <li>📋 Ask medical questions</li>
                    <li>📎 Share medical files & images</li>
                    <li>💊 Discuss medications & symptoms</li>
                    <li>📅 Schedule appointments</li>
                    <li>🔔 Get urgent medical advice</li>
                  </ul>
                  
                  {demoMode && (
                    <div className="mt-3 p-2 bg-green-50 dark:bg-green-900/20 rounded border border-green-200">
                      <p className="text-xs text-green-700 dark:text-green-300 font-medium">
                        🎭 Demo Mode Active: Select a doctor above and try sending messages, files, or questions!
                        Doctors will respond automatically to showcase the interface.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Navigation>
  );
};

export default PatientChatPage; 