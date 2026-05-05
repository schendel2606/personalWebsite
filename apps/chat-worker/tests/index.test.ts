import { describe, it, expect, vi } from 'vitest';
import worker from '../src/index';
import * as anthropicModule from '../src/anthropic';

const ENV = {
  ANTHROPIC_API_KEY: 'sk-test',
  SESSION_COOKIE_SECRET: 'a'.repeat(64),
  ALLOWED_ORIGIN: 'https://niv.schendel.me',
  RATE_LIMIT_PER_HOUR: '10',
  MAX_INPUT_CHARS: '500',
  MAX_OUTPUT_TOKENS: '400',
  RATE_LIMIT_KV: makeKv(),
} as any;

function makeKv() {
  const m = new Map<string, string>();
  return {
    get: async (k: string) => m.get(k) ?? null,
    put: async (k: string, v: string) => { m.set(k, v); },
  };
}

function makeRequest(body: unknown, opts: Partial<RequestInit> = {}): Request {
  return new Request('https://chat.niv.schendel.me/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Origin': 'https://niv.schendel.me',
      'CF-Connecting-IP': '1.2.3.4',
      ...(opts.headers ?? {}),
    },
    body: JSON.stringify(body),
  });
}

describe('worker fetch handler', () => {
  it('OPTIONS returns 204 with CORS', async () => {
    const req = new Request('https://chat.niv.schendel.me/', {
      method: 'OPTIONS',
      headers: { Origin: 'https://niv.schendel.me' },
    });
    const res = await worker.fetch(req, ENV, {} as any);
    expect(res.status).toBe(204);
    expect(res.headers.get('Access-Control-Allow-Origin')).toBe('https://niv.schendel.me');
  });

  it('rejects request from disallowed origin', async () => {
    const req = makeRequest({ messages: [{ role: 'user', content: 'hi' }] }, {
      headers: { Origin: 'https://evil.example' },
    });
    const res = await worker.fetch(req, ENV, {} as any);
    expect(res.status).toBe(403);
  });

  it('returns 400 on empty input', async () => {
    vi.spyOn(anthropicModule, 'askClaude').mockResolvedValue('');
    const req = makeRequest({ messages: [{ role: 'user', content: '' }] });
    const res = await worker.fetch(req, ENV, {} as any);
    expect(res.status).toBe(400);
  });

  it('returns 400 when last message exceeds char cap', async () => {
    const req = makeRequest({ messages: [{ role: 'user', content: 'x'.repeat(501) }] });
    const res = await worker.fetch(req, ENV, {} as any);
    expect(res.status).toBe(400);
  });

  it('successful chat returns 200 with reply and remainingQuota', async () => {
    vi.spyOn(anthropicModule, 'askClaude').mockResolvedValue('A polished answer.');
    const req = makeRequest({ messages: [{ role: 'user', content: 'tell me about niv' }] });
    const res = await worker.fetch(req, ENV, {} as any);
    expect(res.status).toBe(200);
    const body = await res.json() as any;
    expect(body.reply).toBe('A polished answer.');
    expect(body.remainingQuota).toBe(9);
    expect(['en', 'he', 'mixed']).toContain(body.language);
  });

  it('sets a session cookie on first request', async () => {
    vi.spyOn(anthropicModule, 'askClaude').mockResolvedValue('answer');
    const req = makeRequest({ messages: [{ role: 'user', content: 'hi' }] });
    const res = await worker.fetch(req, ENV, {} as any);
    const setCookie = res.headers.get('Set-Cookie');
    expect(setCookie).toBeTruthy();
    expect(setCookie).toContain('session=');
    expect(setCookie).toContain('HttpOnly');
    expect(setCookie).toContain('Secure');
  });

  it('returns 429 when rate limit exceeded', async () => {
    vi.spyOn(anthropicModule, 'askClaude').mockResolvedValue('answer');
    const env = { ...ENV, RATE_LIMIT_KV: makeKv() };
    for (let i = 0; i < 10; i++) {
      const req = makeRequest({ messages: [{ role: 'user', content: `q${i}` }] });
      await worker.fetch(req, env, {} as any);
    }
    const blocked = makeRequest({ messages: [{ role: 'user', content: 'one more' }] });
    const res = await worker.fetch(blocked, env, {} as any);
    expect(res.status).toBe(429);
    const body = await res.json() as any;
    expect(body.error).toBe('rate_limit');
    expect(body.retryAfterSeconds).toBeGreaterThan(0);
    expect(body.fallbackContacts.email).toContain('@');
  });
});
