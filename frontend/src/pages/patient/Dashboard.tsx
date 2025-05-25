import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Heart, 
  Upload, 
  Calendar, 
  MessageSquare, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Activity,
  FileText,
  ArrowRight,
  Plus
} from 'lucide-react';
import Navigation from '../../components/layout/Navigation';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';
import { healthService } from '../../services/healthService';
import { format } from 'date-fns';

const PatientDashboard: React.FC = () => {
  const { user } = useAuth();
  const [greeting, setGreeting] = useState('');

  // Get current time-based greeting
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good morning');
    else if (hour < 17) setGreeting('Good afternoon');
    else setGreeting('Good evening');
  }, []);

  // Fetch user data
  const { data: analyses, isLoading: analysesLoading } = useQuery({
    queryKey: ['user-analyses'],
    queryFn: healthService.getUserAnalyses,
  });

  // Temporarily disable recommendations until we fix the interface
  // const { data: recommendations, isLoading: recommendationsLoading } = useQuery({
  //   queryKey: ['agent-recommendations'],
  //   queryFn: healthService.getAgentRecommendations,
  // });

  const latestAnalysis = analyses ? healthService.getLatestAnalysis(analyses) : null;
  // const highPriorityRecommendations = recommendations 
  //   ? healthService.getHighPriorityRecommendations(recommendations) 
  //   : [];
  const highPriorityRecommendations: any[] = [];

  const quickActions = [
    {
      title: 'Upload Medical File',
      description: 'Upload lab results, reports, or prescriptions',
      icon: Upload,
      href: '/upload',
      color: 'bg-blue-500 hover:bg-blue-600',
    },
    {
      title: 'Book Appointment',
      description: 'Schedule a consultation with a doctor',
      icon: Calendar,
      href: '/appointments',
      color: 'bg-green-500 hover:bg-green-600',
    },
    {
      title: 'Chat with Doctor',
      description: 'Send messages to your healthcare provider',
      icon: MessageSquare,
      href: '/chat',
      color: 'bg-purple-500 hover:bg-purple-600',
    },
    {
      title: 'View History',
      description: 'See your medical history and analyses',
      icon: FileText,
      href: '/history',
      color: 'bg-orange-500 hover:bg-orange-600',
    },
  ];

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    subtitle?: string;
    icon: any;
    color: string;
    trend?: 'up' | 'down' | 'stable';
  }> = ({ title, value, subtitle, icon: Icon, color, trend }) => (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
      {trend && (
        <div className="mt-4 flex items-center">
          <TrendingUp className={`w-4 h-4 mr-1 ${
            trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-gray-400'
          }`} />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {trend === 'up' ? 'Improving' : trend === 'down' ? 'Declining' : 'Stable'}
          </span>
        </div>
      )}
    </div>
  );

  return (
    <Navigation>
      <div className="p-4 lg:p-8 pb-20 lg:pb-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {greeting}, {user?.full_name}!
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Here's your health overview for today, {format(new Date(), 'MMMM d, yyyy')}
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Link
                key={index}
                to={action.href}
                className={`${action.color} text-white p-4 rounded-lg transition-colors duration-200 hover:shadow-lg group`}
              >
                <div className="flex flex-col items-center text-center space-y-2">
                  <Icon className="w-8 h-8" />
                  <span className="text-sm font-medium">{action.title}</span>
                  <span className="text-xs opacity-90 hidden lg:block">{action.description}</span>
                </div>
              </Link>
            );
          })}
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Health Overview */}
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Health Overview
              </h2>
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                <StatCard
                  title="Total Analyses"
                  value={analyses?.length || 0}
                  icon={FileText}
                  color="bg-blue-500"
                />
                <StatCard
                  title="Risk Level"
                  value="N/A"
                  icon={Activity}
                  color="bg-gray-500"
                />
                <StatCard
                  title="Recommendations"
                  value={0}
                  icon={AlertTriangle}
                  subtitle="0 pending"
                  color="bg-purple-500"
                />
              </div>
            </div>

            {/* Recent Analysis */}
            {latestAnalysis && (
              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Latest Analysis
                  </h3>
                  <span className="px-3 py-1 rounded-full text-xs font-medium border bg-gray-50 text-gray-600 border-gray-200">
                    Analysis Complete
                  </span>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">File Name</p>
                    <p className="font-medium text-gray-900 dark:text-white">{latestAnalysis.filename || 'Text Analysis'}</p>
                  </div>
                  
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Summary</p>
                    <p className="text-gray-900 dark:text-white">{latestAnalysis.overall_summary || 'Analysis completed successfully'}</p>
                  </div>
                  
                  {latestAnalysis.metrics && latestAnalysis.metrics.length > 0 && (
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Metrics Found</p>
                      <div className="flex flex-wrap gap-2">
                        {latestAnalysis.metrics.slice(0, 3).map((metric, index) => (
                          <span key={index} className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">
                            {typeof metric === 'object' ? metric.name || `Metric ${index + 1}` : metric}
                          </span>
                        ))}
                        {latestAnalysis.metrics.length > 3 && (
                          <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                            +{latestAnalysis.metrics.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {format(new Date(latestAnalysis.created_at), 'MMM d, yyyy')}
                    </span>
                    <Link
                      to="/history"
                      className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center space-x-1"
                    >
                      <span>View All</span>
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </div>
            )}

            {/* No Analysis State */}
            {!analysesLoading && (!analyses || analyses.length === 0) && (
              <div className="card p-6 text-center">
                <Heart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No health data yet
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Upload your first medical file to get AI-powered health insights
                </p>
                <Link
                  to="/upload"
                  className="btn-primary inline-flex items-center space-x-2"
                >
                  <Upload className="w-4 h-4" />
                  <span>Upload Medical File</span>
                </Link>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Urgent Recommendations */}
            {highPriorityRecommendations.length > 0 && (
              <div className="card p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <AlertTriangle className="w-5 h-5 text-orange-500" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Urgent Actions
                  </h3>
                </div>
                
                <div className="space-y-3">
                  {highPriorityRecommendations.slice(0, 3).map((rec, index) => (
                    <div key={rec.id} className="border-l-4 border-orange-400 pl-4">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                          {rec.title}
                        </h4>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          healthService.getPriorityColor(rec.priority)
                        }`}>
                          {rec.priority}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {rec.description}
                      </p>
                    </div>
                  ))}
                </div>
                
                <Link
                  to="/history"
                  className="block mt-4 text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  View all recommendations →
                </Link>
              </div>
            )}

            {/* Quick Stats */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Quick Stats
              </h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Files Uploaded</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {analyses?.length || 0}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Last Upload</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {latestAnalysis 
                      ? format(new Date(latestAnalysis.created_at), 'MMM d')
                      : 'Never'
                    }
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Active Recommendations</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    0
                  </span>
                </div>
              </div>
            </div>

            {/* Next Appointment */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Upcoming
              </h3>
              
              <div className="text-center py-4">
                <Calendar className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  No upcoming appointments
                </p>
                <Link
                  to="/appointments"
                  className="btn-outline mt-3 text-sm inline-flex items-center space-x-1"
                >
                  <Plus className="w-4 h-4" />
                  <span>Book Appointment</span>
                </Link>
              </div>
            </div>

            {/* Pending Recommendations */}
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Pending Recommendations
                </h3>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  0 total
                </span>
              </div>
              
              <div className="space-y-3">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  No pending recommendations at this time
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Loading States */}
        {analysesLoading && (
          <div className="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
              <LoadingSpinner size="lg" />
              <p className="text-center mt-4 text-gray-600 dark:text-gray-400">
                Loading your health data...
              </p>
            </div>
          </div>
        )}
      </div>
    </Navigation>
  );
};

export default PatientDashboard; 