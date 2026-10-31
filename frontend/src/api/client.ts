import axios from 'axios';
import {
  FoodBatch,
  PickupRequest,
  AppNotification,
  DonorStats,
  NGOStats,
  VolunteerStats,
  FoodCategorizationResult,
  SmartMatchResult,
  PrioritizedTaskResult,
  AIStatus,
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    return Promise.reject(error);
  }
);

// Donation APIs
export const getDonations = async (params?: {
  status?: string;
  category?: string;
  search?: string;
  only_available?: boolean;
}): Promise<FoodBatch[]> => {
  const res = await api.get('/donations', { params });
  return res.data;
};

export const getMyDonations = async (): Promise<FoodBatch[]> => {
  const res = await api.get('/donations/my/list');
  return res.data;
};

export const getDonationById = async (batchId: number): Promise<FoodBatch> => {
  const res = await api.get(`/donations/${batchId}`);
  return res.data;
};

export const createDonation = async (data: any): Promise<FoodBatch> => {
  const res = await api.post('/donations', data);
  return res.data;
};

export const updateDonation = async (batchId: number, data: any): Promise<FoodBatch> => {
  const res = await api.put(`/donations/${batchId}`, data);
  return res.data;
};

export const cancelDonation = async (batchId: number): Promise<FoodBatch> => {
  const res = await api.post(`/donations/${batchId}/cancel`);
  return res.data;
};

// Request APIs
export const createPickupRequest = async (data: {
  batch_id: number;
  requested_quantity: number;
  notes?: string;
}): Promise<PickupRequest> => {
  const res = await api.post('/requests', data);
  return res.data;
};

export const getMyRequests = async (): Promise<PickupRequest[]> => {
  const res = await api.get('/requests/my');
  return res.data;
};

export const getRequestById = async (requestId: number): Promise<PickupRequest> => {
  const res = await api.get(`/requests/${requestId}`);
  return res.data;
};

export const cancelPickupRequest = async (requestId: number): Promise<PickupRequest> => {
  const res = await api.post(`/requests/${requestId}/cancel`);
  return res.data;
};

// Volunteer APIs
export const getAvailableTasks = async (): Promise<PickupRequest[]> => {
  const res = await api.get('/volunteer/tasks/available');
  return res.data;
};

export const claimTask = async (requestId: number): Promise<PickupRequest> => {
  const res = await api.post(`/volunteer/tasks/${requestId}/claim`);
  return res.data;
};

export const getAssignedTasks = async (): Promise<PickupRequest[]> => {
  const res = await api.get('/volunteer/tasks/assigned');
  return res.data;
};

export const getDeliveryHistory = async (): Promise<PickupRequest[]> => {
  const res = await api.get('/volunteer/tasks/history');
  return res.data;
};

export const collectFood = async (requestId: number, notes?: string): Promise<PickupRequest> => {
  const res = await api.post(`/volunteer/tasks/${requestId}/collect`, { notes });
  return res.data;
};

export const deliverFood = async (requestId: number, notes?: string): Promise<PickupRequest> => {
  const res = await api.post(`/volunteer/tasks/${requestId}/deliver`, { notes });
  return res.data;
};

export const updateAvailability = async (status: 'available' | 'busy' | 'offline') => {
  const res = await api.put('/volunteer/availability', { status });
  return res.data;
};

// AI APIs (Hosted Gemma 4)
export const getAIStatus = async (): Promise<AIStatus> => {
  const res = await api.get('/ai/status');
  return res.data;
};

export const categorizeFoodAI = async (
  food_name: string,
  food_description?: string
): Promise<FoodCategorizationResult> => {
  const res = await api.post('/ai/categorize-food', { food_name, food_description });
  return res.data;
};

export const sendAIChatMessage = async (
  message: string,
  history: Array<{ role: string; content: string }> = [],
  context?: Record<string, any>
): Promise<{ reply: string; sources?: string[] }> => {
  const res = await api.post('/ai/chat', { message, history, context });
  return res.data;
};

export const getSmartMatchesAI = async (
  ngo_name?: string,
  ngo_requirements?: string
): Promise<SmartMatchResult> => {
  const res = await api.post('/ai/match-food', { ngo_name, ngo_requirements });
  return res.data;
};

export const getPrioritizedTasksAI = async (
  volunteer_location?: string
): Promise<PrioritizedTaskResult> => {
  const res = await api.post('/ai/prioritize-tasks', { volunteer_location });
  return res.data;
};

// Dashboard & Stats
export const getDashboardStats = async (): Promise<DonorStats | NGOStats | VolunteerStats> => {
  const res = await api.get('/dashboard/stats');
  return res.data;
};

export const getPublicImpactSummary = async () => {
  const res = await api.get('/dashboard/public-summary');
  return res.data;
};

// Notifications
export const getNotifications = async (): Promise<AppNotification[]> => {
  const res = await api.get('/notifications');
  return res.data;
};

export const markNotificationRead = async (notificationId: number) => {
  const res = await api.patch(`/notifications/${notificationId}/read`);
  return res.data;
};

export const markAllNotificationsRead = async () => {
  const res = await api.patch('/notifications/read-all');
  return res.data;
};

export default api;
