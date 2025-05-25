import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Eye, EyeOff, Heart, Stethoscope, User, UserCheck } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { RegisterRequest } from '../../types';

const RegisterPage: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterRequest & { confirmPassword: string }>();

  const watchedPassword = watch('password');
  const watchedRole = watch('role', 'patient');

  const onSubmit = async (data: RegisterRequest & { confirmPassword: string }) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const { confirmPassword, ...registerData } = data;
      await registerUser(registerData);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center items-center space-x-2 mb-4">
            <div className="bg-primary-600 p-3 rounded-full">
              <Heart className="w-8 h-8 text-white" />
            </div>
            <Stethoscope className="w-8 h-8 text-primary-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            Join AI Health Tracker
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Create your account to get started
          </p>
        </div>

        <div className="card p-6 sm:p-8 space-y-6">
          {error && (
            <div className="bg-error-50 border border-error-200 text-error-600 px-4 py-3 rounded-md text-sm">
              {error}
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            {/* Role Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                I am a...
              </label>
              <div className="grid grid-cols-2 gap-3">
                <label className={`relative flex items-center space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  watchedRole === 'patient' 
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                    : 'border-gray-200 hover:border-gray-300 dark:border-gray-600'
                }`}>
                  <input
                    {...register('role', { required: 'Please select your role' })}
                    type="radio"
                    value="patient"
                    className="sr-only"
                  />
                  <User className={`w-6 h-6 ${watchedRole === 'patient' ? 'text-primary-600' : 'text-gray-400'}`} />
                  <span className={`font-medium ${watchedRole === 'patient' ? 'text-primary-700 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300'}`}>
                    Patient
                  </span>
                </label>
                
                <label className={`relative flex items-center space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  watchedRole === 'doctor' 
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                    : 'border-gray-200 hover:border-gray-300 dark:border-gray-600'
                }`}>
                  <input
                    {...register('role', { required: 'Please select your role' })}
                    type="radio"
                    value="doctor"
                    className="sr-only"
                  />
                  <UserCheck className={`w-6 h-6 ${watchedRole === 'doctor' ? 'text-primary-600' : 'text-gray-400'}`} />
                  <span className={`font-medium ${watchedRole === 'doctor' ? 'text-primary-700 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300'}`}>
                    Doctor
                  </span>
                </label>
              </div>
              {errors.role && (
                <p className="mt-1 text-sm text-error-600">{errors.role.message}</p>
              )}
            </div>

            {/* Basic Info */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Full Name
              </label>
              <input
                {...register('full_name', { 
                  required: 'Full name is required',
                  minLength: { value: 2, message: 'Full name must be at least 2 characters' }
                })}
                type="text"
                className="input"
                placeholder="John Doe"
                disabled={isLoading}
              />
              {errors.full_name && (
                <p className="mt-1 text-sm text-error-600">{errors.full_name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email
              </label>
              <input
                {...register('email', { 
                  required: 'Email is required',
                  pattern: { value: /^\S+@\S+\.\S+$/, message: 'Please enter a valid email address' }
                })}
                type="email"
                className="input"
                placeholder="john@example.com"
                disabled={isLoading}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-error-600">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Password
              </label>
              <div className="relative">
                <input
                  {...register('password', { 
                    required: 'Password is required',
                    minLength: { value: 8, message: 'Password must be at least 8 characters' },
                    pattern: { 
                      value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                      message: 'Password must contain at least one uppercase letter, one lowercase letter, and one number'
                    }
                  })}
                  type={showPassword ? 'text' : 'password'}
                  className="input pr-10"
                  placeholder="Create a strong password"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-error-600">{errors.password.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirm Password
              </label>
              <div className="relative">
                <input
                  {...register('confirmPassword', { 
                    required: 'Please confirm your password',
                    validate: value => value === watchedPassword || 'Passwords do not match'
                  })}
                  type={showConfirmPassword ? 'text' : 'password'}
                  className="input pr-10"
                  placeholder="Confirm your password"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  disabled={isLoading}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-error-600">{errors.confirmPassword.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full flex items-center justify-center space-x-2 py-3"
            >
              {isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <span>Create Account</span>
              )}
            </button>
          </form>

          <div className="text-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Already have an account?{' '}
            </span>
            <Link
              to="/login"
              className="text-sm font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400"
            >
              Sign in
            </Link>
          </div>
        </div>

        <div className="text-center text-xs text-gray-500 dark:text-gray-400">
          <p>© 2024 AI Health Tracker. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage; 