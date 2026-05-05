export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  reply: string;
  remainingQuota: number;
  language: 'en' | 'he' | 'mixed';
}

export interface RateLimitResponse {
  error: 'rate_limit';
  retryAfterSeconds: number;
  fallbackContacts: { email: string; linkedin: string };
}

export interface InvalidResponse {
  error: 'input_invalid';
  reason: 'too_long' | 'empty' | 'non_text';
}
