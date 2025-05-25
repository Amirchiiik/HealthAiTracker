export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'patient' | 'doctor';
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
  role: 'patient' | 'doctor';
}

export interface OCRAnalysis {
  id: string;
  filename: string;
  extracted_text: string;
  metrics: HealthMetric[];
  overall_summary: string;
  analysis: {
    valid: boolean;
    validation_message: string;
  };
  created_at: string;
}

export interface HealthMetric {
  name: string;
  value: number | string;
  unit?: string;
  reference_range?: string;
  status: 'normal' | 'low' | 'high' | 'elevated' | 'critical';
  explanation: string;
}

export interface MetricsAnalysisRequest {
  raw_text: string;
}

export interface MetricsExplanationRequest {
  metrics: {
    name: string;
    value: number | string;
    unit?: string;
    reference_range?: string;
    status: string;
  }[];
}

export interface MetricsSummary {
  total_metrics: number;
  by_status: {
    normal: number;
    low: number;
    high: number;
    elevated: number;
    critical: number;
  };
  recommendations: string[];
  urgent_attention: HealthMetric[];
}

export interface HealthAnalysis {
  id: number;
  user_id: number;
  filename?: string;
  extracted_text?: string;
  metrics?: any[];
  overall_summary?: string;
  analysis_data?: any;
  created_at: string;
}

export interface Appointment {
  id: string;
  patient_id: string;
  doctor_id: string;
  appointment_date: string;
  appointment_time: string;
  status: 'scheduled' | 'completed' | 'cancelled' | 'no_show';
  type: 'consultation' | 'follow_up' | 'emergency';
  notes?: string;
  patient?: User;
  doctor?: User;
  created_at: string;
}

export interface ChatMessage {
  id: number;
  sender_id: number;
  receiver_id: number;
  message_text: string;
  attachment_filename?: string;
  attachment_size?: number;
  attachment_type?: string;
  is_read: boolean;
  created_at: string;
  sender: User;
  receiver: User;
}

export interface ChatConversation {
  id: string;
  participants: User[];
  last_message?: ChatMessage;
  unread_count: number;
  created_at: string;
  updated_at: string;
}

export interface AgentRecommendation {
  id: string;
  user_id: string;
  analysis_id?: string;
  recommendation_type: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'completed' | 'ignored';
  actions_taken?: string[];
  created_at: string;
}

export interface DiseaseHistoryEntry {
  id: string;
  user_id: string;
  predicted_conditions: {
    condition: string;
    probability: number;
    risk_factors: string[];
  }[];
  based_on_analysis: string;
  created_at: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface Language {
  code: 'en' | 'ru';
  name: string;
  flag: string;
}

export interface Theme {
  mode: 'light' | 'dark';
}

// Agent-related types based on backend testing results
export interface AgentAnalysisRequest {
  health_analysis_id: number;
  auto_book_critical?: boolean;
  preferred_datetime?: string;
}

export interface AgentAnalysisSummary {
  total_metrics: number;
  abnormal_metrics: number;
  critical_metrics: number;
  priority_level: 'low' | 'medium' | 'high' | 'critical';
  health_analysis_id: number;
}

export interface SpecialistRecommendation {
  type: string;
  reason: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  metrics_involved: string[];
}

export interface AgentRecommendations {
  recommended_specialists: SpecialistRecommendation[];
  agent_reasoning: string;
  next_steps: string[];
  patient?: User;
  doctor?: User;
}

export interface AgentAction {
  action_type: string;
  description: string;
  timestamp: string;
  success: boolean;
  details?: any;
}

export interface AppointmentBooking {
  appointment_id: string;
  doctor_id: string;
  patient_id: string;
  scheduled_datetime: string;
  appointment_type: string;
  status: string;
  booking_reason: string;
}

export interface IntelligentAgentResponse {
  analysis_summary: AgentAnalysisSummary;
  recommendations: AgentRecommendations;
  actions_taken: AgentAction[];
  appointment_booked?: AppointmentBooking;
  processing_time_ms?: number;
  agent_version?: string;
}

export interface AgentNotification {
  id: string;
  user_id: string;
  type: 'recommendation' | 'appointment_booked' | 'critical_alert' | 'analysis_complete';
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  read: boolean;
  action_url?: string;
  created_at: string;
}

export interface CriticalValueThreshold {
  metric: string;
  critical_threshold: number;
  operator: '>' | '<' | '>=' | '<=';
  specialist: string;
  urgency: 'immediate' | 'urgent' | 'priority';
} 