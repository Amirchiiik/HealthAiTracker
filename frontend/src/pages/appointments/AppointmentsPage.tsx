import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Calendar,
  Clock,
  Plus,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  User,
  Stethoscope,
  MapPin,
  Phone,
  Video,
  CheckCircle,
  XCircle,
  AlertCircle,
  Edit,
  Trash2,
  Eye,
  MessageSquare,
  Bell,
  Download,
  Upload,
  RefreshCw,
  Users,
  CalendarDays,
  Timer,
  Star
} from 'lucide-react';
import Navigation from '../../components/layout/Navigation';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';

interface Appointment {
  id: number;
  patient_id: number;
  doctor_id: number;
  patient_name: string;
  doctor_name: string;
  doctor_specialization?: string;
  appointment_date: string;
  appointment_time: string;
  duration: number; // in minutes
  type: 'consultation' | 'follow-up' | 'emergency' | 'routine';
  status: 'scheduled' | 'confirmed' | 'in-progress' | 'completed' | 'cancelled' | 'no-show';
  location: 'in-person' | 'video-call' | 'phone-call';
  notes?: string;
  symptoms?: string;
  created_at: string;
  updated_at: string;
}

interface Doctor {
  id: number;
  full_name: string;
  specialization: string;
  rating: number;
  availability: string[];
  location: string;
}

interface TimeSlot {
  time: string;
  available: boolean;
  appointment?: Appointment;
}

const AppointmentsPage: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<'calendar' | 'list' | 'schedule'>('calendar');
  const [showNewAppointment, setShowNewAppointment] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [demoMode, setDemoMode] = useState(true);

  // Demo data
  const demoAppointments: Appointment[] = [
    {
      id: 1,
      patient_id: 1,
      doctor_id: 2,
      patient_name: 'John Smith',
      doctor_name: 'Dr. Amina Johnson',
      doctor_specialization: 'General Practice',
      appointment_date: '2024-01-25',
      appointment_time: '09:00',
      duration: 30,
      type: 'consultation',
      status: 'confirmed',
      location: 'in-person',
      notes: 'Regular checkup and blood pressure monitoring',
      symptoms: 'Mild headaches, fatigue',
      created_at: '2024-01-20T10:00:00Z',
      updated_at: '2024-01-22T14:30:00Z'
    },
    {
      id: 2,
      patient_id: 1,
      doctor_id: 3,
      patient_name: 'John Smith',
      doctor_name: 'Dr. Michael Chen',
      doctor_specialization: 'Cardiology',
      appointment_date: '2024-01-26',
      appointment_time: '14:30',
      duration: 45,
      type: 'follow-up',
      status: 'scheduled',
      location: 'video-call',
      notes: 'Follow-up on cardiac stress test results',
      created_at: '2024-01-21T09:15:00Z',
      updated_at: '2024-01-21T09:15:00Z'
    },
    {
      id: 3,
      patient_id: 2,
      doctor_id: 2,
      patient_name: 'Sarah Wilson',
      doctor_name: 'Dr. Amina Johnson',
      doctor_specialization: 'General Practice',
      appointment_date: '2024-01-25',
      appointment_time: '10:00',
      duration: 30,
      type: 'routine',
      status: 'completed',
      location: 'in-person',
      notes: 'Annual physical examination completed',
      created_at: '2024-01-18T16:20:00Z',
      updated_at: '2024-01-25T10:30:00Z'
    }
  ];

  const demoDoctors: Doctor[] = [
    {
      id: 2,
      full_name: 'Dr. Amina Johnson',
      specialization: 'General Practice',
      rating: 4.8,
      availability: ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00'],
      location: 'Medical Center, Room 201'
    },
    {
      id: 3,
      full_name: 'Dr. Michael Chen',
      specialization: 'Cardiology',
      rating: 4.9,
      availability: ['08:00', '09:30', '11:00', '14:30', '16:00'],
      location: 'Cardiac Wing, Room 305'
    },
    {
      id: 4,
      full_name: 'Dr. Sarah Williams',
      specialization: 'Internal Medicine',
      rating: 4.7,
      availability: ['09:00', '10:30', '13:00', '14:30', '15:30'],
      location: 'Internal Medicine, Room 150'
    }
  ];

  // Fetch appointments
  const { data: appointments, isLoading: appointmentsLoading } = useQuery({
    queryKey: ['appointments'],
    queryFn: async (): Promise<Appointment[]> => {
      if (demoMode) {
        return demoAppointments;
      }
      // Real API call would go here
      return [];
    }
  });

  // Fetch doctors for scheduling
  const { data: doctors } = useQuery({
    queryKey: ['doctors-for-appointments'],
    queryFn: async (): Promise<Doctor[]> => {
      if (demoMode) {
        return demoDoctors;
      }
      // Real API call would go here
      return [];
    }
  });

  // Create appointment mutation
  const createAppointmentMutation = useMutation({
    mutationFn: async (appointmentData: Partial<Appointment>) => {
      if (demoMode) {
        // Demo implementation
        await new Promise(resolve => setTimeout(resolve, 1000));
        return { ...appointmentData, id: Date.now() };
      }
      // Real API call would go here
      return appointmentData;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      setShowNewAppointment(false);
    }
  });

  // Update appointment mutation
  const updateAppointmentMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<Appointment> }) => {
      if (demoMode) {
        await new Promise(resolve => setTimeout(resolve, 500));
        return { id, ...data };
      }
      // Real API call would go here
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      setSelectedAppointment(null);
    }
  });

  // Filter appointments based on user role and filters
  const filteredAppointments = appointments?.filter(appointment => {
    // Role-based filtering
    if (user?.role === 'patient' && appointment.patient_id !== user.id) return false;
    if (user?.role === 'doctor' && appointment.doctor_id !== user.id) return false;

    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      const searchFields = [
        appointment.patient_name,
        appointment.doctor_name,
        appointment.doctor_specialization,
        appointment.notes,
        appointment.symptoms
      ].filter(Boolean);
      
      if (!searchFields.some(field => field?.toLowerCase().includes(searchLower))) {
        return false;
      }
    }

    // Status filter
    if (statusFilter !== 'all' && appointment.status !== statusFilter) return false;

    // Type filter
    if (typeFilter !== 'all' && appointment.type !== typeFilter) return false;

    return true;
  }) || [];

  // Get appointments for selected date
  const selectedDateAppointments = filteredAppointments.filter(
    appointment => appointment.appointment_date === selectedDate.toISOString().split('T')[0]
  );

  // Calendar navigation
  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + (direction === 'next' ? 1 : -1));
    setCurrentDate(newDate);
  };

  // Generate calendar days
  const generateCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    const days = [];
    const currentDateObj = new Date(startDate);

    for (let i = 0; i < 42; i++) {
      const dayAppointments = filteredAppointments.filter(
        appointment => appointment.appointment_date === currentDateObj.toISOString().split('T')[0]
      );

      days.push({
        date: new Date(currentDateObj),
        isCurrentMonth: currentDateObj.getMonth() === month,
        isToday: currentDateObj.toDateString() === new Date().toDateString(),
        isSelected: currentDateObj.toDateString() === selectedDate.toDateString(),
        appointments: dayAppointments
      });

      currentDateObj.setDate(currentDateObj.getDate() + 1);
    }

    return days;
  };

  const calendarDays = generateCalendarDays();

  // Status styling
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'in-progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'no-show': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'consultation': return <Stethoscope className="w-4 h-4" />;
      case 'follow-up': return <RefreshCw className="w-4 h-4" />;
      case 'emergency': return <AlertCircle className="w-4 h-4" />;
      case 'routine': return <CheckCircle className="w-4 h-4" />;
      default: return <Calendar className="w-4 h-4" />;
    }
  };

  const getLocationIcon = (location: string) => {
    switch (location) {
      case 'in-person': return <MapPin className="w-4 h-4" />;
      case 'video-call': return <Video className="w-4 h-4" />;
      case 'phone-call': return <Phone className="w-4 h-4" />;
      default: return <MapPin className="w-4 h-4" />;
    }
  };

  return (
    <Navigation>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-4">
                <Calendar className="w-8 h-8 text-blue-600" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Appointments
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {user?.role === 'patient' ? 'Manage your medical appointments' : 'Manage patient appointments'}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                {/* Demo Mode Toggle */}
                <button
                  onClick={() => setDemoMode(!demoMode)}
                  className={`px-3 py-1 text-xs rounded-full ${
                    demoMode ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {demoMode ? '🎭 Demo Mode' : '🔗 Live Mode'}
                </button>

                {/* View Mode Selector */}
                <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                  {['calendar', 'list', 'schedule'].map((mode) => (
                    <button
                      key={mode}
                      onClick={() => setViewMode(mode as any)}
                      className={`px-3 py-1 text-sm rounded-md capitalize transition-colors ${
                        viewMode === mode
                          ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                          : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                      }`}
                    >
                      {mode}
                    </button>
                  ))}
                </div>

                {/* New Appointment Button */}
                <button
                  onClick={() => setShowNewAppointment(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>New Appointment</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex flex-wrap items-center gap-4">
              {/* Search */}
              <div className="flex-1 min-w-64">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search appointments, doctors, or notes..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              {/* Status Filter */}
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Status</option>
                <option value="scheduled">Scheduled</option>
                <option value="confirmed">Confirmed</option>
                <option value="in-progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
                <option value="no-show">No Show</option>
              </select>

              {/* Type Filter */}
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Types</option>
                <option value="consultation">Consultation</option>
                <option value="follow-up">Follow-up</option>
                <option value="emergency">Emergency</option>
                <option value="routine">Routine</option>
              </select>

              {/* Results Count */}
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {filteredAppointments.length} appointment{filteredAppointments.length !== 1 ? 's' : ''}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {viewMode === 'calendar' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Calendar */}
              <div className="lg:col-span-2">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                  {/* Calendar Header */}
                  <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                    </h2>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => navigateMonth('prev')}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setCurrentDate(new Date())}
                        className="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-lg hover:bg-blue-200 transition-colors"
                      >
                        Today
                      </button>
                      <button
                        onClick={() => navigateMonth('next')}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Calendar Grid */}
                  <div className="p-4">
                    {/* Day Headers */}
                    <div className="grid grid-cols-7 gap-1 mb-2">
                      {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                        <div key={day} className="p-2 text-center text-sm font-medium text-gray-500 dark:text-gray-400">
                          {day}
                        </div>
                      ))}
                    </div>

                    {/* Calendar Days */}
                    <div className="grid grid-cols-7 gap-1">
                      {calendarDays.map((day, index) => (
                        <div
                          key={index}
                          onClick={() => setSelectedDate(day.date)}
                          className={`p-2 min-h-[80px] border border-gray-200 dark:border-gray-700 rounded-lg cursor-pointer transition-colors ${
                            day.isSelected
                              ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-500'
                              : day.isToday
                              ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500'
                              : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                          } ${
                            !day.isCurrentMonth ? 'opacity-50' : ''
                          }`}
                        >
                          <div className={`text-sm font-medium ${
                            day.isToday ? 'text-yellow-800 dark:text-yellow-200' :
                            day.isSelected ? 'text-blue-800 dark:text-blue-200' :
                            'text-gray-900 dark:text-white'
                          }`}>
                            {day.date.getDate()}
                          </div>
                          
                          {/* Appointment indicators */}
                          <div className="mt-1 space-y-1">
                            {day.appointments.slice(0, 2).map((appointment, idx) => (
                              <div
                                key={idx}
                                className={`text-xs px-1 py-0.5 rounded truncate ${getStatusColor(appointment.status)}`}
                              >
                                {appointment.appointment_time} {user?.role === 'doctor' ? appointment.patient_name : appointment.doctor_name}
                              </div>
                            ))}
                            {day.appointments.length > 2 && (
                              <div className="text-xs text-gray-500 dark:text-gray-400">
                                +{day.appointments.length - 2} more
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Selected Date Appointments */}
              <div className="lg:col-span-1">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {selectedDate.toLocaleDateString('en-US', { 
                        weekday: 'long', 
                        month: 'long', 
                        day: 'numeric' 
                      })}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {selectedDateAppointments.length} appointment{selectedDateAppointments.length !== 1 ? 's' : ''}
                    </p>
                  </div>

                  <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
                    {selectedDateAppointments.length === 0 ? (
                      <div className="text-center py-8">
                        <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <p className="text-gray-500 dark:text-gray-400">No appointments scheduled</p>
                        <button
                          onClick={() => setShowNewAppointment(true)}
                          className="mt-2 text-blue-600 hover:text-blue-700 text-sm"
                        >
                          Schedule an appointment
                        </button>
                      </div>
                    ) : (
                      selectedDateAppointments.map((appointment) => (
                        <div
                          key={appointment.id}
                          onClick={() => setSelectedAppointment(appointment)}
                          className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              {getTypeIcon(appointment.type)}
                              <span className="font-medium text-gray-900 dark:text-white">
                                {appointment.appointment_time}
                              </span>
                            </div>
                            <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(appointment.status)}`}>
                              {appointment.status}
                            </span>
                          </div>
                          
                          <div className="text-sm text-gray-600 dark:text-gray-300">
                            <div className="flex items-center space-x-1 mb-1">
                              <User className="w-3 h-3" />
                              <span>
                                {user?.role === 'doctor' ? appointment.patient_name : appointment.doctor_name}
                              </span>
                            </div>
                            {appointment.doctor_specialization && user?.role === 'patient' && (
                              <div className="flex items-center space-x-1 mb-1">
                                <Stethoscope className="w-3 h-3" />
                                <span>{appointment.doctor_specialization}</span>
                              </div>
                            )}
                            <div className="flex items-center space-x-1">
                              {getLocationIcon(appointment.location)}
                              <span className="capitalize">{appointment.location.replace('-', ' ')}</span>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {viewMode === 'list' && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Date & Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        {user?.role === 'doctor' ? 'Patient' : 'Doctor'}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Location
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {filteredAppointments.map((appointment) => (
                      <tr key={appointment.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {new Date(appointment.appointment_date).toLocaleDateString()}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {appointment.appointment_time} ({appointment.duration} min)
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10">
                              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                                {user?.role === 'doctor' ? (
                                  <User className="w-5 h-5 text-white" />
                                ) : (
                                  <Stethoscope className="w-5 h-5 text-white" />
                                )}
                              </div>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900 dark:text-white">
                                {user?.role === 'doctor' ? appointment.patient_name : appointment.doctor_name}
                              </div>
                              {appointment.doctor_specialization && user?.role === 'patient' && (
                                <div className="text-sm text-gray-500 dark:text-gray-400">
                                  {appointment.doctor_specialization}
                                </div>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center space-x-2">
                            {getTypeIcon(appointment.type)}
                            <span className="text-sm text-gray-900 dark:text-white capitalize">
                              {appointment.type}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(appointment.status)}`}>
                            {appointment.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center space-x-2">
                            {getLocationIcon(appointment.location)}
                            <span className="text-sm text-gray-900 dark:text-white capitalize">
                              {appointment.location.replace('-', ' ')}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => setSelectedAppointment(appointment)}
                              className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300">
                              <Edit className="w-4 h-4" />
                            </button>
                            <button className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {filteredAppointments.length === 0 && (
                <div className="text-center py-12">
                  <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No appointments found</h3>
                  <p className="text-gray-500 dark:text-gray-400 mb-4">
                    {searchTerm || statusFilter !== 'all' || typeFilter !== 'all'
                      ? 'Try adjusting your filters to see more appointments.'
                      : 'You don\'t have any appointments scheduled yet.'}
                  </p>
                  <button
                    onClick={() => setShowNewAppointment(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
                  >
                    Schedule Your First Appointment
                  </button>
                </div>
              )}
            </div>
          )}

          {viewMode === 'schedule' && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Time Slots */}
              <div className="lg:col-span-3">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Daily Schedule - {selectedDate.toLocaleDateString()}
                    </h3>
                  </div>
                  
                  <div className="p-4">
                    <div className="space-y-2">
                      {Array.from({ length: 12 }, (_, i) => {
                        const hour = i + 8; // 8 AM to 7 PM
                        const timeSlot = `${hour.toString().padStart(2, '0')}:00`;
                        const appointment = selectedDateAppointments.find(
                          apt => apt.appointment_time === timeSlot
                        );

                        return (
                          <div
                            key={timeSlot}
                            className={`p-3 border border-gray-200 dark:border-gray-700 rounded-lg ${
                              appointment ? 'bg-blue-50 dark:bg-blue-900/20' : 'bg-gray-50 dark:bg-gray-700'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <div className="text-sm font-medium text-gray-900 dark:text-white w-16">
                                  {timeSlot}
                                </div>
                                {appointment ? (
                                  <div className="flex items-center space-x-2">
                                    {getTypeIcon(appointment.type)}
                                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                                      {user?.role === 'doctor' ? appointment.patient_name : appointment.doctor_name}
                                    </span>
                                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(appointment.status)}`}>
                                      {appointment.status}
                                    </span>
                                  </div>
                                ) : (
                                  <span className="text-sm text-gray-500 dark:text-gray-400">Available</span>
                                )}
                              </div>
                              
                              {appointment ? (
                                <div className="flex items-center space-x-2">
                                  <button
                                    onClick={() => setSelectedAppointment(appointment)}
                                    className="text-blue-600 hover:text-blue-700 text-sm"
                                  >
                                    View Details
                                  </button>
                                </div>
                              ) : (
                                <button
                                  onClick={() => setShowNewAppointment(true)}
                                  className="text-blue-600 hover:text-blue-700 text-sm"
                                >
                                  Book Slot
                                </button>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>

              {/* Quick Stats */}
              <div className="lg:col-span-1 space-y-4">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Today's Summary</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">Total</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {selectedDateAppointments.length}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">Confirmed</span>
                      <span className="text-sm font-medium text-green-600">
                        {selectedDateAppointments.filter(apt => apt.status === 'confirmed').length}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">Pending</span>
                      <span className="text-sm font-medium text-yellow-600">
                        {selectedDateAppointments.filter(apt => apt.status === 'scheduled').length}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">Completed</span>
                      <span className="text-sm font-medium text-gray-600">
                        {selectedDateAppointments.filter(apt => apt.status === 'completed').length}
                      </span>
                    </div>
                  </div>
                </div>

                {user?.role === 'doctor' && (
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Quick Actions</h4>
                    <div className="space-y-2">
                      <button className="w-full text-left p-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded">
                        Block Time Slot
                      </button>
                      <button className="w-full text-left p-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded">
                        Set Availability
                      </button>
                      <button className="w-full text-left p-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded">
                        Emergency Slot
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Appointment Details Modal */}
        {selectedAppointment && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Appointment Details
                  </h3>
                  <button
                    onClick={() => setSelectedAppointment(null)}
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    <XCircle className="w-6 h-6" />
                  </button>
                </div>

                <div className="space-y-6">
                  {/* Basic Info */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Date & Time
                      </label>
                      <div className="text-sm text-gray-900 dark:text-white">
                        {new Date(selectedAppointment.appointment_date).toLocaleDateString()} at {selectedAppointment.appointment_time}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        Duration: {selectedAppointment.duration} minutes
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Status
                      </label>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(selectedAppointment.status)}`}>
                        {selectedAppointment.status}
                      </span>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {user?.role === 'doctor' ? 'Patient' : 'Doctor'}
                      </label>
                      <div className="text-sm text-gray-900 dark:text-white">
                        {user?.role === 'doctor' ? selectedAppointment.patient_name : selectedAppointment.doctor_name}
                      </div>
                      {selectedAppointment.doctor_specialization && user?.role === 'patient' && (
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {selectedAppointment.doctor_specialization}
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Type & Location
                      </label>
                      <div className="flex items-center space-x-2 text-sm text-gray-900 dark:text-white">
                        {getTypeIcon(selectedAppointment.type)}
                        <span className="capitalize">{selectedAppointment.type}</span>
                      </div>
                      <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {getLocationIcon(selectedAppointment.location)}
                        <span className="capitalize">{selectedAppointment.location.replace('-', ' ')}</span>
                      </div>
                    </div>
                  </div>

                  {/* Notes */}
                  {selectedAppointment.notes && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Notes
                      </label>
                      <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg text-sm text-gray-900 dark:text-white">
                        {selectedAppointment.notes}
                      </div>
                    </div>
                  )}

                  {/* Symptoms */}
                  {selectedAppointment.symptoms && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Symptoms
                      </label>
                      <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg text-sm text-gray-900 dark:text-white">
                        {selectedAppointment.symptoms}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                    {selectedAppointment.location === 'video-call' && (
                      <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                        <Video className="w-4 h-4" />
                        <span>Join Video Call</span>
                      </button>
                    )}
                    
                    <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      <MessageSquare className="w-4 h-4" />
                      <span>Send Message</span>
                    </button>

                    <button className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                      <Edit className="w-4 h-4" />
                      <span>Edit</span>
                    </button>

                    {selectedAppointment.status === 'scheduled' && (
                      <button className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                        <XCircle className="w-4 h-4" />
                        <span>Cancel</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* New Appointment Modal */}
        {showNewAppointment && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Schedule New Appointment
                  </h3>
                  <button
                    onClick={() => setShowNewAppointment(false)}
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    <XCircle className="w-6 h-6" />
                  </button>
                </div>

                <div className="space-y-6">
                  {user?.role === 'patient' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Select Doctor
                      </label>
                      <div className="space-y-2">
                        {doctors?.map((doctor) => (
                          <div
                            key={doctor.id}
                            className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                                  <Stethoscope className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                  <div className="font-medium text-gray-900 dark:text-white">
                                    {doctor.full_name}
                                  </div>
                                  <div className="text-sm text-gray-500 dark:text-gray-400">
                                    {doctor.specialization}
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <div className="flex items-center">
                                  {[...Array(5)].map((_, i) => (
                                    <Star
                                      key={i}
                                      className={`w-3 h-3 ${
                                        i < Math.floor(doctor.rating)
                                          ? 'text-yellow-400 fill-current'
                                          : 'text-gray-300'
                                      }`}
                                    />
                                  ))}
                                  <span className="text-xs text-gray-500 ml-1">{doctor.rating}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Date
                      </label>
                      <input
                        type="date"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Time
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                        <option value="">Select time</option>
                        <option value="09:00">9:00 AM</option>
                        <option value="10:00">10:00 AM</option>
                        <option value="11:00">11:00 AM</option>
                        <option value="14:00">2:00 PM</option>
                        <option value="15:00">3:00 PM</option>
                        <option value="16:00">4:00 PM</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Type
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                        <option value="consultation">Consultation</option>
                        <option value="follow-up">Follow-up</option>
                        <option value="routine">Routine Checkup</option>
                        <option value="emergency">Emergency</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Location
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                        <option value="in-person">In-Person</option>
                        <option value="video-call">Video Call</option>
                        <option value="phone-call">Phone Call</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Symptoms or Reason for Visit
                    </label>
                    <textarea
                      rows={3}
                      placeholder="Describe your symptoms or reason for the appointment..."
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Additional Notes
                    </label>
                    <textarea
                      rows={2}
                      placeholder="Any additional information for the doctor..."
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>

                  {demoMode && (
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200">
                      <p className="text-sm text-green-700 dark:text-green-300">
                        🎭 Demo Mode: This appointment will be created as a demo. Toggle to Live Mode for real scheduling.
                      </p>
                    </div>
                  )}

                  <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <button
                      onClick={() => setShowNewAppointment(false)}
                      className="px-4 py-2 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => {
                        // Demo appointment creation
                        if (demoMode) {
                          alert('Demo appointment scheduled successfully! 🎉');
                          setShowNewAppointment(false);
                        }
                      }}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Schedule Appointment
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Navigation>
  );
};

export default AppointmentsPage; 