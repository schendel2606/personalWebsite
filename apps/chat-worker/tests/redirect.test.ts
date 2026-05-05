import { describe, it, expect } from 'vitest';
import { handleApexRedirect } from '../src/redirect';

describe('handleApexRedirect', () => {
  it('redirects schendel.me apex to niv.schendel.me', () => {
    const req = new Request('https://schendel.me/', { method: 'GET' });
    const res = handleApexRedirect(req)!;
    expect(res.status).toBe(301);
    expect(res.headers.get('Location')).toBe('https://niv.schendel.me/');
  });

  it('redirects www.schendel.me to niv.schendel.me', () => {
    const req = new Request('https://www.schendel.me/', { method: 'GET' });
    const res = handleApexRedirect(req)!;
    expect(res.status).toBe(301);
    expect(res.headers.get('Location')).toBe('https://niv.schendel.me/');
  });

  it('preserves path and query string', () => {
    const req = new Request('https://schendel.me/projects?source=linkedin#bio');
    const res = handleApexRedirect(req)!;
    expect(res.headers.get('Location')).toBe(
      'https://niv.schendel.me/projects?source=linkedin#bio',
    );
  });

  it('upgrades http to https on redirect target', () => {
    const req = new Request('http://schendel.me/x');
    const res = handleApexRedirect(req)!;
    expect(res.headers.get('Location')!.startsWith('https://')).toBe(true);
  });

  it('redirects regardless of HTTP method (POST, PUT, DELETE)', () => {
    for (const method of ['POST', 'PUT', 'DELETE']) {
      const req = new Request('https://www.schendel.me/x', { method });
      const res = handleApexRedirect(req)!;
      expect(res.status).toBe(301);
    }
  });

  it('returns null for chat.niv.schendel.me (chat handler should run)', () => {
    const req = new Request('https://chat.niv.schendel.me/');
    expect(handleApexRedirect(req)).toBeNull();
  });

  it('returns null for niv.schendel.me (already canonical)', () => {
    const req = new Request('https://niv.schendel.me/');
    expect(handleApexRedirect(req)).toBeNull();
  });

  it('returns null for unrelated hostnames', () => {
    const req = new Request('https://example.com/');
    expect(handleApexRedirect(req)).toBeNull();
  });

  it('does NOT redirect subdomains other than www (e.g. agent, fpl, tasks)', () => {
    for (const host of ['agent.schendel.me', 'fpl.schendel.me', 'tasks.schendel.me', 'learn.schendel.me']) {
      const req = new Request(`https://${host}/`);
      expect(handleApexRedirect(req)).toBeNull();
    }
  });
});
