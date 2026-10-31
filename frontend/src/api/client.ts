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
  IntentChatResponse,
  CalculateExpiryRequest,
  CalculateExpiryResponse,
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

// -----------------------------------------------------------------------------
// DONATION APIS
// -----------------------------------------------------------------------------
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
  const res = await api.get('/donations/my');
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

export const calculateExpiryAuto = async (
  payload: CalculateExpiryRequest
): Promise<CalculateExpiryResponse> => {
  const res = await api.post('/donations/calculate-expiry', payload);
  return res.data;
};

// -----------------------------------------------------------------------------
// REQUEST APIS
// -----------------------------------------------------------------------------
export const createPickupRequest = async (data: {
  batch_id: number;
  requested_quantity?: number;
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

// -----------------------------------------------------------------------------
// VOLUNTEER APIS
// -----------------------------------------------------------------------------
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

// -----------------------------------------------------------------------------
// DONATION PHOTO UPLOAD (Ordinary food photography display)
// -----------------------------------------------------------------------------
export const uploadDonationImage = async (file: File): Promise<{ image_url: string }> => {
  const formData = new FormData();
  formData.append('image', file);
  const res = await api.post('/donations/upload-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

// -----------------------------------------------------------------------------
// AI APIS (Hosted Gemma 4 via Gemini API)
// -----------------------------------------------------------------------------
export const getAIStatus = async (): Promise<AIStatus> => {
  const res = await api.get('/ai/status');
  return res.data;
};

export const categorizeFoodAI = async (
  food_name: string,
  food_description?: string
): Promise<FoodCategorizationResult> => {
  const res = await api.post('/ai/categorize-food', { food_name, description: food_description });
  return res.data;
};

export const sendAIChatMessage = async (
  message: string,
  history: Array<{ role: string; content: string }> = [],
  confirmedAction?: boolean,
  pendingActionData?: any
): Promise<IntentChatResponse> => {
  const res = await api.post('/ai/chat', {
    message,
    history,
    confirmed_action: confirmedAction,
    pending_action_data: pendingActionData,
  });
  return res.data;
};

export const getSmartMatchesAI = async (
  ngo_name?: string,
  ngo_requirements?: string
): Promise<SmartMatchResult> => {
  const res = await api.get('/ai/match-food');
  return {
    recommendations: res.data || [],
    summary: 'Ranked by bacterial holding risk and distribution urgency.',
  };
};

export const getPrioritizedTasksAI = async (): Promise<PrioritizedTaskResult> => {
  const res = await api.get('/ai/prioritize-tasks');
  const items = (res.data || []).map((t: any) => ({
    request_id: t.request_id,
    food_name: t.food_name,
    quantity: t.quantity,
    unit: t.unit,
    pickup_address: t.pickup_address,
    ngo_name: t.ngo_name,
    priority_level: t.urgency_badge.includes('URGENT') ? 'urgent' : t.urgency_badge.includes('TODAY') ? 'high' : 'standard',
    reason: t.priority_reason,
    estimated_minutes_left: t.remaining_minutes,
  }));
  return { prioritized_tasks: items };
};

// -----------------------------------------------------------------------------
// DASHBOARD & STATS
// -----------------------------------------------------------------------------
export const getDashboardStats = async (): Promise<DonorStats | NGOStats | VolunteerStats> => {
  const res = await api.get('/dashboard/stats');
  return res.data;
};

export const getPublicImpactSummary = async () => {
  const res = await api.get('/dashboard/public-summary');
  return res.data;
};

// -----------------------------------------------------------------------------
// NOTIFICATIONS
// -----------------------------------------------------------------------------
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

// -----------------------------------------------------------------------------
// FAVORITES / BOOKMARKS (In-browser Persistent Storage for NGOs)
// -----------------------------------------------------------------------------
const FAVORITES_KEY = 'cfrn_favorite_batches';

export const getFavorites = (): number[] => {
  try {
    const raw = localStorage.getItem(FAVORITES_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
};

export const toggleFavorite = (batchId: number): boolean => {
  const current = getFavorites();
  let updated: number[];
  const exists = current.includes(batchId);
  if (exists) {
    updated = current.filter((id) => id !== batchId);
  } else {
    updated = [...current, batchId];
  }
  localStorage.setItem(FAVORITES_KEY, JSON.stringify(updated));
  return !exists;
};

export const isFavorited = (batchId: number): boolean => {
  return getFavorites().includes(batchId);
};

export default api;
