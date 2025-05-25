import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Users,
  Search,
  Filter,
  Plus,
  Eye,
  MessageSquare,
  Calendar,
  FileText,
  AlertTriangle,
  CheckCircle,
  XCircle,
  AlertCircle,
  ChevronRight,
  MoreVertical,
  Download,
  Phone,
  Video,
  Mail,
  User as UserIcon,
  Activity,
  Clock,
  TrendingUp,
  TrendingDown,
  Heart
} from 'lucide-react';
import Navigation from '../../components/layout/Navigation';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

interface Patient {
  id: number;
  full_name: string;
  email: string;
  phone?: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  last_analysis: string;
  critical_metrics: number;
  total_analyses: number;
  last_message?: string;
  last_appointment?: string;
  status: 'critical' | 'warning' | 'normal';
  created_at: string;
  recent_activity: {
    type: string;
    timestamp: string;
    description: string;
  }[];
}

const PatientsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('name');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  // Fetch patients data
  const { data: patients, isLoading, error } = useQuery({
    queryKey: ['doctor-patients-detailed'],
    queryFn: async (): Promise<Patient[]> => {
      // Mock data for now - replace with actual API call
      return [
        {
          id: 1,
          full_name: 'Sarah Johnson',
          email: 'sarah.j@email.com',
          phone: '+1 (555) 123-4567',
          age: 45,
          gender: 'female',
          last_analysis: '2024-01-15',
          critical_metrics: 2,
          total_analyses: 5,
          last_message: 'Feeling dizzy after new medication',
          last_appointment: '2024-01-10',
          status: 'critical',
          created_at: '2024-01-01',
          recent_activity: [
            {
              type: 'analysis',
              timestamp: '2024-01-15T10:30:00Z',
              description: 'Uploaded blood test results'
            },
            {
              type: 'message',
              timestamp: '2024-01-14T14:20:00Z',
              description: 'Sent message about medication side effects'
            }
          ]
        },
        {
          id: 2,
          full_name: 'Michael Chen',
          email: 'michael.c@email.com',
          phone: '+1 (555) 987-6543',
          age: 38,
          gender: 'male',
          last_analysis: '2024-01-14',
          critical_metrics: 0,
          total_analyses: 3,
          last_message: 'Blood pressure looks good',
          last_appointment: '2024-01-12',
          status: 'normal',
          created_at: '2024-01-05',
          recent_activity: [
            {
              type: 'appointment',
              timestamp: '2024-01-12T09:00:00Z',
              description: 'Completed routine checkup'
            }
          ]
        },
        {
          id: 3,
          full_name: 'Emma Wilson',
          email: 'emma.w@email.com',
          phone: '+1 (555) 456-7890',
          age: 29,
          gender: 'female',
          last_analysis: '2024-01-13',
          critical_metrics: 1,
          total_analyses: 7,
          last_message: 'Question about lab results',
          last_appointment: '2024-01-08',
          status: 'warning',
          created_at: '2024-01-03',
          recent_activity: [
            {
              type: 'analysis',
              timestamp: '2024-01-13T16:45:00Z',
              description: 'Shared MRI scan results'
            }
          ]
        }
      ];
    }
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

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'normal':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const filteredPatients = patients?.filter(patient => {
    const matchesSearch = patient.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         patient.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || patient.status === filterStatus;
    return matchesSearch && matchesFilter;
  }).sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.full_name.localeCompare(b.full_name);
      case 'status':
        return a.status.localeCompare(b.status);
      case 'lastActivity':
        return new Date(b.last_analysis).getTime() - new Date(a.last_analysis).getTime();
      default:
        return 0;
    }
  });

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
                <Users className="w-8 h-8 mr-3 text-blue-600" />
                Patient Management
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Manage and monitor your patients' health
              </p>
            </div>
            
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
              <Plus className="w-4 h-4" />
              <span>Add Patient</span>
            </button>
          </div>

          {/* Filters and Search */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
              {/* Search */}
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search patients..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              
              <div className="flex items-center space-x-4">
                {/* Status Filter */}
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="all">All Status</option>
                  <option value="critical">Critical</option>
                  <option value="warning">Warning</option>
                  <option value="normal">Normal</option>
                </select>
                
                {/* Sort By */}
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="name">Sort by Name</option>
                  <option value="status">Sort by Status</option>
                  <option value="lastActivity">Sort by Activity</option>
                </select>
              </div>
            </div>
          </div>

          {/* Patients List */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Patients ({filteredPatients?.length || 0})
              </h2>
            </div>
            
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredPatients?.map((patient) => (
                <div
                  key={patient.id}
                  className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
                  onClick={() => {
                    setSelectedPatient(patient);
                    setShowDetails(true);
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      {/* Avatar */}
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                          <UserIcon className="w-6 h-6 text-white" />
                        </div>
                      </div>
                      
                      {/* Patient Info */}
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                            {patient.full_name}
                          </h3>
                          {getStatusIcon(patient.status)}
                          <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusBadge(patient.status)}`}>
                            {patient.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {patient.email} • {patient.age} years • {patient.gender}
                        </p>
                        <div className="flex items-center space-x-4 mt-1 text-xs text-gray-400 dark:text-gray-500">
                          <span>Last analysis: {formatDate(patient.last_analysis)}</span>
                          <span>•</span>
                          <span>{patient.total_analyses} total analyses</span>
                          {patient.critical_metrics > 0 && (
                            <>
                              <span>•</span>
                              <span className="text-red-500">{patient.critical_metrics} critical metrics</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // Navigate to chat
                        }}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-full transition-colors"
                        title="Send Message"
                      >
                        <MessageSquare className="w-4 h-4 text-gray-500" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // Schedule appointment
                        }}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-full transition-colors"
                        title="Schedule Appointment"
                      >
                        <Calendar className="w-4 h-4 text-gray-500" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // View medical records
                        }}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-full transition-colors"
                        title="View Records"
                      >
                        <FileText className="w-4 h-4 text-gray-500" />
                      </button>
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    </div>
                  </div>
                  
                  {/* Recent Activity Preview */}
                  {patient.last_message && (
                    <div className="mt-3 ml-16">
                      <p className="text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-600 px-3 py-2 rounded-lg">
                        Latest: "{patient.last_message}"
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Patient Details Modal */}
          {showDetails && selectedPatient && (
            <div className="fixed inset-0 z-50 overflow-y-auto">
              <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                <div className="fixed inset-0 transition-opacity" onClick={() => setShowDetails(false)}>
                  <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
                </div>
                
                <div className="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                  <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {selectedPatient.full_name}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Patient Details</p>
                  </div>
                  
                  <div className="px-6 py-4 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Email</label>
                        <p className="text-gray-900 dark:text-white">{selectedPatient.email}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Phone</label>
                        <p className="text-gray-900 dark:text-white">{selectedPatient.phone || 'N/A'}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Age</label>
                        <p className="text-gray-900 dark:text-white">{selectedPatient.age} years</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Gender</label>
                        <p className="text-gray-900 dark:text-white capitalize">{selectedPatient.gender}</p>
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Status</label>
                      <div className="flex items-center space-x-2 mt-1">
                        {getStatusIcon(selectedPatient.status)}
                        <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusBadge(selectedPatient.status)}`}>
                          {selectedPatient.status}
                        </span>
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Recent Activity</label>
                      <div className="mt-2 space-y-2">
                        {selectedPatient.recent_activity.map((activity, index) => (
                          <div key={index} className="text-sm text-gray-600 dark:text-gray-300">
                            <span className="font-medium">{activity.type}:</span> {activity.description}
                            <span className="text-xs text-gray-400 ml-2">
                              {new Date(activity.timestamp).toLocaleDateString()}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700 flex justify-end space-x-3">
                    <button
                      onClick={() => setShowDetails(false)}
                      className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    >
                      Close
                    </button>
                    <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg">
                      View Full Profile
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </Navigation>
  );
};

export default PatientsPage; 