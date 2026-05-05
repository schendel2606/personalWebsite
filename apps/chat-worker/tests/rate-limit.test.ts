import { describe, it, expect, beforeEach, vi } from 'vitest';
import { checkAndCount, type RateLimitStore } from '../src/rate-limit';

class MemoryStore implements RateLimitStore {
  private data = new Map<string, number[]>();
  async get(key: string): Promise<number[] | null> {
    return this.data.get(key) ?? null;
  }
  async put(key: string, value: number[]): Promise<void> {
    this.data.set(key, value);
  }
}

const NOW = 1_700_000_000_000;

describe('rate limit', () => {
  let store: MemoryStore;

  beforeEach(() => {
    vi.setSystemTime(NOW);
    store = new MemoryStore();
  });

  it('allows first request, returns remaining=9', async () => {
    const r = await checkAndCount(store, 'ip:1.1.1.1', 'cookie:abc', 10, 3600);
    expect(r.allowed).toBe(true);
    expect(r.remaining).toBe(9);
  });

  it('blocks 11th request from same IP within hour', async () => {
    for (let i = 0; i < 10; i++) {
      const r = await checkAndCount(store, 'ip:1.1.1.1', `cookie:${i}`, 10, 3600);
      expect(r.allowed).toBe(true);
    }
    const blocked = await checkAndCount(store, 'ip:1.1.1.1', 'cookie:new', 10, 3600);
    expect(blocked.allowed).toBe(false);
    expect(blocked.remaining).toBe(0);
    expect(blocked.retryAfterSeconds).toBeGreaterThan(0);
    expect(blocked.retryAfterSeconds).toBeLessThanOrEqual(3600);
  });

  it('blocks 11th request from same cookie even on different IPs', async () => {
    for (let i = 0; i < 10; i++) {
      await checkAndCount(store, `ip:2.${i}.0.0`, 'cookie:same', 10, 3600);
    }
    const blocked = await checkAndCount(store, 'ip:99.99.99.99', 'cookie:same', 10, 3600);
    expect(blocked.allowed).toBe(false);
  });

  it('expires entries older than window', async () => {
    await checkAndCount(store, 'ip:3.3.3.3', 'cookie:x', 10, 3600);
    vi.setSystemTime(NOW + 3601 * 1000);  // advance just past window
    const r = await checkAndCount(store, 'ip:3.3.3.3', 'cookie:x', 10, 3600);
    expect(r.allowed).toBe(true);
    expect(r.remaining).toBe(9);  // earlier hit dropped
  });
});
