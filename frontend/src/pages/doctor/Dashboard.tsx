import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Stethoscope,
  Users,
  Calendar,
  MessageSquare,
  AlertTriangle,
  Activity,
  Clock,
  TrendingUp,
  TrendingDown,
  Heart,
  FileText,
  Bell,
  Search,
  Filter,
  Plus,
  Eye,
  Download,
  MoreVertical,
  UserCheck,
  Shield,
  Zap,
  BarChart3,
  PieChart,
  ArrowRight,
  Phone,
  Video,
  Mail,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  XCircle,
  User as UserIcon
} from 'lucide-react';
import Navigation from '../../components/layout/Navigation';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';
import { chatService } from '../../services/chatService';
import { apiClient } from '../../config/api';

interface PatientOverview {
  id: number;
  full_name: string;
  email: string;
  last_analysis: string;
  critical_metrics: number;
  total_analyses: number;
  last_message: string;
  status: 'critical' | 'warning' | 'normal';
  created_at: string;
}

interface DoctorStats {
  total_patients: number;
  active_conversations: number;
  today_appointments: number;
  critical_alerts: number;
  new_analyses: number;
  messages_unread: number;
}

interface RecentActivity {
  id: string;
  type: 'analysis' | 'message' | 'appointment' | 'alert';
  patient_name: string;
  patient_id: number;
  title: string;
  description: string;
  timestamp: string;
  priority: 'high' | 'medium' | 'low';
  status: 'new' | 'read' | 'completed';
}

const DoctorDashboard: React.FC = () => {
  const { user } = useAuth();
  const [selectedTimeframe, setSelectedTimeframe] = useState('today');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  // Fetch doctor statistics
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['doctor-stats'],
    queryFn: async (): Promise<DoctorStats> => {
      // Mock data for now - replace with actual API call
      return {
        total_patients: 47,
        active_conversations: 12,
        today_appointments: 8,
        critical_alerts: 3,
        new_analyses: 15,
        messages_unread: 7
      };
    },
    refetchInterval: 30000
  });

  // Fetch patient overview
  const { data: patients, isLoading: patientsLoading } = useQuery({
    queryKey: ['doctor-patients'],
    queryFn: async (): Promise<PatientOverview[]> => {
      // Mock data for now - replace with actual API call
      return [
        {
          id: 1,
          full_name: 'Sarah Johnson',
          email: 'sarah.j@email.com',
          last_analysis: '2024-01-15',
          critical_metrics: 2,
          total_analyses: 5,
          last_message: 'Feeling dizzy after new medication',
          status: 'critical',
          created_at: '2024-01-10'
        },
        {
          id: 2,
          full_name: 'Michael Chen',
          email: 'michael.c@email.com',
          last_analysis: '2024-01-14',
          critical_metrics: 0,
          total_analyses: 3,
          last_message: 'Blood pressure looks good',
          status: 'normal',
          created_at: '2024-01-12'
        },
        {
          id: 3,
          full_name: 'Emma Wilson',
          email: 'emma.w@email.com',
          last_analysis: '2024-01-13',
          critical_metrics: 1,
          total_analyses: 7,
          last_message: 'Question about lab results',
          status: 'warning',
          created_at: '2024-01-08'
        }
      ];
    }
  });

  // Fetch recent activities
  const { data: activities, isLoading: activitiesLoading } = useQuery({
    queryKey: ['doctor-activities'],
    queryFn: async (): Promise<RecentActivity[]> => {
      // Mock data for now - replace with actual API call
      return [
        {
          id: '1',
          type: 'analysis',
          patient_name: 'Sarah Johnson',
          patient_id: 1,
          title: 'New Blood Test Results',
          description: 'High cholesterol levels detected',
          timestamp: '2024-01-15T10:30:00Z',
          priority: 'high',
          status: 'new'
        },
        {
          id: '2',
          type: 'message',
          patient_name: 'Michael Chen',
          patient_id: 2,
          title: 'Patient Message',
          description: 'Asking about medication side effects',
          timestamp: '2024-01-15T09:15:00Z',
          priority: 'medium',
          status: 'new'
        },
        {
          id: '3',
          type: 'appointment',
          patient_name: 'Emma Wilson',
          patient_id: 3,
          title: 'Follow-up Consultation',
          description: 'Scheduled for today at 2:00 PM',
          timestamp: '2024-01-15T14:00:00Z',
          priority: 'medium',
          status: 'completed'
        }
      ];
    }
  });

  // Fetch conversations for quick chat access
  const { data: conversations } = useQuery({
    queryKey: ['doctor-conversations'],
    queryFn: chatService.getConversations
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'critical':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'normal':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      default:
        return <UserIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
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

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'analysis':
        return <FileText className="w-5 h-5 text-blue-500" />;
      case 'message':
        return <MessageSquare className="w-5 h-5 text-green-500" />;
      case 'appointment':
        return <Calendar className="w-5 h-5 text-purple-500" />;
      case 'alert':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      return `${Math.floor(diffInHours * 60)}m ago`;
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const filteredPatients = patients?.filter(patient => {
    const matchesSearch = patient.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         patient.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || patient.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  if (statsLoading || patientsLoading || activitiesLoading) {
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
                <Stethoscope className="w-8 h-8 mr-3 text-blue-600" />
                Doctor Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Welcome back, Dr. {user?.full_name?.split(' ')[0]}
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              {/* Quick Actions */}
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
                <Plus className="w-4 h-4" />
                <span>New Appointment</span>
              </button>
              <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
                <MessageSquare className="w-4 h-4" />
                <span>Start Chat</span>
              </button>
            </div>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Patients</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.total_patients}</p>
                </div>
                <Users className="w-8 h-8 text-blue-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Chats</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.active_conversations}</p>
                </div>
                <MessageSquare className="w-8 h-8 text-green-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Today's Appointments</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.today_appointments}</p>
                </div>
                <Calendar className="w-8 h-8 text-purple-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Critical Alerts</p>
                  <p className="text-2xl font-bold text-red-600">{stats?.critical_alerts}</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">New Analyses</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.new_analyses}</p>
                </div>
                <Activity className="w-8 h-8 text-orange-600" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Unread Messages</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.messages_unread}</p>
                </div>
                <Bell className="w-8 h-8 text-red-500" />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Patient Overview */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
                    <Users className="w-5 h-5 mr-2" />
                    Patient Overview
                  </h2>
                  <div className="flex items-center space-x-2">
                    {/* Search */}
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <input
                        type="text"
                        placeholder="Search patients..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    
                    {/* Filter */}
                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                      className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="all">All Status</option>
                      <option value="critical">Critical</option>
                      <option value="warning">Warning</option>
                      <option value="normal">Normal</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="max-h-96 overflow-y-auto">
                {filteredPatients?.map((patient) => (
                  <div key={patient.id} className="p-4 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                            <UserIcon className="w-5 h-5 text-white" />
                          </div>
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <h3 className="font-medium text-gray-900 dark:text-white">{patient.full_name}</h3>
                            {getStatusIcon(patient.status)}
                          </div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{patient.email}</p>
                          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                            Last analysis: {new Date(patient.last_analysis).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {patient.critical_metrics > 0 && (
                          <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                            {patient.critical_metrics} critical
                          </span>
                        )}
                        <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-full transition-colors">
                          <ChevronRight className="w-4 h-4 text-gray-500" />
                        </button>
                      </div>
                    </div>
                    
                    {patient.last_message && (
                      <div className="mt-2 ml-13">
                        <p className="text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-600 px-3 py-2 rounded-lg">
                          "{patient.last_message}"
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Recent Activity
                </h2>
              </div>
              
              <div className="max-h-96 overflow-y-auto">
                {activities?.map((activity) => (
                  <div key={activity.id} className="p-4 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        {getActivityIcon(activity.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-gray-900 dark:text-white">{activity.title}</p>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(activity.priority)}`}>
                            {activity.priority}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-300">{activity.patient_name}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{activity.description}</p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">{formatTime(activity.timestamp)}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Actions Panel */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <Zap className="w-5 h-5 mr-2" />
              Quick Actions
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <button className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-left">
                <MessageSquare className="w-8 h-8 text-blue-600 mb-2" />
                <h3 className="font-medium text-gray-900 dark:text-white">View All Chats</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Access patient conversations</p>
              </button>
              
              <button className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-left">
                <Calendar className="w-8 h-8 text-purple-600 mb-2" />
                <h3 className="font-medium text-gray-900 dark:text-white">Schedule Appointment</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Book new consultation</p>
              </button>
              
              <button className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-left">
                <FileText className="w-8 h-8 text-green-600 mb-2" />
                <h3 className="font-medium text-gray-900 dark:text-white">Review Analyses</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Check new patient results</p>
              </button>
              
              <button className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-left">
                <BarChart3 className="w-8 h-8 text-orange-600 mb-2" />
                <h3 className="font-medium text-gray-900 dark:text-white">Practice Analytics</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">View performance metrics</p>
              </button>
            </div>
          </div>

        </div>
      </div>
    </Navigation>
  );
};

export default DoctorDashboard; 