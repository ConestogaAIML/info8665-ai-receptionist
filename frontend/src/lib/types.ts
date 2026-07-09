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
