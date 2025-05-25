import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart3,
  PieChart,
  TrendingUp,
  TrendingDown,
  Users,
  Activity,
  Calendar,
  MessageSquare,
  AlertTriangle,
  FileText,
  Clock,
  Filter,
  Download,
  RefreshCw,
  Eye,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import Navigation from '../../components/layout/Navigation';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

interface AnalyticsData {
  patient_trends: {
    month: string;
    new_patients: number;
    active_patients: number;
    total_consultations: number;
  }[];
  condition_distribution: {
    condition: string;
    count: number;
    percentage: number;
    color: string;
  }[];
  monthly_metrics: {
    total_patients: number;
    total_consultations: number;
    critical_cases: number;
    avg_response_time: number;
    patient_satisfaction: number;
    growth_rate: number;
  };
  recent_insights: {
    id: string;
    type: 'trend' | 'alert' | 'recommendation';
    title: string;
    description: string;
    impact: 'high' | 'medium' | 'low';
    created_at: string;
  }[];
}

const AnalyticsPage: React.FC = () => {
  const [timeframe, setTimeframe] = useState('6months');
  const [selectedMetric, setSelectedMetric] = useState('patients');

  // Fetch analytics data
  const { data: analytics, isLoading, refetch } = useQuery({
    queryKey: ['doctor-analytics', timeframe],
    queryFn: async (): Promise<AnalyticsData> => {
      // Mock data for now - replace with actual API call
      return {
        patient_trends: [
          { month: 'Jul', new_patients: 12, active_patients: 45, total_consultations: 87 },
          { month: 'Aug', new_patients: 15, active_patients: 52, total_consultations: 95 },
          { month: 'Sep', new_patients: 18, active_patients: 61, total_consultations: 112 },
          { month: 'Oct', new_patients: 14, active_patients: 67, total_consultations: 108 },
          { month: 'Nov', new_patients: 21, active_patients: 74, total_consultations: 125 },
          { month: 'Dec', new_patients: 19, active_patients: 78, total_consultations: 134 }
        ],
        condition_distribution: [
          { condition: 'Hypertension', count: 28, percentage: 35, color: '#3B82F6' },
          { condition: 'Diabetes', count: 22, percentage: 28, color: '#EF4444' },
          { condition: 'Heart Disease', count: 15, percentage: 19, color: '#F59E0B' },
          { condition: 'Respiratory', count: 10, percentage: 13, color: '#10B981' },
          { condition: 'Other', count: 4, percentage: 5, color: '#6B7280' }
        ],
        monthly_metrics: {
          total_patients: 78,
          total_consultations: 134,
          critical_cases: 12,
          avg_response_time: 2.4,
          patient_satisfaction: 4.8,
          growth_rate: 15.3
        },
        recent_insights: [
          {
            id: '1',
            type: 'trend',
            title: 'Patient Volume Increase',
            description: 'New patient registrations increased by 25% this month',
            impact: 'high',
            created_at: '2024-01-15T10:00:00Z'
          },
          {
            id: '2',
            type: 'alert',
            title: 'High Critical Case Rate',
            description: '15% of cases marked as critical - above normal threshold',
            impact: 'high',
            created_at: '2024-01-14T14:30:00Z'
          },
          {
            id: '3',
            type: 'recommendation',
            title: 'Response Time Optimization',
            description: 'Consider scheduling more consultation slots for faster response',
            impact: 'medium',
            created_at: '2024-01-13T09:15:00Z'
          }
        ]
      };
    }
  });

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'trend':
        return <TrendingUp className="w-5 h-5 text-blue-500" />;
      case 'alert':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'recommendation':
        return <Eye className="w-5 h-5 text-green-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  const getTrendIcon = (value: number) => {
    if (value > 0) return <ArrowUp className="w-4 h-4 text-green-500" />;
    if (value < 0) return <ArrowDown className="w-4 h-4 text-red-500" />;
    return <Minus className="w-4 h-4 text-gray-500" />;
  };

  if (isLoading) {
    return (
      <Navigation>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </Navigation>
    );
  }

  return (
    <Navigation>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
        <div className="max-w-7xl mx-auto space-y-6">
          
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
                <BarChart3 className="w-8 h-8 mr-3 text-blue-600" />
                Practice Analytics
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Insights and metrics for your medical practice
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="3months">Last 3 Months</option>
                <option value="6months">Last 6 Months</option>
                <option value="1year">Last Year</option>
              </select>
              
              <button
                onClick={() => refetch()}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </button>
              
              <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Patients</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics?.monthly_metrics.total_patients}</p>
                  <div className="flex items-center mt-1">
                    {getTrendIcon(analytics?.monthly_metrics.growth_rate || 0)}
                    <span className="text-sm text-green-600 ml-1">+{analytics?.monthly_metrics.growth_rate}%</span>
                  </div>
                </div>
                <Users className="w-8 h-8 text-blue-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Consultations</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics?.monthly_metrics.total_consultations}</p>
                  <div className="flex items-center mt-1">
                    {getTrendIcon(12)}
                    <span className="text-sm text-green-600 ml-1">+12%</span>
                  </div>
                </div>
                <MessageSquare className="w-8 h-8 text-green-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Critical Cases</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics?.monthly_metrics.critical_cases}</p>
                  <div className="flex items-center mt-1">
                    {getTrendIcon(-5)}
                    <span className="text-sm text-red-600 ml-1">-5%</span>
                  </div>
                </div>
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Response Time</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics?.monthly_metrics.avg_response_time}h</p>
                  <div className="flex items-center mt-1">
                    {getTrendIcon(-8)}
                    <span className="text-sm text-green-600 ml-1">-8%</span>
                  </div>
                </div>
                <Clock className="w-8 h-8 text-purple-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Satisfaction</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics?.monthly_metrics.patient_satisfaction}/5</p>
                  <div className="flex items-center mt-1">
                    {getTrendIcon(3)}
                    <span className="text-sm text-green-600 ml-1">+3%</span>
                  </div>
                </div>
                <Activity className="w-8 h-8 text-orange-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Growth Rate</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics?.monthly_metrics.growth_rate}%</p>
                  <div className="flex items-center mt-1">
                    {getTrendIcon(analytics?.monthly_metrics.growth_rate || 0)}
                    <span className="text-sm text-green-600 ml-1">This month</span>
                  </div>
                </div>
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Patient Trends Chart */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Patient Trends</h2>
                <select
                  value={selectedMetric}
                  onChange={(e) => setSelectedMetric(e.target.value)}
                  className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="patients">New Patients</option>
                  <option value="consultations">Consultations</option>
                  <option value="active">Active Patients</option>
                </select>
              </div>
              
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={analytics?.patient_trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  {selectedMetric === 'patients' && (
                    <Area
                      type="monotone"
                      dataKey="new_patients"
                      stroke="#3B82F6"
                      fill="#3B82F6"
                      fillOpacity={0.6}
                      name="New Patients"
                    />
                  )}
                  {selectedMetric === 'consultations' && (
                    <Area
                      type="monotone"
                      dataKey="total_consultations"
                      stroke="#10B981"
                      fill="#10B981"
                      fillOpacity={0.6}
                      name="Consultations"
                    />
                  )}
                  {selectedMetric === 'active' && (
                    <Area
                      type="monotone"
                      dataKey="active_patients"
                      stroke="#F59E0B"
                      fill="#F59E0B"
                      fillOpacity={0.6}
                      name="Active Patients"
                    />
                  )}
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Condition Distribution */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Condition Distribution</h2>
              
              <div className="flex items-center justify-center">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analytics?.condition_distribution}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="condition" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              
              <div className="mt-4 space-y-2">
                {analytics?.condition_distribution.map((condition, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: condition.color }}
                      ></div>
                      <span className="text-sm text-gray-600 dark:text-gray-300">{condition.condition}</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {condition.count} ({condition.percentage}%)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Insights and Recommendations */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">AI Insights & Recommendations</h2>
            
            <div className="space-y-4">
              {analytics?.recent_insights.map((insight) => (
                <div key={insight.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {getInsightIcon(insight.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium text-gray-900 dark:text-white">{insight.title}</h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getImpactColor(insight.impact)}`}>
                          {insight.impact} impact
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{insight.description}</p>
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                        {new Date(insight.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </Navigation>
  );
};

export default AnalyticsPage; 