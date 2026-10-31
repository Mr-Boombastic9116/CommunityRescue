export type UserRole = 'donor' | 'ngo' | 'volunteer';

export interface User {
  user_id: number;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  profile?: {
    donor_id?: number;
    ngo_id?: number;
    volunteer_id?: number;
    organization_name?: string;
    phone?: string;
    address?: string;
    latitude?: number;
    longitude?: number;
    availability_status?: 'available' | 'busy' | 'offline';
  };
}

export interface FoodBatch {
  batch_id: number;
  donor_id: number;
  donor_name?: string;
  donor_phone?: string;
  food_name: string;
  food_description?: string;
  food_category: string;
  quantity: number;
  unit: string;
  donated_quantity?: number;
  allocated_quantity?: number;
  remaining_quantity?: number;
  prepared_at: string;
  expiry_time: string;
  user_expiry_time?: string;
  effective_expiry_time?: string;
  packaging_expiry_time?: string;
  storage_condition?: 'ambient' | 'refrigerated' | 'frozen' | 'hot_holding';
  storage_temperature?: number;
  expiry_validation_status?: 'valid' | 'verified' | 'adjusted' | 'requires_verification' | 'pending_verification' | 'manual_verification_required';
  expiry_rule_applied?: string;
  expiry_adjustment_reason?: string;
  image_url?: string;
  food_status: 'available' | 'partially_reserved' | 'reserved' | 'requested' | 'assigned' | 'collected' | 'delivered' | 'expired' | 'cancelled' | 'pending_verification';
  pickup_address: string;
  latitude?: number;
  longitude?: number;
  created_at: string;
  updated_at: string;
  remaining_hours?: number;
  is_close_to_expiry: boolean;
  urgency_level?: 'safe' | 'approaching' | 'urgent' | 'expired';
  max_holding_hours?: number;
  approved_maximum_expiry?: string;
}

export interface PickupRequest {
  request_id: number;
  batch_id: number;
  ngo_id: number;
  ngo_name?: string;
  ngo_phone?: string;
  ngo_address?: string;
  volunteer_id?: number;
  volunteer_name?: string;
  volunteer_phone?: string;
  requested_quantity: number;
  unit: string;
  request_status: 'requested' | 'assigned' | 'collected' | 'delivered' | 'cancelled' | 'rejected';
  requested_at: string;
  assigned_at?: string;
  collected_at?: string;
  completed_at?: string;
  updated_at: string;
  food_batch?: FoodBatch;
}

export interface DeliveryLog {
  log_id: number;
  request_id: number;
  performed_by_user_id?: number;
  performer_name?: string;
  action: string;
  notes?: string;
  logged_at: string;
}

export interface AppNotification {
  notification_id: number;
  user_id: number;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface DonorStats {
  role: 'donor';
  total_donations: number;
  available_donations: number;
  in_progress_donations: number;
  completed_donations: number;
  expired_donations: number;
  total_quantity_donated: number;
  recent_activities: Array<{
    id: number;
    title: string;
    status: string;
    time: string;
    details: string;
  }>;
}

export interface NGOStats {
  role: 'ngo';
  total_requests: number;
  pending_requests: number;
  assigned_requests: number;
  collected_requests: number;
  completed_requests: number;
  cancelled_requests: number;
  total_quantity_received: number;
  recent_activities: Array<{
    id: number;
    title: string;
    status: string;
    time: string;
    details: string;
  }>;
}

export interface VolunteerStats {
  role: 'volunteer';
  total_claimed: number;
  assigned_tasks: number;
  collected_tasks: number;
  completed_tasks: number;
  availability_status: 'available' | 'busy' | 'offline';
  recent_activities: Array<{
    id: number;
    title: string;
    status: string;
    time: string;
    details: string;
  }>;
}

// AI Interfaces
export interface FoodCategorizationResult {
  normalized_name?: string;
  suggested_category?: string;
  category?: string;
  suggested_storage?: 'ambient' | 'refrigerated' | 'frozen' | 'hot_holding';
  storage_condition?: 'ambient' | 'refrigerated' | 'frozen' | 'hot_holding';
  shelf_life_hours?: number;
  dietary_tags?: string[];
  allergens?: string[];
  fssai_guideline?: string;
  concise_description?: string;
  confidence?: number;
}

export interface ChatMessage {
  id?: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  parsed_intent?: ChatbotParsedIntent;
  tool_executed?: string;
  confirmation_prompt?: string;
}

export interface SmartMatchRecommendation {
  batch_id: number;
  food_name: string;
  food_category: string;
  remaining_quantity: number;
  unit: string;
  urgency: 'critical' | 'high' | 'medium' | 'low';
  match_score: number;
  reason: string;
  distance_km?: number;
}

export interface SmartMatchResult {
  recommendations: SmartMatchRecommendation[];
  summary: string;
}

export interface PrioritizedTask {
  request_id: number;
  food_name: string;
  quantity: number;
  unit: string;
  pickup_address: string;
  ngo_name: string;
  priority_level: 'urgent' | 'high' | 'standard';
  reason: string;
  estimated_minutes_left?: number;
}

export interface PrioritizedTaskResult {
  prioritized_tasks: PrioritizedTask[];
}

export interface AIStatus {
  status: string;
  model: string;
  provider: string;
  ai_available?: boolean;
}

// Intent-Aware Chatbot
export interface ChatbotParsedIntent {
  intent: string;
  question_type: string;
  action?: string | null;
  main_entity?: string | null;
  extracted_entities: Record<string, any>;
  quantity?: number | null;
  unit?: string | null;
  relevant_ids: number[];
  missing_information: string[];
  backend_action_needed: boolean;
  confirmation_required: boolean;
  confirmation_prompt?: string | null;
}

export interface IntentChatResponse {
  reply: string;
  parsed_intent: ChatbotParsedIntent;
  tool_executed?: string | null;
  tool_results_count?: number | null;
  role: string;
  user_name: string;
  ai_powered: boolean;
}

// Expiry Calculation Workflow
export interface CalculateExpiryRequest {
  food_name: string;
  food_category: string;
  storage_condition: string;
  prepared_at: string;
  storage_temperature?: number;
  packaging_expiry?: string;
}

export interface CalculateExpiryResponse {
  food_category: string;
  storage_condition: string;
  max_holding_hours: number | null;
  approved_maximum_expiry: string | null;
  rule_applied: string | null;
  rule_source: string | null;
  rule_clause: string | null;
  requires_manual_verification: boolean;
  verification_reason?: string | null;
}
