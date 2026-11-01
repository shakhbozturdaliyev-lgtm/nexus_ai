export type Role = 'owner' | 'admin' | 'operator' | 'viewer';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  business_id: number;
}

export interface Customer {
  id: number;
  display_name: string;
  telegram_user_id: number;
  preferred_language: string;
  created_at?: string;
}

export interface Message {
  id: number;
  sender_type: 'customer' | 'ai' | 'operator' | 'system';
  content: string;
  message_type: string;
  is_internal: boolean;
  created_at: string;
}

export interface ConversationSummary {
  id: number;
  status: 'ai_active' | 'awaiting_operator' | 'operator_active' | 'closed';
  created_at: string;
  updated_at: string;
  assigned_operator_id?: number | null;
  customer: Customer;
  last_message?: {
    sender_type: string;
    content: string;
    created_at: string;
  };
}

export interface ProductVariant {
  id: number;
  sku: string;
  storage_capacity?: string;
  color?: string;
  price: number;
  stock_quantity: number;
  availability_status: string;
}

export interface Product {
  id: number;
  name: string;
  brand: string;
  description?: string;
  currency: string;
  active_status: boolean;
  created_at: string;
  variants: ProductVariant[];
}

export interface Order {
  id: number;
  order_number: string;
  status: string;
  total_amount: number;
  currency: string;
  shipping_address?: string;
  created_at: string;
  customer: {
    id: number;
    display_name: string;
    telegram_user_id: number;
  };
}

export interface SupportTicket {
  id: number;
  category: string;
  priority: string;
  status: string;
  conversation_id?: number;
  assigned_operator_id?: number;
  created_at: string;
  resolved_at?: string;
  customer: {
    id: number;
    display_name: string;
    preferred_language: string;
  };
}

export interface KnowledgeArticle {
  id: number;
  category: string;
  title: string;
  content: string;
  language: string;
  version: number;
  is_active: boolean;
  updated_at: string;
}

export interface AISettings {
  business_id: number;
  model_name: string;
  is_enabled: boolean;
  temperature: number;
  max_output_tokens: number;
  context_window_turns: number;
  tool_call_limit: number;
  system_instructions?: string;
  fallback_message?: string;
  updated_at: string;
}

export interface OverviewMetrics {
  total_conversations: number;
  active_conversations: number;
  ai_handled_conversations: number;
  human_handled_conversations: number;
  closed_conversations: number;
  open_support_tickets: number;
  total_customers: number;
  total_orders: number;
  total_revenue_uzs: number;
  resolution_rate_percent: number;
  estimated_ai_tokens_used: number;
  estimated_ai_cost_usd: number;
}
