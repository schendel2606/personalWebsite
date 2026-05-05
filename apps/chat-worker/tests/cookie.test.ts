import { describe, it, expect } from 'vitest';
import { signCookie, verifyCookie, parseCookie } from '../src/cookie';

const SECRET = 'a'.repeat(64);

describe('cookie', () => {
  it('signs and verifies a session id', async () => {
    const signed = await signCookie('session-abc-123', SECRET);
    expect(signed).toContain('session-abc-123.');
    const verified = await verifyCookie(signed, SECRET);
    expect(verified).toBe('session-abc-123');
  });

  it('rejects tampered cookie', async () => {
    const signed = await signCookie('id-1', SECRET);
    const tampered = signed.replace('id-1', 'id-2');
    const verified = await verifyCookie(tampered, SECRET);
    expect(verified).toBeNull();
  });

  it('rejects cookie signed with wrong secret', async () => {
    const signed = await signCookie('id-1', SECRET);
    const verified = await verifyCookie(signed, 'b'.repeat(64));
    expect(verified).toBeNull();
  });

  it('parseCookie extracts named cookie from Cookie header', () => {
    const header = 'foo=bar; session=abc.signed; baz=qux';
    expect(parseCookie(header, 'session')).toBe('abc.signed');
    expect(parseCookie(header, 'missing')).toBeNull();
    expect(parseCookie(null, 'session')).toBeNull();
  });
});
