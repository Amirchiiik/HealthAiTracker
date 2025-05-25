import React, { useState } from 'react';
import { FileText, Brain, Zap, AlertCircle, CheckCircle } from 'lucide-react';
import { uploadService } from '../../services/uploadService';
import { healthService } from '../../services/healthService';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { OCRAnalysis, HealthMetric } from '../../types';

interface TextAnalyzerProps {
  onAnalysisComplete?: (analysis: OCRAnalysis) => void;
}

const TextAnalyzer: React.FC<TextAnalyzerProps> = ({ onAnalysisComplete }) => {
  const [text, setText] = useState('');
  const [analysis, setAnalysis] = useState<OCRAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeText = async () => {
    if (!text.trim()) {
      setError('Please enter some medical text to analyze');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await uploadService.analyzeTextWithExplanations({
        raw_text: text
      });
      
      setAnalysis(result);
      onAnalysisComplete?.(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze text');
    } finally {
      setIsLoading(false);
    }
  };

  const clearAnalysis = () => {
    setAnalysis(null);
    setText('');
    setError(null);
  };

  const getMetricStatusIcon = (status: string) => {
    switch (status) {
      case 'normal':
        return <CheckCircle className="w-4 h-4 text-success-500" />;
      case 'critical':
        return <AlertCircle className="w-4 h-4 text-error-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-warning-500" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <Brain className="w-5 h-5 mr-2" />
          Text Analysis Tool
        </h3>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="medical-text" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Medical Text or Lab Results
            </label>
            <textarea
              id="medical-text"
              rows={6}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste your medical text, lab results, or health metrics here...

Example:
Гемоглобин: 140 г/л (норма: 120-160)
Глюкоза: 110 мг/дл (норма: 70-99)
Холестерин: 250 мг/дл (норма: <200)"
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
              disabled={isLoading}
            />
          </div>
          
          {error && (
            <div className="bg-error-50 border border-error-200 text-error-700 px-4 py-3 rounded-md flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" />
              <span>{error}</span>
            </div>
          )}
          
          <div className="flex space-x-3">
            <button
              onClick={analyzeText}
              disabled={isLoading || !text.trim()}
              className="btn-primary flex items-center space-x-2"
            >
              {isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <Zap className="w-4 h-4" />
              )}
              <span>{isLoading ? 'Analyzing...' : 'Analyze Text'}</span>
            </button>
            
            {analysis && (
              <button
                onClick={clearAnalysis}
                className="btn-outline"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Summary */}
          {analysis.overall_summary && (
            <div className="card p-6">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                Analysis Summary
              </h4>
              <p className="text-gray-700 dark:text-gray-300">{analysis.overall_summary}</p>
            </div>
          )}

          {/* Individual Metrics */}
          {analysis.metrics && analysis.metrics.length > 0 && (
            <div className="card p-6">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Brain className="w-5 h-5 mr-2" />
                Detected Health Metrics
                <span className="ml-2 text-sm bg-primary-100 text-primary-800 px-2 py-1 rounded-full">
                  {analysis.metrics.length}
                </span>
              </h4>
              
              <div className="grid gap-4">
                {analysis.metrics.map((metric: HealthMetric, index: number) => (
                  <div key={index} className={`p-4 rounded-lg border-2 ${healthService.getMetricStatusColor(metric.status)}`}>
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h5 className="font-semibold flex items-center space-x-2">
                          <span>{metric.name}</span>
                          {getMetricStatusIcon(metric.status)}
                        </h5>
                        <div className="flex items-baseline space-x-2 mt-1">
                          <span className="text-xl font-bold">
                            {healthService.formatMetricValue(metric)}
                          </span>
                          {metric.reference_range && (
                            <span className="text-sm opacity-70">
                              (Normal: {metric.reference_range})
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className={`px-2 py-1 rounded text-xs font-medium uppercase ${
                        healthService.getMetricStatusColor(metric.status)
                      }`}>
                        {metric.status}
                      </div>
                    </div>
                    
                    {/* Individual Explanation */}
                    <div className="bg-white/50 dark:bg-gray-800/50 rounded p-3 border">
                      <div className="flex items-start space-x-2">
                        <Brain className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                            AI Explanation
                          </p>
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

          {/* Validation Info */}
          {analysis.analysis && (
            <div className="card p-4">
              <div className="flex items-center space-x-2">
                {analysis.analysis.valid ? (
                  <CheckCircle className="w-5 h-5 text-success-500" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-warning-500" />
                )}
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {analysis.analysis.validation_message}
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TextAnalyzer; 