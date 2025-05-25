import { agentService } from './agentService';
import { healthService } from './healthService';
import { HealthMetric, IntelligentAgentResponse, HealthAnalysis } from '../types';

export interface CriticalAnalysisResult {
  hasCriticalValues: boolean;
  criticalMetrics: HealthMetric[];
  agentResponse?: IntelligentAgentResponse;
  recommendedActions: string[];
  urgencyLevel: 'low' | 'medium' | 'high' | 'critical';
}

export const criticalAnalysisService = {
  /**
   * Check if uploaded analysis contains critical values
   */
  async checkForCriticalValues(analysisId: number): Promise<CriticalAnalysisResult> {
    try {
      // Get the health analysis
      const analyses = await healthService.getUserAnalyses();
      const analysis = analyses.find(a => a.id === analysisId);
      
      if (!analysis || !analysis.metrics) {
        return {
          hasCriticalValues: false,
          criticalMetrics: [],
          recommendedActions: [],
          urgencyLevel: 'low'
        };
      }

      // Extract metrics and check for critical values
      const metrics = Array.isArray(analysis.metrics) ? analysis.metrics : [];
      const criticalMetrics = metrics.filter(metric => 
        metric.status === 'critical' || this.isCriticalValue(metric)
      );

      const hasCriticalValues = criticalMetrics.length > 0;
      const urgencyLevel = this.determineUrgencyLevel(metrics);

      let agentResponse: IntelligentAgentResponse | undefined;
      let recommendedActions: string[] = [];

      // If critical values found, automatically trigger agent analysis
      if (hasCriticalValues) {
        try {
          agentResponse = await agentService.analyzeAndAct({
            health_analysis_id: analysisId,
            auto_book_critical: true,
            preferred_datetime: this.getNextAvailableSlot()
          });

          recommendedActions = this.generateRecommendedActions(criticalMetrics, agentResponse);
        } catch (error) {
          console.error('Failed to trigger automatic agent analysis:', error);
          recommendedActions = this.generateBasicRecommendations(criticalMetrics);
        }
      }

      return {
        hasCriticalValues,
        criticalMetrics,
        agentResponse,
        recommendedActions,
        urgencyLevel
      };
    } catch (error) {
      console.error('Error checking for critical values:', error);
      return {
        hasCriticalValues: false,
        criticalMetrics: [],
        recommendedActions: ['Please consult with your healthcare provider about these results.'],
        urgencyLevel: 'low'
      };
    }
  },

  /**
   * Check if a metric value is critical based on thresholds
   */
  isCriticalValue(metric: HealthMetric): boolean {
    const criticalThresholds = agentService.getDefaultThresholds();
    
    for (const threshold of criticalThresholds) {
      if (metric.name.toLowerCase().includes(threshold.metric.toLowerCase())) {
        const value = parseFloat(metric.value.toString());
        if (isNaN(value)) continue;

        switch (threshold.operator) {
          case '>':
            return value > threshold.critical_threshold;
          case '<':
            return value < threshold.critical_threshold;
          case '>=':
            return value >= threshold.critical_threshold;
          case '<=':
            return value <= threshold.critical_threshold;
        }
      }
    }
    
    return false;
  },

  /**
   * Determine overall urgency level based on metrics
   */
  determineUrgencyLevel(metrics: HealthMetric[]): 'low' | 'medium' | 'high' | 'critical' {
    const criticalCount = metrics.filter(m => m.status === 'critical' || this.isCriticalValue(m)).length;
    const abnormalCount = metrics.filter(m => m.status !== 'normal').length;
    
    if (criticalCount > 0) return 'critical';
    if (abnormalCount >= 3) return 'high';
    if (abnormalCount >= 1) return 'medium';
    return 'low';
  },

  /**
   * Generate recommended actions based on critical metrics and agent response
   */
  generateRecommendedActions(criticalMetrics: HealthMetric[], agentResponse?: IntelligentAgentResponse): string[] {
    const actions: string[] = [];

    if (agentResponse) {
      // Use agent recommendations if available
      if (agentResponse.appointment_booked) {
        actions.push(`🚨 URGENT: Appointment automatically scheduled for ${new Date(agentResponse.appointment_booked.scheduled_datetime).toLocaleDateString()}`);
      }

      agentResponse.recommendations.recommended_specialists.forEach(specialist => {
        actions.push(`📋 Consult ${specialist.type}: ${specialist.reason}`);
      });

      if (agentResponse.recommendations.next_steps) {
        actions.push(...agentResponse.recommendations.next_steps);
      }
    } else {
      // Fallback recommendations
      actions.push('🚨 CRITICAL VALUES DETECTED - Immediate medical attention required');
      
      criticalMetrics.forEach(metric => {
        const specialist = this.getSpecialistForMetric(metric.name);
        if (specialist) {
          actions.push(`📋 Consult ${specialist} for ${metric.name}: ${metric.value} ${metric.unit || ''}`);
        }
      });
      
      actions.push('📞 Contact your healthcare provider immediately');
      actions.push('🏥 Consider visiting emergency care if symptoms worsen');
    }

    return actions;
  },

  /**
   * Generate basic recommendations without agent analysis
   */
  generateBasicRecommendations(criticalMetrics: HealthMetric[]): string[] {
    const actions = [
      '🚨 CRITICAL VALUES DETECTED in your lab results',
      '📞 Contact your healthcare provider immediately',
      '📋 Schedule an urgent appointment with appropriate specialist',
    ];

    criticalMetrics.forEach(metric => {
      actions.push(`⚠️ ${metric.name}: ${metric.value} ${metric.unit || ''} (${metric.status})`);
    });

    return actions;
  },

  /**
   * Get appropriate specialist for a metric
   */
  getSpecialistForMetric(metricName: string): string | null {
    const metricLower = metricName.toLowerCase();
    
    if (metricLower.includes('glucose') || metricLower.includes('hba1c')) {
      return 'Endocrinologist';
    }
    if (metricLower.includes('alt') || metricLower.includes('ast') || metricLower.includes('liver')) {
      return 'Gastroenterologist';
    }
    if (metricLower.includes('creatinine') || metricLower.includes('kidney')) {
      return 'Nephrologist';
    }
    if (metricLower.includes('hemoglobin') || metricLower.includes('platelet') || metricLower.includes('wbc')) {
      return 'Hematologist';
    }
    if (metricLower.includes('cholesterol') || metricLower.includes('triglyceride')) {
      return 'Cardiologist';
    }
    
    return 'General Practitioner';
  },

  /**
   * Get next available appointment slot (default to 1 day from now)
   */
  getNextAvailableSlot(): string {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(9, 0, 0, 0); // 9 AM tomorrow
    return tomorrow.toISOString();
  },

  /**
   * Format urgency level for display
   */
  formatUrgencyLevel(urgency: string): { text: string; color: string; icon: string } {
    switch (urgency) {
      case 'critical':
        return { text: 'CRITICAL', color: 'text-red-600 bg-red-100 border-red-300', icon: '🚨' };
      case 'high':
        return { text: 'HIGH', color: 'text-orange-600 bg-orange-100 border-orange-300', icon: '⚠️' };
      case 'medium':
        return { text: 'MEDIUM', color: 'text-yellow-600 bg-yellow-100 border-yellow-300', icon: '⚡' };
      case 'low':
        return { text: 'LOW', color: 'text-green-600 bg-green-100 border-green-300', icon: '✅' };
      default:
        return { text: 'UNKNOWN', color: 'text-gray-600 bg-gray-100 border-gray-300', icon: '❓' };
    }
  }
}; 