/**
 * Canonical-URL redirect for the Worker.
 *
 * The site has one canonical hostname (`niv.schendel.me`). The legacy
 * apex (`schendel.me`) and `www` variant historically served other content;
 * we now permanently redirect them so all three URLs resolve to the same
 * page without serving duplicate content.
 *
 * Returns a 301 Response when the request hostname is one of the redirect
 * sources, or null when the request should fall through to the chat handler
 * (i.e. it's already on `chat.niv.schendel.me`).
 */

const CANONICAL_HOSTNAME = 'niv.schendel.me';
const REDIRECT_FROM = new Set<string>(['schendel.me', 'www.schendel.me']);

export function handleApexRedirect(request: Request): Response | null {
  const url = new URL(request.url);
  if (!REDIRECT_FROM.has(url.hostname)) {
    return null;
  }
  url.hostname = CANONICAL_HOSTNAME;
  url.protocol = 'https:';
  return Response.redirect(url.toString(), 301);
}
