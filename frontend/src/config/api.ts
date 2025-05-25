import axios from 'axios';

// Base API URL - update this to match your backend
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  ME: '/auth/me',
  
  // Upload & OCR - Enhanced with individual explanations
  UPLOAD: '/upload',
  OCR_ANALYSIS: (filename: string) => `/ocr/${filename}/with-explanations`,
  OCR_BASIC: (filename: string) => `/ocr/${filename}`, // Fallback to basic OCR
  
  // Enhanced Analysis endpoints
  ANALYZE_TEXT: '/analysis/text',
  EXPLAIN_METRICS: '/analysis/metrics/explain', 
  METRICS_SUMMARY: '/analysis/summary',
  EXPLAIN_TEXT_METRICS: '/explain/metrics',
  
  // Agent
  AGENT_ANALYZE: '/agent/analyze-and-act',
  AGENT_PROCESS_OCR: '/agent/process-ocr-analysis',
  AGENT_RECOMMENDATIONS: '/agent/my-recommendations',
  
  // Chat
  CHAT_SEND: '/chat/send',
  CHAT_HISTORY: '/chat/history',
  CHAT_CONVERSATIONS: '/users/me/chats',
  
  // Appointments
  APPOINTMENTS: '/appointments',
  DOCTOR_AVAILABILITY: '/appointments/availability',
  
  // Users & Profiles
  USER_ANALYSES: '/users/me/analyses',
  UPDATE_PROFILE: '/users/me/profile',
  
  // Disease predictions
  DISEASE_HISTORY: '/disease/history',
  
  // Doctors (for patients to find)
  DOCTORS: '/users/doctors',
} as const; 