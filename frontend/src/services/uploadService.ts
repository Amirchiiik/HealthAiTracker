import { apiClient, API_ENDPOINTS } from '../config/api';
import { OCRAnalysis, UploadProgress, MetricsAnalysisRequest, MetricsExplanationRequest, MetricsSummary } from '../types';

export const uploadService = {
  async uploadFile(
    file: File, 
    onProgress?: (progress: UploadProgress) => void
  ): Promise<{ filename: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post(API_ENDPOINTS.UPLOAD, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentage = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percentage,
          });
        }
      },
    });

    return response.data;
  },

  // Enhanced OCR with individual metric explanations
  async getOCRAnalysis(filename: string): Promise<OCRAnalysis> {
    const response = await apiClient.get(API_ENDPOINTS.OCR_ANALYSIS(filename));
    return response.data;
  },

  // Fallback to basic OCR if enhanced fails
  async getBasicOCRAnalysis(filename: string): Promise<OCRAnalysis> {
    const response = await apiClient.get(API_ENDPOINTS.OCR_BASIC(filename));
    return response.data;
  },

  // Analyze raw text with individual explanations
  async analyzeTextWithExplanations(request: MetricsAnalysisRequest): Promise<OCRAnalysis> {
    const response = await apiClient.post(API_ENDPOINTS.EXPLAIN_TEXT_METRICS, request);
    return response.data;
  },

  // Analyze text with enhanced analysis
  async analyzeText(request: MetricsAnalysisRequest): Promise<OCRAnalysis> {
    const response = await apiClient.post(API_ENDPOINTS.ANALYZE_TEXT, request);
    return response.data;
  },

  // Get explanations for specific metrics
  async explainMetrics(request: MetricsExplanationRequest): Promise<{ metrics: any[] }> {
    const response = await apiClient.post(API_ENDPOINTS.EXPLAIN_METRICS, request);
    return response.data;
  },

  // Get metrics summary
  async getMetricsSummary(metrics: any[]): Promise<MetricsSummary> {
    const response = await apiClient.post(API_ENDPOINTS.METRICS_SUMMARY, { metrics });
    return response.data;
  },

  async triggerAgentAnalysis(filename: string): Promise<any> {
    const response = await apiClient.post(API_ENDPOINTS.AGENT_PROCESS_OCR, {
      filename,
    });
    return response.data;
  },

  // Helper function to validate file types
  validateFile(file: File): { isValid: boolean; error?: string } {
    const allowedTypes = [
      'image/jpeg',
      'image/png',
      'image/webp',
      'application/pdf',
      'text/plain',
    ];
    
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      return {
        isValid: false,
        error: 'File type not supported. Please upload JPEG, PNG, WebP, PDF, or TXT files.',
      };
    }

    if (file.size > maxSize) {
      return {
        isValid: false,
        error: 'File size too large. Please upload files smaller than 10MB.',
      };
    }

    return { isValid: true };
  },

  // Helper function to get status color for metrics
  getMetricStatusColor(status: string): string {
    switch (status) {
      case 'normal': 
        return 'text-success-600 bg-success-50 border-success-200';
      case 'low': 
        return 'text-warning-600 bg-warning-50 border-warning-200';
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

  // Helper function to get status icon
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
}; 