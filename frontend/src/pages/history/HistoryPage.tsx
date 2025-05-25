import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Calendar,
  FileText,
  Heart,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Download,
  Search,
  Filter,
  Clock,
  Brain,
  Zap
} from 'lucide-react';
import { format, parseISO, subMonths, startOfMonth, endOfMonth, eachMonthOfInterval } from 'date-fns';
import Navigation from '../../components/layout/Navigation';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { healthService } from '../../services/healthService';
import { useAuth } from '../../contexts/AuthContext';

const HistoryPage: React.FC = () => {
  const { user } = useAuth();
  const [selectedTimeRange, setSelectedTimeRange] = useState('6months');
  const [selectedMetric, setSelectedMetric] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'timeline' | 'analytics'>('analytics');

  // Fetch user analyses
  const { data: analyses, isLoading } = useQuery({
    queryKey: ['user-analyses'],
    queryFn: healthService.getUserAnalyses,
  });

  // Process data for analytics
  const analyticsData = useMemo(() => {
    if (!analyses) return null;

    // Group analyses by month
    const monthlyData = new Map();
    const metricTrends = new Map();
    const statusDistribution = { normal: 0, high: 0, low: 0, elevated: 0, critical: 0 };
    
    analyses.forEach(analysis => {
      const date = parseISO(analysis.created_at);
      const monthKey = format(date, 'yyyy-MM');
      
      if (!monthlyData.has(monthKey)) {
        monthlyData.set(monthKey, {
          month: format(date, 'MMM yyyy'),
          date: monthKey,
          totalAnalyses: 0,
          totalMetrics: 0,
          abnormalMetrics: 0,
          criticalMetrics: 0
        });
      }
      
      const monthData = monthlyData.get(monthKey);
      monthData.totalAnalyses += 1;
      
      if (analysis.metrics) {
        monthData.totalMetrics += analysis.metrics.length;
        
        analysis.metrics.forEach((metric: any) => {
          // Track status distribution
          if (statusDistribution.hasOwnProperty(metric.status)) {
            statusDistribution[metric.status as keyof typeof statusDistribution]++;
          }
          
          // Track abnormal metrics
          if (metric.status !== 'normal') {
            monthData.abnormalMetrics += 1;
          }
          
          if (metric.status === 'critical') {
            monthData.criticalMetrics += 1;
          }
          
          // Track metric trends over time
          const metricKey = metric.name;
          if (!metricTrends.has(metricKey)) {
            metricTrends.set(metricKey, []);
          }
          
          metricTrends.get(metricKey).push({
            date: analysis.created_at,
            value: typeof metric.value === 'number' ? metric.value : parseFloat(metric.value) || 0,
            status: metric.status,
            unit: metric.unit,
            reference_range: metric.reference_range
          });
        });
      }
    });

    return {
      monthlyTrends: Array.from(monthlyData.values()).sort((a, b) => a.date.localeCompare(b.date)),
      metricTrends: Array.from(metricTrends.entries()).map(([name, data]) => ({
        name,
        data: data.sort((a: any, b: any) => new Date(a.date).getTime() - new Date(b.date).getTime())
      })),
      statusDistribution: Object.entries(statusDistribution).map(([status, count]) => ({
        status,
        count,
        percentage: Math.round((count / Object.values(statusDistribution).reduce((a, b) => a + b, 1)) * 100)
      })),
      totalAnalyses: analyses.length,
      totalMetrics: analyses.reduce((acc, analysis) => acc + (analysis.metrics?.length || 0), 0),
      latestAnalysis: analyses[0]
    };
  }, [analyses]);

  const timeRangeOptions = [
    { value: '3months', label: 'Last 3 Months' },
    { value: '6months', label: 'Last 6 Months' },
    { value: '1year', label: 'Last Year' },
    { value: 'all', label: 'All Time' }
  ];

  const pieColors = {
    normal: '#10B981',
    high: '#F59E0B',
    low: '#3B82F6',
    elevated: '#F97316',
    critical: '#EF4444'
  };

  if (isLoading) {
    return (
      <Navigation>
        <div className="p-4 lg:p-8 pb-20 lg:pb-8">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="text-gray-600 dark:text-gray-400 mt-4">Loading your medical history...</p>
          </div>
        </div>
      </Navigation>
    );
  }

  if (!analyses || analyses.length === 0) {
    return (
      <Navigation>
        <div className="p-4 lg:p-8 pb-20 lg:pb-8">
          <div className="text-center">
            <Heart className="w-16 h-16 text-gray-400 mx-auto mb-6" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">No Medical History Yet</h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Upload your first medical file to start tracking your health journey
            </p>
            <a href="/upload" className="btn-primary">
              Upload Medical File
            </a>
          </div>
        </div>
      </Navigation>
    );
  }

  return (
    <Navigation>
      <div className="p-4 lg:p-8 pb-20 lg:pb-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Medical History & Analytics</h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Track your health journey with comprehensive analytics and insights
              </p>
            </div>
            
            <div className="flex flex-wrap items-center gap-3 mt-4 lg:mt-0">
              {/* View Mode Toggle */}
              <div className="flex rounded-lg bg-gray-100 dark:bg-gray-700 p-1">
                <button
                  onClick={() => setViewMode('analytics')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    viewMode === 'analytics'
                      ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                >
                  <BarChart3 className="w-4 h-4 inline mr-2" />
                  Analytics
                </button>
                <button
                  onClick={() => setViewMode('timeline')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    viewMode === 'timeline'
                      ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                >
                  <Clock className="w-4 h-4 inline mr-2" />
                  Timeline
                </button>
              </div>
              
              {/* Export Button */}
              <button className="btn-outline flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
            </div>
          </div>

          {/* Quick Stats */}
          {analyticsData && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="card p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Analyses</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{analyticsData.totalAnalyses}</p>
                  </div>
                  <FileText className="w-8 h-8 text-blue-500" />
                </div>
              </div>
              
              <div className="card p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Health Metrics</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{analyticsData.totalMetrics}</p>
                  </div>
                  <Activity className="w-8 h-8 text-green-500" />
                </div>
              </div>
              
              <div className="card p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Critical Alerts</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {analyticsData.statusDistribution.find(s => s.status === 'critical')?.count || 0}
                    </p>
                  </div>
                  <AlertTriangle className="w-8 h-8 text-red-500" />
                </div>
              </div>
              
              <div className="card p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Normal Metrics</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {analyticsData.statusDistribution.find(s => s.status === 'normal')?.count || 0}
                    </p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-500" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Analytics View */}
        {viewMode === 'analytics' && analyticsData && (
          <div className="space-y-8">
            {/* Monthly Trends */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
                <TrendingUp className="w-6 h-6 mr-2" />
                Health Analysis Trends
              </h2>
              
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={analyticsData.monthlyTrends}>
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis 
                      dataKey="month" 
                      className="text-xs"
                    />
                    <YAxis className="text-xs" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Area 
                      type="monotone" 
                      dataKey="totalAnalyses" 
                      stroke="#3B82F6" 
                      fill="#3B82F6" 
                      fillOpacity={0.6}
                      name="Total Analyses"
                    />
                    <Area 
                      type="monotone" 
                      dataKey="abnormalMetrics" 
                      stroke="#F59E0B" 
                      fill="#F59E0B" 
                      fillOpacity={0.6}
                      name="Abnormal Metrics"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-8">
              {/* Status Distribution */}
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Metric Status Distribution
                </h3>
                
                <div className="h-64 flex items-center justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={analyticsData.statusDistribution.filter(d => d.count > 0)}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="count"
                      >
                        {analyticsData.statusDistribution.map((entry, index) => (
                          <Cell 
                            key={`cell-${index}`} 
                            fill={pieColors[entry.status as keyof typeof pieColors]} 
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                
                <div className="mt-4 space-y-2">
                  {analyticsData.statusDistribution.filter(d => d.count > 0).map(item => (
                    <div key={item.status} className="flex items-center justify-between text-sm">
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: pieColors[item.status as keyof typeof pieColors] }}
                        />
                        <span className="capitalize">{item.status}</span>
                      </div>
                      <span className="font-medium">{item.count} ({item.percentage}%)</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Activity */}
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
                  <Clock className="w-5 h-5 mr-2" />
                  Recent Activity
                </h3>
                
                <div className="space-y-4">
                  {analyses.slice(0, 5).map((analysis, index) => (
                    <div key={analysis.id} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                        <FileText className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {analysis.filename || 'Text Analysis'}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {analysis.metrics?.length || 0} metrics • {format(parseISO(analysis.created_at), 'MMM d, yyyy')}
                        </p>
                        {analysis.overall_summary && (
                          <p className="text-xs text-gray-600 dark:text-gray-300 mt-1 line-clamp-2">
                            {analysis.overall_summary}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Timeline View */}
        {viewMode === 'timeline' && (
          <div className="space-y-6">
            {analyses.map((analysis, index) => (
              <div key={analysis.id} className="card p-6">
                <div className="flex items-start space-x-4">
                  <div className="flex flex-col items-center">
                    <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                      <FileText className="w-5 h-5 text-white" />
                    </div>
                    {index < analyses.length - 1 && (
                      <div className="w-px h-16 bg-gray-200 dark:bg-gray-700 mt-4" />
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {analysis.filename || 'Text Analysis'}
                      </h3>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {format(parseISO(analysis.created_at), 'MMM d, yyyy HH:mm')}
                      </span>
                    </div>
                    
                    {analysis.overall_summary && (
                      <p className="text-gray-600 dark:text-gray-300 mb-4">
                        {analysis.overall_summary}
                      </p>
                    )}
                    
                    {analysis.metrics && analysis.metrics.length > 0 && (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {analysis.metrics.slice(0, 6).map((metric: any, metricIndex: number) => (
                          <div 
                            key={metricIndex} 
                            className={`p-3 rounded-lg border ${healthService.getMetricStatusColor(metric.status)}`}
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium">{metric.name}</span>
                              <span className="text-xs px-2 py-1 rounded-full bg-white/50">
                                {metric.status}
                              </span>
                            </div>
                            <div className="mt-1">
                              <span className="text-lg font-bold">
                                {healthService.formatMetricValue(metric)}
                              </span>
                              {metric.reference_range && (
                                <span className="text-xs text-gray-600 ml-2">
                                  Normal: {metric.reference_range}
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                        {analysis.metrics.length > 6 && (
                          <div className="p-3 rounded-lg border border-gray-200 dark:border-gray-700 flex items-center justify-center">
                            <span className="text-sm text-gray-500">
                              +{analysis.metrics.length - 6} more metrics
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Navigation>
  );
};

export default HistoryPage; 