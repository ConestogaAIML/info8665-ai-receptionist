export interface ChatResponse {
  answer: string;
  matched_question: string | null;
  category: string | null;
  confidence: number;
  fallback: boolean;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  meta?: Pick<ChatResponse, "matched_question" | "category" | "confidence" | "fallback">;
}

export interface Business {
  id: number;
  name: string;
  description: string;
  phone: string;
  email: string;
  address: string;
  business_hours: string;
  website: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BusinessListResponse {
  count: number;
  results: Business[];
}

export interface BusinessFAQ {
  id: number;
  business_id: number;
  question: string;
  answer: string;
  category: string;
  tags: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BusinessFAQListResponse {
  count: number;
  results: BusinessFAQ[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export type AppointmentStatus = "scheduled" | "completed" | "cancelled";

export interface Appointment {
  id: number;
  client_id: number;
  service_id: number;
  client_name: string;
  service_name: string;
  appointment_date: string;
  appointment_time: string;
  status: AppointmentStatus;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface AppointmentListResponse {
  count: number;
  results: Appointment[];
}

export interface AppointmentInput {
  client_id: number;
  service_id: number;
  appointment_date: string;
  appointment_time: string;
  status: AppointmentStatus;
  notes: string;
}

export interface Client {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface ClientListResponse {
  count: number;
  results: Client[];
}

export interface Service {
  id: number;
  name: string;
  description: string;
  duration_minutes: number;
  price: number;
  category: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ServiceListResponse {
  count: number;
  results: Service[];
}

export interface PredictionRequest {
  age: number;
  waiting_days: number;
  sms_received: number;
}

export interface PredictionResponse {
  preferred_hour: string;
  preferred_weekday: string;
  no_show_risk: number;
  recommendation: string;
}

export interface AtRiskAppointment {
  customer_id: number;
  no_show_risk: number;
  requires_confirmation: boolean;
}

export interface AtRiskListResponse {
  count: number;
  results: AtRiskAppointment[];
}
