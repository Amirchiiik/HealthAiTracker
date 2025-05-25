import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Upload, CheckCircle, AlertCircle, Brain } from 'lucide-react';
import Navigation from '../../components/layout/Navigation';
import FileUpload from '../../components/upload/FileUpload';
import TextAnalyzer from '../../components/analysis/TextAnalyzer';
import CriticalAnalysisAlert from '../../components/alerts/CriticalAnalysisAlert';
import { criticalAnalysisService, CriticalAnalysisResult } from '../../services/criticalAnalysisService';
import { healthService } from '../../services/healthService';

const UploadPage: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<'upload' | 'text'>('upload');
  const [criticalAnalysisResult, setCriticalAnalysisResult] = useState<CriticalAnalysisResult | null>(null);
  const [showCriticalAlert, setShowCriticalAlert] = useState(false);
  const navigate = useNavigate();

  const handleUploadComplete = async (filename: string) => {
    setUploadedFiles(prev => [...prev, filename]);
    
    // Check for critical values after upload
    try {
      // Wait a moment for the analysis to be processed
      setTimeout(async () => {
        try {
          // Get the latest analysis for this user
          const analyses = await healthService.getUserAnalyses();
          const latestAnalysis = analyses[0]; // Assuming the latest is first
          
          if (latestAnalysis) {
            const result = await criticalAnalysisService.checkForCriticalValues(latestAnalysis.id);
            
            if (result.hasCriticalValues) {
              setCriticalAnalysisResult(result);
              setShowCriticalAlert(true);
              // Don't auto-navigate if critical values are found
              return;
            }
          }
        } catch (error) {
          console.error('Failed to check for critical values:', error);
        }
        
        // Only navigate if no critical values or check failed
        navigate(`/analysis/${filename}`);
      }, 2000);
    } catch (error) {
      console.error('Error in upload completion:', error);
      // Fallback to normal navigation
      setTimeout(() => {
        navigate(`/analysis/${filename}`);
      }, 1000);
    }
  };

  const handleUploadError = (error: string) => {
    setErrors(prev => [...prev, error]);
    // Auto-remove error after 5 seconds
    setTimeout(() => {
      setErrors(prev => prev.filter(e => e !== error));
    }, 5000);
  };

  const handleTextAnalysisComplete = (analysis: any) => {
    // Show success message for text analysis
    setErrors(prev => [...prev.filter(e => !e.includes('analysis')), 'Text analysis completed successfully!']);
    setTimeout(() => {
      setErrors(prev => prev.filter(e => !e.includes('completed')));
    }, 3000);
  };

  const clearError = (errorToRemove: string) => {
    setErrors(prev => prev.filter(e => e !== errorToRemove));
  };

  return (
    <Navigation>
      {/* Critical Analysis Alert */}
      {showCriticalAlert && criticalAnalysisResult && (
        <CriticalAnalysisAlert
          result={criticalAnalysisResult}
          onDismiss={() => {
            setShowCriticalAlert(false);
            // Navigate to analysis after dismissing critical alert
            if (uploadedFiles.length > 0) {
              navigate(`/analysis/${uploadedFiles[uploadedFiles.length - 1]}`);
            }
          }}
          analysisId={criticalAnalysisResult.agentResponse?.analysis_summary?.health_analysis_id}
        />
      )}
      
      <div className="p-4 lg:p-8 pb-20 lg:pb-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Medical Analysis
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Upload medical documents or analyze text directly for AI-powered health insights
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('upload')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'upload'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Upload className="w-4 h-4" />
                  <span>Upload Files</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('text')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'text'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Brain className="w-4 h-4" />
                  <span>Analyze Text</span>
                </div>
              </button>
            </nav>
          </div>
        </div>

        {/* Error/Success Messages */}
        {errors.length > 0 && (
          <div className="mb-6 space-y-2">
            {errors.map((error, index) => (
              <div
                key={index}
                className={`px-4 py-3 rounded-md flex items-center justify-between ${
                  error.includes('success') || error.includes('completed')
                    ? 'bg-success-50 border border-success-200 text-success-700'
                    : 'bg-error-50 border border-error-200 text-error-700'
                }`}
              >
                <div className="flex items-center">
                  {error.includes('success') || error.includes('completed') ? (
                    <CheckCircle className="w-5 h-5 mr-2" />
                  ) : (
                    <AlertCircle className="w-5 h-5 mr-2" />
                  )}
                  <span>{error}</span>
                </div>
                <button
                  onClick={() => clearError(error)}
                  className={error.includes('success') || error.includes('completed') ? 'text-success-500 hover:text-success-700' : 'text-error-500 hover:text-error-700'}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Success Messages for Uploads */}
        {uploadedFiles.length > 0 && activeTab === 'upload' && (
          <div className="mb-6">
            <div className="bg-success-50 border border-success-200 text-success-700 px-4 py-3 rounded-md flex items-center">
              <CheckCircle className="w-5 h-5 mr-2" />
              <span>
                {uploadedFiles.length} file(s) uploaded successfully! 
                {uploadedFiles.length === 1 && ' Redirecting to analysis...'}
              </span>
            </div>
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'upload' ? (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Upload Area */}
            <div className="lg:col-span-2">
              <FileUpload
                onUploadComplete={handleUploadComplete}
                onUploadError={handleUploadError}
                maxFiles={10}
              />
            </div>

            {/* Sidebar Info */}
            <div className="space-y-6">
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Supported Files
                </h3>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Lab Reports</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">PDF, JPG, PNG</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Blood Tests</span>
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">PDF, JPG, PNG</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Prescriptions</span>
                    <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">PDF, JPG, PNG</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Medical Notes</span>
                    <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded">TXT, PDF</span>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  What Happens Next?
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-medium">
                      1
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">OCR Processing</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        We extract text and data from your files
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-xs font-medium">
                      2
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Enhanced AI Analysis</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        Individual metric explanations with AI insights
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-xs font-medium">
                      3
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Personalized Recommendations</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        Get detailed health insights and recommendations
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Privacy & Security
                </h3>
                
                <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>End-to-end encryption</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>HIPAA compliant storage</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Data deletion on request</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>No data sharing with third parties</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Text Analysis Area */}
            <div className="lg:col-span-2">
              <TextAnalyzer onAnalysisComplete={handleTextAnalysisComplete} />
            </div>

            {/* Text Analysis Sidebar */}
            <div className="space-y-6">
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Brain className="w-5 h-5 mr-2" />
                  How It Works
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-medium">
                      1
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Paste Medical Text</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        Copy and paste lab results, medical reports, or health metrics
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-xs font-medium">
                      2
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">AI Processing</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        Our AI extracts and analyzes health metrics
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-xs font-medium">
                      3
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Individual Explanations</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        Get detailed explanations for each metric
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Supported Formats
                </h3>
                
                <div className="space-y-3 text-sm">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Lab results with values and units</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Blood test reports</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Medical measurements</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Multiple languages supported</span>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Example Text
                </h3>
                
                <div className="bg-gray-50 dark:bg-gray-800 rounded p-3 text-sm font-mono">
                  <div className="text-gray-700 dark:text-gray-300">
                    Гемоглобин: 140 г/л (норма: 120-160)<br/>
                    Глюкоза: 110 мг/дл (норма: 70-99)<br/>
                    Холестерин: 250 мг/дл (норма: &lt;200)<br/>
                    АД: 140/90 mmHg (норма: &lt;120/80)
                  </div>
                </div>
                
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Copy this example to test the analysis feature
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Recently Uploaded Files */}
        {uploadedFiles.length > 0 && activeTab === 'upload' && (
          <div className="mt-12">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Recently Uploaded
            </h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {uploadedFiles.map((filename, index) => (
                <div key={index} className="card p-4 hover:shadow-md transition-shadow duration-200">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {filename}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Uploaded successfully
                      </p>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => navigate(`/analysis/${filename}`)}
                    className="mt-3 w-full btn-outline text-sm"
                  >
                    View Analysis
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Navigation>
  );
};

export default UploadPage;