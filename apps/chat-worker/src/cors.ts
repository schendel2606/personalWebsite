export function corsHeaders(
  requestOrigin: string | null,
  allowedOrigin: string,
): Record<string, string> {
  const headers: Record<string, string> = {
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Credentials': 'true',
    'Vary': 'Origin',
  };
  if (requestOrigin === allowedOrigin) {
    headers['Access-Control-Allow-Origin'] = allowedOrigin;
  }
  return headers;
}

export function handlePreflight(request: Request, allowedOrigin: string): Response {
  return new Response(null, {
    status: 204,
    headers: corsHeaders(request.headers.get('Origin'), allowedOrigin),
  });
}
