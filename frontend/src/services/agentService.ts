import { apiClient } from '../config/api';
import { 
  AgentAnalysisRequest, 
  IntelligentAgentResponse, 
  AgentNotification,
  CriticalValueThreshold 
} from '../types';

export const agentService = {
  /**
   * Analyze health data and get AI agent recommendations
   * Based on backend testing results from AGENT_ENDPOINT_TESTING_RESULTS.md
   */
  async analyzeAndAct(request: AgentAnalysisRequest): Promise<IntelligentAgentResponse> {
    try {
      const response = await apiClient.post('/agent/analyze-and-act', request);
      return response.data;
    } catch (error: any) {
      console.error('Agent analysis failed:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Unable to complete intelligent analysis. Please try again later.'
      );
    }
  },

  /**
   * Get agent notifications for the current user
   */
  async getNotifications(): Promise<AgentNotification[]> {
    try {
      const response = await apiClient.get('/agent/notifications');
      return response.data.notifications || [];
    } catch (error: any) {
      console.error('Failed to fetch agent notifications:', error);
      return [];
    }
  },

  /**
   * Mark agent notification as read
   */
  async markNotificationRead(notificationId: string): Promise<void> {
    try {
      await apiClient.put(`/agent/notifications/${notificationId}/read`);
    } catch (error: any) {
      console.error('Failed to mark notification as read:', error);
      throw error;
    }
  },

  /**
   * Get critical value thresholds configuration
   */
  async getCriticalThresholds(): Promise<CriticalValueThreshold[]> {
    try {
      const response = await apiClient.get('/agent/critical-thresholds');
      return response.data.thresholds || this.getDefaultThresholds();
    } catch (error: any) {
      console.warn('Using default critical thresholds:', error);
      return this.getDefaultThresholds();
    }
  },

  /**
   * Default critical value thresholds based on backend configuration
   */
  getDefaultThresholds(): CriticalValueThreshold[] {
    return [
      {
        metric: 'Glucose',
        critical_threshold: 11.0,
        operator: '>',
        specialist: 'Endocrinologist',
        urgency: 'immediate'
      },
      {
        metric: 'ALT',
        critical_threshold: 100,
        operator: '>',
        specialist: 'Gastroenterologist',
        urgency: 'urgent'
      },
      {
        metric: 'AST',
        critical_threshold: 100,
        operator: '>',
        specialist: 'Gastroenterologist',
        urgency: 'urgent'
      },
      {
        metric: 'Creatinine',
        critical_threshold: 150,
        operator: '>',
        specialist: 'Nephrologist',
        urgency: 'urgent'
      },
      {
        metric: 'Hemoglobin',
        critical_threshold: 90,
        operator: '<',
        specialist: 'Hematologist',
        urgency: 'priority'
      },
      {
        metric: 'Platelets',
        critical_threshold: 100,
        operator: '<',
        specialist: 'Hematologist',
        urgency: 'urgent'
      }
    ];
  },

  /**
   * Format priority level for display
   */
  formatPriorityLevel(priority: string): { text: string; color: string; icon: string } {
    switch (priority.toLowerCase()) {
      case 'critical':
        return { text: 'Critical', color: 'text-red-600', icon: '🚨' };
      case 'high':
        return { text: 'High', color: 'text-orange-600', icon: '⚠️' };
      case 'medium':
        return { text: 'Medium', color: 'text-yellow-600', icon: '⚡' };
      case 'low':
        return { text: 'Low', color: 'text-green-600', icon: '✅' };
      default:
        return { text: 'Unknown', color: 'text-gray-600', icon: '❓' };
    }
  },

  /**
   * Format specialist type for display
   */
  formatSpecialistType(type: string): string {
    const specialistMap: { [key: string]: string } = {
      'Gastroenterologist': 'Gastroenterology',
      'Endocrinologist': 'Endocrinology',
      'Nephrologist': 'Nephrology',
      'Hematologist': 'Hematology',
      'Hepatologist': 'Hepatology',
      'Cardiologist': 'Cardiology',
      'Neurologist': 'Neurology',
      'Oncologist': 'Oncology'
    };
    
    return specialistMap[type] || type;
  },

  /**
   * Get specialist icon based on type
   */
  getSpecialistIcon(type: string): string {
    const iconMap: { [key: string]: string } = {
      'Gastroenterologist': '🫃',
      'Endocrinologist': '🩺',
      'Nephrologist': '🫘',
      'Hematologist': '🩸',
      'Hepatologist': '🫀',
      'Cardiologist': '❤️',
      'Neurologist': '🧠',
      'Oncologist': '🎗️'
    };
    
    return iconMap[type] || '👨‍⚕️';
  },

  /**
   * Check if analysis requires immediate attention
   */
  requiresImmediateAttention(response: IntelligentAgentResponse): boolean {
    return (
      response.analysis_summary.priority_level === 'critical' ||
      response.analysis_summary.critical_metrics > 0 ||
      response.appointment_booked !== null
    );
  },

  /**
   * Generate summary text for agent response
   */
  generateSummaryText(response: IntelligentAgentResponse): string {
    const { analysis_summary, recommendations } = response;
    
    if (analysis_summary.priority_level === 'low') {
      return `All ${analysis_summary.total_metrics} health metrics are within normal ranges. Continue regular check-ups.`;
    }
    
    if (analysis_summary.abnormal_metrics > 0) {
      const specialistCount = recommendations.recommended_specialists.length;
      return `${analysis_summary.abnormal_metrics} of ${analysis_summary.total_metrics} metrics need attention. ${specialistCount} specialist${specialistCount !== 1 ? 's' : ''} recommended.`;
    }
    
    return `Analysis complete for ${analysis_summary.total_metrics} health metrics.`;
  }
}; 