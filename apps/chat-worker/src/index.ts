export interface Env {
  ANTHROPIC_API_KEY: string;
  SESSION_COOKIE_SECRET: string;
  ALLOWED_ORIGIN: string;
  RATE_LIMIT_PER_HOUR: string;
  MAX_INPUT_CHARS: string;
  MAX_OUTPUT_TOKENS: string;
  RATE_LIMIT_KV: KVNamespace;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    return new Response('chat-worker placeholder', { status: 200 });
  },
} satisfies ExportedHandler<Env>;
