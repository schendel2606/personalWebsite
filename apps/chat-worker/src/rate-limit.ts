export interface RateLimitStore {
  get(key: string): Promise<number[] | null>;
  put(key: string, value: number[]): Promise<void>;
}

export interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  retryAfterSeconds: number;
}

/**
 * Sliding-window rate limit. Counts the request itself if allowed.
 * Returns the remaining quota for the most-constrained identifier.
 *
 * Stored value: array of millisecond-precision timestamps within window.
 */
export async function checkAndCount(
  store: RateLimitStore,
  ipKey: string,
  cookieKey: string,
  limit: number,
  windowSeconds: number,
): Promise<RateLimitResult> {
  const now = Date.now();
  const cutoff = now - windowSeconds * 1000;

  const ipHits = (await store.get(ipKey)) ?? [];
  const cookieHits = (await store.get(cookieKey)) ?? [];

  const ipFresh = ipHits.filter((t) => t > cutoff);
  const cookieFresh = cookieHits.filter((t) => t > cutoff);

  if (ipFresh.length >= limit || cookieFresh.length >= limit) {
    const oldest = Math.min(
      ipFresh.length >= limit ? ipFresh[0] : Infinity,
      cookieFresh.length >= limit ? cookieFresh[0] : Infinity,
    );
    const retry = Math.ceil((oldest + windowSeconds * 1000 - now) / 1000);
    return { allowed: false, remaining: 0, retryAfterSeconds: Math.max(retry, 1) };
  }

  ipFresh.push(now);
  cookieFresh.push(now);
  await Promise.all([store.put(ipKey, ipFresh), store.put(cookieKey, cookieFresh)]);

  const constrainingCount = Math.max(ipFresh.length, cookieFresh.length);
  return {
    allowed: true,
    remaining: limit - constrainingCount,
    retryAfterSeconds: 0,
  };
}
