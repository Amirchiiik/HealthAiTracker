import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Brain,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Calendar,
  User,
  Stethoscope,
  TrendingUp,
  TrendingDown,
  Zap,
  Bell,
  RefreshCw,
  Play,
  Settings,
  Info,
  ExternalLink,
  ChevronRight,
  Shield,
  Target
} from 'lucide-react';
import Navigation from '../../components/layout/Navigation';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';
import { agentService } from '../../services/agentService';
import { healthService } from '../../services/healthService';
import { 
  IntelligentAgentResponse, 
  HealthAnalysis, 
  AgentAnalysisRequest,
  SpecialistRecommendation,
  AgentAction 
} from '../../types';

const AgentPage: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<number | null>(null);
  const [autoBookCritical, setAutoBookCritical] = useState(true);
  const [preferredDateTime, setPreferredDateTime] = useState('');
  const [agentResponse, setAgentResponse] = useState<IntelligentAgentResponse | null>(null);

  // Fetch user's health analyses
  const { data: healthAnalyses, isLoading: analysesLoading } = useQuery({
    queryKey: ['health-analyses'],
    queryFn: healthService.getUserAnalyses,
    enabled: !!user
  });

  // Fetch critical thresholds
  const { data: criticalThresholds } = useQuery({
    queryKey: ['critical-thresholds'],
    queryFn: agentService.getCriticalThresholds
  });

  // Agent analysis mutation
  const agentAnalysisMutation = useMutation({
    mutationFn: agentService.analyzeAndAct,
    onSuccess: (response) => {
      setAgentResponse(response);
      queryClient.invalidateQueries({ queryKey: ['agent-notifications'] });
    },
    onError: (error: any) => {
      console.error('Agent analysis failed:', error);
      alert(error.message || 'Failed to analyze health data. Please try again.');
    }
  });

  // Set default preferred datetime to 1 week from now
  useEffect(() => {
    const nextWeek = new Date();
    nextWeek.setDate(nextWeek.getDate() + 7);
    nextWeek.setHours(10, 0, 0, 0); // 10 AM
    setPreferredDateTime(nextWeek.toISOString().slice(0, 16));
  }, []);

  const handleAnalyzeHealth = () => {
    if (!selectedAnalysisId) {
      alert('Please select a health analysis to analyze');
      return;
    }

    const request: AgentAnalysisRequest = {
      health_analysis_id: selectedAnalysisId,
      auto_book_critical: autoBookCritical,
      preferred_datetime: preferredDateTime
    };

    agentAnalysisMutation.mutate(request);
  };

  const renderAnalysisSummary = (response: IntelligentAgentResponse) => {
    const { analysis_summary } = response;
    const priority = agentService.formatPriorityLevel(analysis_summary.priority_level);
    const requiresAttention = agentService.requiresImmediateAttention(response);

    return (
      <div className={`p-6 rounded-lg border-2 ${
        requiresAttention 
          ? 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20' 
          : 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
      }`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
            <Brain className="w-5 h-5 mr-2" />
            AI Analysis Summary
          </h3>
          <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${priority.color} bg-white dark:bg-gray-800`}>
            <span className="mr-1">{priority.icon}</span>
            {priority.text} Priority
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{analysis_summary.total_metrics}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Metrics</div>
          </div>
          <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">{analysis_summary.abnormal_metrics}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Abnormal</div>
          </div>
          <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
            <div className="text-2xl font-bold text-red-600">{analysis_summary.critical_metrics}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Critical</div>
          </div>
          <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {analysis_summary.total_metrics - analysis_summary.abnormal_metrics}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Normal</div>
          </div>
        </div>

        <p className="text-gray-700 dark:text-gray-300">
          {agentService.generateSummaryText(response)}
        </p>
      </div>
    );
  };

  const renderSpecialistRecommendations = (specialists: SpecialistRecommendation[]) => {
    if (specialists.length === 0) {
      return (
        <div className="p-6 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
          <div className="flex items-center text-green-700 dark:text-green-300">
            <CheckCircle className="w-5 h-5 mr-2" />
            <span className="font-medium">No specialist consultations needed at this time</span>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {specialists.map((specialist, index) => {
          const priority = agentService.formatPriorityLevel(specialist.priority);
          const icon = agentService.getSpecialistIcon(specialist.type);
          
          return (
            <div key={index} className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className="text-2xl">{icon}</div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 dark:text-white">
                      {agentService.formatSpecialistType(specialist.type)}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {specialist.reason}
                    </p>
                    <div className="flex items-center mt-2 space-x-2">
                      <span className="text-xs text-gray-500">Metrics involved:</span>
                      {specialist.metrics_involved.map((metric, idx) => (
                        <span key={idx} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded">
                          {metric}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className={`flex items-center px-2 py-1 rounded text-xs font-medium ${priority.color} bg-gray-50 dark:bg-gray-700`}>
                  <span className="mr-1">{priority.icon}</span>
                  {priority.text}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderAgentRecommendations = (response: IntelligentAgentResponse) => {
    const { recommendations } = response;

    return (
      <div className="space-y-6">
        {/* Specialist Recommendations */}
        <div>
          <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Stethoscope className="w-5 h-5 mr-2" />
            Specialist Recommendations
          </h4>
          {renderSpecialistRecommendations(recommendations.recommended_specialists)}
        </div>

        {/* AI Reasoning */}
        {recommendations.agent_reasoning && (
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <h4 className="font-semibold text-blue-900 dark:text-blue-300 mb-2 flex items-center">
              <Brain className="w-4 h-4 mr-2" />
              AI Clinical Reasoning
            </h4>
            <p className="text-blue-800 dark:text-blue-200 text-sm leading-relaxed">
              {recommendations.agent_reasoning}
            </p>
          </div>
        )}

        {/* Next Steps */}
        {recommendations.next_steps && recommendations.next_steps.length > 0 && (
          <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
              <Target className="w-4 h-4 mr-2" />
              Recommended Next Steps
            </h4>
            <ul className="space-y-2">
              {recommendations.next_steps.map((step, index) => (
                <li key={index} className="flex items-start text-sm text-gray-700 dark:text-gray-300">
                  <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-gray-400 flex-shrink-0" />
                  {step}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  const renderActionsTaken = (actions: AgentAction[]) => {
    if (actions.length === 0) {
      return (
        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <p className="text-gray-600 dark:text-gray-400 text-sm">No automated actions were taken.</p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {actions.map((action, index) => (
          <div key={index} className={`p-3 rounded-lg border ${
            action.success 
              ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' 
              : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                {action.success ? (
                  <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-red-600 mr-2" />
                )}
                <span className="font-medium text-gray-900 dark:text-white">
                  {action.action_type}
                </span>
              </div>
              <span className="text-xs text-gray-500">
                {new Date(action.timestamp).toLocaleString()}
              </span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {action.description}
            </p>
          </div>
        ))}
      </div>
    );
  };

  const renderAppointmentBooked = (response: IntelligentAgentResponse) => {
    const { appointment_booked } = response;
    
    if (!appointment_booked) return null;

    return (
      <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
        <div className="flex items-center mb-3">
          <Calendar className="w-5 h-5 text-green-600 mr-2" />
          <h4 className="font-semibold text-green-900 dark:text-green-300">
            Appointment Automatically Booked
          </h4>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div>
            <span className="font-medium text-gray-700 dark:text-gray-300">Date & Time:</span>
            <p className="text-gray-600 dark:text-gray-400">
              {new Date(appointment_booked.scheduled_datetime).toLocaleString()}
            </p>
          </div>
          <div>
            <span className="font-medium text-gray-700 dark:text-gray-300">Type:</span>
            <p className="text-gray-600 dark:text-gray-400 capitalize">
              {appointment_booked.appointment_type}
            </p>
          </div>
          <div className="md:col-span-2">
            <span className="font-medium text-gray-700 dark:text-gray-300">Reason:</span>
            <p className="text-gray-600 dark:text-gray-400">
              {appointment_booked.booking_reason}
            </p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Navigation>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
                  <Brain className="w-8 h-8 mr-3 text-blue-600" />
                  AI Health Agent
                </h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                  Intelligent analysis and automated health recommendations
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <div className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-sm font-medium">
                  ✅ Agent Active
                </div>
              </div>
            </div>
          </div>

          {/* Analysis Configuration */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <Settings className="w-5 h-5 mr-2" />
              Analysis Configuration
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Health Analysis Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Select Health Analysis
                </label>
                {analysesLoading ? (
                  <div className="flex items-center justify-center p-4">
                    <LoadingSpinner size="sm" />
                  </div>
                ) : (
                  <select
                    value={selectedAnalysisId || ''}
                    onChange={(e) => setSelectedAnalysisId(Number(e.target.value) || null)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="">Choose an analysis...</option>
                    {healthAnalyses && Array.isArray(healthAnalyses) && healthAnalyses.map((analysis: HealthAnalysis) => (
                      <option key={analysis.id} value={analysis.id}>
                        {analysis.filename || `Analysis ${analysis.id}`} - {new Date(analysis.created_at).toLocaleDateString()}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {/* Preferred Appointment Time */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Preferred Appointment Time
                </label>
                <input
                  type="datetime-local"
                  value={preferredDateTime}
                  onChange={(e) => setPreferredDateTime(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            {/* Auto-booking Option */}
            <div className="mt-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={autoBookCritical}
                  onChange={(e) => setAutoBookCritical(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Automatically book appointments for critical values
                </span>
              </label>
            </div>

            {/* Analyze Button */}
            <div className="mt-6">
              <button
                onClick={handleAnalyzeHealth}
                disabled={!selectedAnalysisId || agentAnalysisMutation.isPending}
                className="w-full md:w-auto px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center"
              >
                {agentAnalysisMutation.isPending ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span className="ml-2">Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Run AI Analysis
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Agent Response */}
          {agentResponse && (
            <div className="space-y-6">
              {/* Analysis Summary */}
              {renderAnalysisSummary(agentResponse)}

              {/* Recommendations */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Zap className="w-5 h-5 mr-2" />
                  AI Recommendations
                </h3>
                {renderAgentRecommendations(agentResponse)}
              </div>

              {/* Actions Taken */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Actions Taken
                </h3>
                {renderActionsTaken(agentResponse.actions_taken)}
              </div>

              {/* Appointment Booked */}
              {agentResponse.appointment_booked && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                    <Calendar className="w-5 h-5 mr-2" />
                    Appointment Scheduled
                  </h3>
                  {renderAppointmentBooked(agentResponse)}
                </div>
              )}
            </div>
          )}

          {/* Critical Thresholds Info */}
          {criticalThresholds && (
            <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Shield className="w-5 h-5 mr-2" />
                Critical Value Thresholds
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {criticalThresholds.map((threshold, index) => (
                  <div key={index} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="font-medium text-gray-900 dark:text-white">
                      {threshold.metric}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {threshold.operator} {threshold.critical_threshold}
                    </div>
                    <div className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                      → {threshold.specialist}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Navigation>
  );
};

export default AgentPage; 