import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  FileText, 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  CheckCircle, 
  AlertTriangle, 
  Info,
  ArrowLeft,
  Bot,
  Zap,
  Heart,
  BarChart3,
  MessageCircle
} from 'lucide-react';
import Navigation from '../../components/layout/Navigation';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import CriticalAnalysisAlert from '../../components/alerts/CriticalAnalysisAlert';
import { uploadService } from '../../services/uploadService';
import { healthService } from '../../services/healthService';
import { criticalAnalysisService, CriticalAnalysisResult } from '../../services/criticalAnalysisService';
import { format } from 'date-fns';

const AnalysisPage: React.FC = () => {
  const { filename } = useParams<{ filename: string }>();
  const [isProcessingAgent, setIsProcessingAgent] = useState(false);
  const [criticalAnalysisResult, setCriticalAnalysisResult] = useState<CriticalAnalysisResult | null>(null);
  const [showCriticalAlert, setShowCriticalAlert] = useState(false);

  // Fetch OCR analysis with enhanced individual explanations
  const { data: analysis, isLoading, error, refetch } = useQuery({
    queryKey: ['ocr-analysis', filename],
    queryFn: () => filename ? uploadService.getOCRAnalysis(filename) : null,
    enabled: !!filename,
    retry: (failureCount, error: any) => {
      // Fallback to basic OCR if enhanced fails
      if (failureCount === 0 && error?.response?.status === 404) {
        return true;
      }
      return false;
    },
  });

  // Fallback to basic OCR if enhanced fails
  const { data: basicAnalysis } = useQuery({
    queryKey: ['basic-ocr-analysis', filename],
    queryFn: () => filename ? uploadService.getBasicOCRAnalysis(filename) : null,
    enabled: !!filename && !!error,
  });

  const currentAnalysis = analysis || basicAnalysis;

  // Check for critical values when analysis is loaded
  useEffect(() => {
    const checkCriticalValues = async () => {
      if (currentAnalysis && currentAnalysis.id) {
        try {
          const analysisId = typeof currentAnalysis.id === 'string' ? parseInt(currentAnalysis.id, 10) : currentAnalysis.id;
          const result = await criticalAnalysisService.checkForCriticalValues(analysisId);
          setCriticalAnalysisResult(result);
          
          if (result.hasCriticalValues) {
            setShowCriticalAlert(true);
          }
        } catch (error) {
          console.error('Failed to check for critical values:', error);
        }
      }
    };

    checkCriticalValues();
  }, [currentAnalysis]);

  const triggerAgentAnalysis = async () => {
    if (!filename) return;
    
    setIsProcessingAgent(true);
    try {
      await uploadService.triggerAgentAnalysis(filename);
      // Refetch the analysis to get updated data
      setTimeout(() => {
        refetch();
      }, 2000);
      alert('AI Agent analysis triggered! The page will refresh with updated insights.');
    } catch (error) {
      console.error('Failed to trigger agent analysis:', error);
      alert('Failed to trigger AI analysis. Please try again.');
    } finally {
      setIsProcessingAgent(false);
    }
  };

  const getMetricStatusIcon = (status: string) => {
    switch (status) {
      case 'normal':
        return <CheckCircle className="w-5 h-5 text-success-500" />;
      case 'high':
      case 'elevated':
        return <TrendingUp className="w-5 h-5 text-warning-500" />;
      case 'low':
        return <TrendingDown className="w-5 h-5 text-blue-500" />;
      case 'critical':
        return <AlertTriangle className="w-5 h-5 text-error-500" />;
      default:
        return <Info className="w-5 h-5 text-gray-400" />;
    }
  };

  if (!filename) {
    return (
      <Navigation>
        <div className="p-4 lg:p-8 pb-20 lg:pb-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">File not found</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Please check the filename and try again.
            </p>
            <Link to="/upload" className="btn-primary mt-4">
              Upload New File
            </Link>
          </div>
        </div>
      </Navigation>
    );
  }

  if (isLoading) {
    return (
      <Navigation>
        <div className="p-4 lg:p-8 pb-20 lg:pb-8">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="text-gray-600 dark:text-gray-400 mt-4">
              Analyzing your medical file with AI...
            </p>
          </div>
        </div>
      </Navigation>
    );
  }

  if ((error && !basicAnalysis) || !currentAnalysis) {
    return (
      <Navigation>
        <div className="p-4 lg:p-8 pb-20 lg:pb-8">
          <div className="text-center">
            <AlertTriangle className="w-12 h-12 text-error-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analysis Failed</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              We couldn't analyze this file. Please try uploading it again.
            </p>
            <Link to="/upload" className="btn-primary mt-4">
              Upload New File
            </Link>
          </div>
        </div>
      </Navigation>
    );
  }

  // Generate metrics summary for enhanced display
  const metricsSummary = currentAnalysis.metrics ? 
    healthService.generateMetricsSummary(currentAnalysis.metrics) : null;

  return (
    <Navigation>
      {/* Critical Analysis Alert */}
      {showCriticalAlert && criticalAnalysisResult && (
        <CriticalAnalysisAlert
          result={criticalAnalysisResult}
          onDismiss={() => setShowCriticalAlert(false)}
          analysisId={currentAnalysis?.id ? (typeof currentAnalysis.id === 'string' ? parseInt(currentAnalysis.id, 10) : currentAnalysis.id) : undefined}
        />
      )}
      
      <div className="p-4 lg:p-8 pb-20 lg:pb-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <Link
              to="/dashboard"
              className="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Enhanced Analysis Results
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                {filename} • {currentAnalysis.created_at 
                  ? `Analyzed on ${format(new Date(currentAnalysis.created_at), 'MMMM d, yyyy')}`
                  : 'Recently analyzed'
                }
              </p>
            </div>
          </div>

          {/* Analysis Summary */}
          {currentAnalysis.overall_summary && (
            <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <h2 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Analysis Summary
              </h2>
              <p className="text-blue-800 dark:text-blue-200">{currentAnalysis.overall_summary}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={triggerAgentAnalysis}
              disabled={isProcessingAgent}
              className="btn-primary flex items-center space-x-2"
            >
              {isProcessingAgent ? (
                <LoadingSpinner size="sm" />
              ) : (
                <Bot className="w-4 h-4" />
              )}
              <span>{isProcessingAgent ? 'Processing...' : 'Get AI Recommendations'}</span>
            </button>
            
            <Link to="/upload" className="btn-outline flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>Upload Another File</span>
            </Link>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Individual Health Metrics with Explanations */}
            {currentAnalysis.metrics && currentAnalysis.metrics.length > 0 && (
              <div className="card p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
                  <Activity className="w-6 h-6 mr-2" />
                  Individual Health Metrics
                  <span className="ml-2 text-sm bg-primary-100 text-primary-800 px-2 py-1 rounded-full">
                    {currentAnalysis.metrics.length} detected
                  </span>
                </h2>
                
                <div className="space-y-6">
                  {currentAnalysis.metrics.map((metric, index) => (
                    <div key={index} className={`p-6 rounded-lg border-2 ${healthService.getMetricStatusColor(metric.status)}`}>
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-lg font-semibold flex items-center space-x-2">
                            <span>{metric.name}</span>
                            {getMetricStatusIcon(metric.status)}
                          </h3>
                          <div className="flex items-baseline space-x-2 mt-1">
                            <span className="text-2xl font-bold">
                              {healthService.formatMetricValue(metric)}
                            </span>
                            {metric.reference_range && (
                              <span className="text-sm opacity-70">
                                (Normal: {metric.reference_range})
                              </span>
                            )}
                          </div>
                        </div>
                        
                        <div className={`px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wide ${
                          healthService.getMetricStatusColor(metric.status)
                        }`}>
                          {metric.status}
                        </div>
                      </div>
                      
                      {/* Individual Explanation */}
                      <div className="bg-white/50 dark:bg-gray-800/50 rounded-lg p-4 border">
                        <div className="flex items-start space-x-2">
                          <Brain className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white mb-1">
                              AI Explanation
                            </h4>
                            <p className="text-sm text-gray-700 dark:text-gray-300">
                              {metric.explanation}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Extracted Text */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
                <FileText className="w-6 h-6 mr-2" />
                Extracted Medical Text
              </h2>
              
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 max-h-96 overflow-y-auto">
                <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-mono">
                  {currentAnalysis.extracted_text}
                </pre>
              </div>
              
              {currentAnalysis.analysis && (
                <div className="mt-4 flex items-center space-x-2">
                  {currentAnalysis.analysis.valid ? (
                    <CheckCircle className="w-5 h-5 text-success-500" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-warning-500" />
                  )}
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {currentAnalysis.analysis.validation_message}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Metrics Summary */}
            {metricsSummary && (
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Metrics Summary
                </h3>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="text-center p-3 bg-success-50 rounded-lg border border-success-200">
                      <div className="text-2xl font-bold text-success-600">{metricsSummary.by_status.normal}</div>
                      <div className="text-success-700">Normal</div>
                    </div>
                    <div className="text-center p-3 bg-warning-50 rounded-lg border border-warning-200">
                      <div className="text-2xl font-bold text-warning-600">
                        {metricsSummary.by_status.high + metricsSummary.by_status.low + metricsSummary.by_status.elevated}
                      </div>
                      <div className="text-warning-700">Abnormal</div>
                    </div>
                  </div>
                  
                  {metricsSummary.urgent_attention.length > 0 && (
                    <div className="p-3 bg-error-50 rounded-lg border border-error-200">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-error-600">{metricsSummary.urgent_attention.length}</div>
                        <div className="text-error-700 text-sm">Critical</div>
                      </div>
                    </div>
                  )}
                  
                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                    {metricsSummary.recommendations.map((rec, index) => (
                      <p key={index} className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                        • {rec}
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Quick Actions
              </h3>
              
              <div className="space-y-3">
                <Link
                  to="/history"
                  className="w-full btn-outline text-sm flex items-center justify-center space-x-2"
                >
                  <FileText className="w-4 h-4" />
                  <span>View All Analyses</span>
                </Link>
                
                <Link
                  to="/appointments"
                  className="w-full btn-secondary text-sm flex items-center justify-center space-x-2"
                >
                  <Heart className="w-4 h-4" />
                  <span>Book Doctor Visit</span>
                </Link>
                
                <Link
                  to="/chat"
                  className="w-full btn-secondary text-sm flex items-center justify-center space-x-2"
                >
                  <MessageCircle className="w-4 h-4" />
                  <span>Ask AI Assistant</span>
                </Link>
              </div>
            </div>

            {/* File Info */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                File Information
              </h3>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Filename:</span>
                  <span className="font-medium text-gray-900 dark:text-white">{currentAnalysis.filename}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Analysis Type:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {analysis ? 'Enhanced OCR' : 'Basic OCR'}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Processed:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {currentAnalysis.created_at 
                      ? format(new Date(currentAnalysis.created_at), 'MMM d, yyyy HH:mm')
                      : 'Recently'
                    }
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Metrics Found:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {currentAnalysis.metrics?.length || 0}
                  </span>
                </div>
              </div>
            </div>

            {/* Health Tips */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Zap className="w-5 h-5 mr-2" />
                Health Tips
              </h3>
              
              <div className="space-y-3 text-sm">
                <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                  <p className="text-green-800 dark:text-green-300">
                    Each metric now comes with individual AI explanations for better understanding.
                  </p>
                </div>
                
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <p className="text-blue-800 dark:text-blue-300">
                    Critical metrics require immediate medical attention.
                  </p>
                </div>
                
                <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                  <p className="text-purple-800 dark:text-purple-300">
                    Regular monitoring helps track your health progress over time.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Navigation>
  );
};

export default AnalysisPage; 