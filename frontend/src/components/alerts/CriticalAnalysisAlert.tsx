import React from 'react';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  Calendar,
  Stethoscope,
  Phone,
  X,
  ExternalLink,
  Clock,
  Brain,
  Heart
} from 'lucide-react';
import { CriticalAnalysisResult, criticalAnalysisService } from '../../services/criticalAnalysisService';

interface CriticalAnalysisAlertProps {
  result: CriticalAnalysisResult;
  onDismiss: () => void;
  analysisId?: number;
}

const CriticalAnalysisAlert: React.FC<CriticalAnalysisAlertProps> = ({
  result,
  onDismiss,
  analysisId
}) => {
  const urgencyFormat = criticalAnalysisService.formatUrgencyLevel(result.urgencyLevel);

  if (!result.hasCriticalValues) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className={`p-6 border-b border-gray-200 dark:border-gray-700 ${
          result.urgencyLevel === 'critical' ? 'bg-red-50 dark:bg-red-900/20' : 'bg-orange-50 dark:bg-orange-900/20'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-full ${
                result.urgencyLevel === 'critical' ? 'bg-red-100 dark:bg-red-900/30' : 'bg-orange-100 dark:bg-orange-900/30'
              }`}>
                <AlertTriangle className={`w-6 h-6 ${
                  result.urgencyLevel === 'critical' ? 'text-red-600' : 'text-orange-600'
                }`} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  Critical Values Detected
                </h2>
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${urgencyFormat.color}`}>
                  <span className="mr-1">{urgencyFormat.icon}</span>
                  {urgencyFormat.text} PRIORITY
                </div>
              </div>
            </div>
            <button
              onClick={onDismiss}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Critical Metrics */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
              <Heart className="w-5 h-5 mr-2 text-red-500" />
              Critical Health Metrics ({result.criticalMetrics.length})
            </h3>
            <div className="space-y-2">
              {result.criticalMetrics.map((metric, index) => (
                <div key={index} className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-medium text-red-900 dark:text-red-100">
                        {metric.name}
                      </span>
                      <span className="ml-2 text-red-700 dark:text-red-300">
                        {metric.value} {metric.unit}
                      </span>
                    </div>
                    <span className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 text-xs rounded uppercase font-medium">
                      {metric.status}
                    </span>
                  </div>
                  {metric.reference_range && (
                    <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                      Normal range: {metric.reference_range}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* AI Agent Response */}
          {result.agentResponse && (
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2 flex items-center">
                <Brain className="w-4 h-4 mr-2" />
                AI Agent Analysis Complete
              </h4>
              
              {result.agentResponse.appointment_booked && (
                <div className="mb-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded">
                  <div className="flex items-center text-green-800 dark:text-green-200">
                    <Calendar className="w-4 h-4 mr-2" />
                    <span className="font-medium">Urgent Appointment Scheduled</span>
                  </div>
                  <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                    {new Date(result.agentResponse.appointment_booked.scheduled_datetime).toLocaleString()}
                  </p>
                </div>
              )}

              {result.agentResponse.recommendations.recommended_specialists.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-blue-800 dark:text-blue-200">Specialists Recommended:</p>
                  {result.agentResponse.recommendations.recommended_specialists.map((specialist, index) => (
                    <div key={index} className="flex items-center text-sm text-blue-700 dark:text-blue-300">
                      <Stethoscope className="w-3 h-3 mr-2" />
                      <span>{specialist.type} - {specialist.priority} priority</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Recommended Actions */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
              <Clock className="w-5 h-5 mr-2 text-orange-500" />
              Immediate Actions Required
            </h3>
            <div className="space-y-2">
              {result.recommendedActions.map((action, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="w-6 h-6 bg-orange-100 dark:bg-orange-900/30 text-orange-600 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                    {index + 1}
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                    {action}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Emergency Contact Info */}
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <h4 className="font-semibold text-red-900 dark:text-red-100 mb-2 flex items-center">
              <Phone className="w-4 h-4 mr-2" />
              Emergency Contact Information
            </h4>
            <div className="space-y-1 text-sm text-red-800 dark:text-red-200">
              <p>• If experiencing severe symptoms, call emergency services immediately</p>
              <p>• Contact your primary care physician as soon as possible</p>
              <p>• Keep this analysis report for your medical appointment</p>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <div className="flex flex-col sm:flex-row gap-3">
            {analysisId && (
              <Link
                to={`/analysis/${analysisId}`}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                View Full Analysis
              </Link>
            )}
            
            <Link
              to="/appointments"
              className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center"
            >
              <Calendar className="w-4 h-4 mr-2" />
              Schedule Appointment
            </Link>
            
            <button
              onClick={onDismiss}
              className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              I Understand
            </button>
          </div>
          
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-3 text-center">
            This analysis has been saved to your health history. Please consult with a healthcare professional for proper medical advice.
          </p>
        </div>
      </div>
    </div>
  );
};

export default CriticalAnalysisAlert; 