import { describe, it, expect } from 'vitest';
import { corsHeaders, handlePreflight } from '../src/cors';

describe('cors', () => {
  it('returns allow-origin for matching origin', () => {
    const h = corsHeaders('https://niv.schendel.me', 'https://niv.schendel.me');
    expect(h['Access-Control-Allow-Origin']).toBe('https://niv.schendel.me');
    expect(h['Access-Control-Allow-Credentials']).toBe('true');
  });

  it('omits allow-origin for mismatching origin', () => {
    const h = corsHeaders('https://evil.example', 'https://niv.schendel.me');
    expect(h['Access-Control-Allow-Origin']).toBeUndefined();
  });

  it('handlePreflight returns 204 with CORS headers', () => {
    const req = new Request('https://chat.niv.schendel.me/', {
      method: 'OPTIONS',
      headers: { Origin: 'https://niv.schendel.me' },
    });
    const res = handlePreflight(req, 'https://niv.schendel.me');
    expect(res.status).toBe(204);
    expect(res.headers.get('Access-Control-Allow-Origin')).toBe('https://niv.schendel.me');
    expect(res.headers.get('Access-Control-Allow-Methods')).toContain('POST');
  });
});
