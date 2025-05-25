import { apiClient, API_ENDPOINTS } from '../config/api';
import { HealthAnalysis, AgentRecommendation, DiseaseHistoryEntry, HealthMetric, MetricsSummary } from '../types';

export const healthService = {
  async getUserAnalyses(): Promise<HealthAnalysis[]> {
    const response = await apiClient.get(API_ENDPOINTS.USER_ANALYSES);
    return response.data;
  },

  async getAgentRecommendations(): Promise<AgentRecommendation[]> {
    const response = await apiClient.get(API_ENDPOINTS.AGENT_RECOMMENDATIONS);
    return response.data;
  },

  async getDiseaseHistory(): Promise<DiseaseHistoryEntry[]> {
    const response = await apiClient.get(API_ENDPOINTS.DISEASE_HISTORY);
    return response.data;
  },

  async triggerAgentAnalysis(data: any): Promise<any> {
    const response = await apiClient.post(API_ENDPOINTS.AGENT_ANALYZE, data);
    return response.data;
  },

  // Helper functions for data processing
  getLatestAnalysis(analyses: HealthAnalysis[]): HealthAnalysis | null {
    if (!analyses.length) return null;
    return analyses.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )[0];
  },

  getHighPriorityRecommendations(recommendations: AgentRecommendation[]): AgentRecommendation[] {
    return recommendations.filter(rec => 
      rec.priority === 'high' || rec.priority === 'urgent'
    ).sort((a, b) => {
      const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  },

  // Enhanced metric processing functions
  getMetricsByStatus(metrics: HealthMetric[]): Record<string, HealthMetric[]> {
    return metrics.reduce((acc, metric) => {
      const status = metric.status;
      if (!acc[status]) acc[status] = [];
      acc[status].push(metric);
      return acc;
    }, {} as Record<string, HealthMetric[]>);
  },

  getAbnormalMetrics(metrics: HealthMetric[]): HealthMetric[] {
    return metrics.filter(metric => metric.status !== 'normal');
  },

  getCriticalMetrics(metrics: HealthMetric[]): HealthMetric[] {
    return metrics.filter(metric => metric.status === 'critical');
  },

  generateMetricsSummary(metrics: HealthMetric[]): MetricsSummary {
    const byStatus = {
      normal: 0,
      low: 0,
      high: 0,
      elevated: 0,
      critical: 0,
    };

    metrics.forEach(metric => {
      if (byStatus.hasOwnProperty(metric.status)) {
        byStatus[metric.status as keyof typeof byStatus]++;
      }
    });

    const urgentAttention = this.getCriticalMetrics(metrics);
    const abnormalCount = metrics.length - byStatus.normal;

    const recommendations = [];
    if (abnormalCount > 0) {
      recommendations.push(`${abnormalCount} metric(s) need attention`);
    }
    if (urgentAttention.length > 0) {
      recommendations.push(`${urgentAttention.length} critical metric(s) require immediate attention`);
    }
    if (byStatus.normal === metrics.length) {
      recommendations.push('All metrics are within normal ranges');
    }

    return {
      total_metrics: metrics.length,
      by_status: byStatus,
      recommendations,
      urgent_attention: urgentAttention,
    };
  },

  getRiskLevelColor(riskLevel: string): string {
    switch (riskLevel) {
      case 'low': return 'text-success-600 bg-success-50 border-success-200';
      case 'medium': return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'high': return 'text-error-600 bg-error-50 border-error-200';
      case 'critical': return 'text-red-800 bg-red-100 border-red-300';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  },

  getPriorityColor(priority: string): string {
    switch (priority) {
      case 'low': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'medium': return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'high': return 'text-error-600 bg-error-50 border-error-200';
      case 'urgent': return 'text-red-800 bg-red-100 border-red-300';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  },

  // New metric status helper functions
  getMetricStatusColor(status: string): string {
    switch (status) {
      case 'normal': 
        return 'text-success-600 bg-success-50 border-success-200';
      case 'low': 
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'high': 
        return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'elevated': 
        return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'critical': 
        return 'text-error-600 bg-error-50 border-error-200';
      default: 
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  },

  getMetricStatusIcon(status: string): string {
    switch (status) {
      case 'normal': return '✓';
      case 'low': return '↓';
      case 'high': return '↑';
      case 'elevated': return '⚡';
      case 'critical': return '⚠️';
      default: return 'ℹ️';
    }
  },

  formatMetricValue(metric: HealthMetric): string {
    return `${metric.value}${metric.unit ? ` ${metric.unit}` : ''}`;
  },
}; 