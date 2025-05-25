import { apiClient, API_ENDPOINTS } from '../config/api';
import { AuthResponse, LoginRequest, RegisterRequest, User } from '../types';

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post(API_ENDPOINTS.LOGIN, credentials);
    return response.data;
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post(API_ENDPOINTS.REGISTER, data);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get(API_ENDPOINTS.ME);
    return response.data;
  },

  async updateProfile(profileData: Partial<User>): Promise<User> {
    const response = await apiClient.put(API_ENDPOINTS.UPDATE_PROFILE, profileData);
    return response.data;
  },
}; 