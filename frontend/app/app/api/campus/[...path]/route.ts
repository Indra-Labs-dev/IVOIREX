import { NextRequest, NextResponse } from 'next/server';

const apiBase = process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:43101/api/v1';
const ACCESS = 'ivoirex_access';
const REFRESH = 'ivoirex_refresh';
const cookieOptions = { httpOnly: true, secure: process.env.COOKIE_SECURE === 'true', sameSite: 'lax' as const, path: '/' };
type TokenPair = { access_token: string; refresh_token: string };

function allowed(method: string, path: string[]) {
  const joined = path.join('/');
  if (joined === 'community/posts' && (method === 'GET' || method === 'POST')) return true;
  if (/^community\/posts\/[0-9a-f-]{36}$/.test(joined) && method === 'GET') return true;
  if (/^community\/posts\/[0-9a-f-]{36}\/comments$/.test(joined) && method === 'POST') return true;
  if (/^community\/posts\/[0-9a-f-]{36}\/reaction$/.test(joined) && (method === 'PUT' || method === 'DELETE')) return true;
  if (method === 'GET') return joined === 'courses' || /^courses\/[a-z0-9-]+$/.test(joined) || joined === 'enrollments/me' || /^lessons\/[0-9a-f-]{36}$/.test(joined);
  if (method === 'POST') return joined === 'enrollments' || joined === 'progress/complete';
  return false;
}

function originError(request: NextRequest) {
  const origin = request.headers.get('origin');
  const host = request.headers.get('x-forwarded-host') ?? request.headers.get('host');
  const protocol = request.headers.get('x-forwarded-proto') ?? request.nextUrl.protocol.replace(':', '');
  return !origin || !host || origin !== `${protocol}://${host}`;
}

function refreshCookies(response: NextResponse, pair: TokenPair) {
  response.cookies.set(ACCESS, pair.access_token, { ...cookieOptions, maxAge: Number(process.env.JWT_ACCESS_MINUTES ?? 15) * 60 });
  response.cookies.set(REFRESH, pair.refresh_token, { ...cookieOptions, maxAge: Number(process.env.JWT_REFRESH_DAYS ?? 14) * 86400 });
}

async function proxy(request: NextRequest, path: string[]) {
  const method = request.method;
  if (!allowed(method, path)) return NextResponse.json({ detail: 'Route inconnue.' }, { status: 404 });
  if (method !== 'GET' && originError(request)) return NextResponse.json({ detail: 'Requête d’origine invalide.' }, { status: 403 });
  const apiPath = `${apiBase.replace(/\/$/, '')}/${path.map(encodeURIComponent).join('/')}${request.nextUrl.search}`;
  const access = request.cookies.get(ACCESS)?.value;
  const refresh = request.cookies.get(REFRESH)?.value;
  const needsAuth = method !== 'GET' || path[0] !== 'courses';
  if (needsAuth && !access && !refresh) return NextResponse.json({ detail: 'Connexion requise.' }, { status: 401 });
  const body = method === 'POST' ? await request.text() : undefined;
  if (body && body.length > 64_000) return NextResponse.json({ detail: 'Requête trop volumineuse.' }, { status: 413 });
  const send = (token?: string) => fetch(apiPath, { method, cache: 'no-store', headers: { ...(body ? { 'Content-Type': 'application/json' } : {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body });
  let result = await send(access);
  let pair: TokenPair | undefined;
  if (result.status === 401 && refresh) {
    const renewed = await fetch(`${apiBase.replace(/\/$/, '')}/auth/refresh`, { method: 'POST', cache: 'no-store', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ refresh_token: refresh }) });
    if (renewed.ok) { pair = await renewed.json() as TokenPair; result = await send(pair.access_token); }
  }
  const payload = await result.arrayBuffer();
  const response = new NextResponse(payload, { status: result.status, headers: { 'Content-Type': result.headers.get('Content-Type') ?? 'application/json', 'Cache-Control': 'no-store' } });
  if (pair) refreshCookies(response, pair);
  if (result.status === 401 && needsAuth) {
    response.cookies.set(ACCESS, '', { ...cookieOptions, maxAge: 0 });
    response.cookies.set(REFRESH, '', { ...cookieOptions, maxAge: 0 });
  }
  return response;
}

type Context = { params: Promise<{ path: string[] }> };
export async function GET(request: NextRequest, context: Context) { return proxy(request, (await context.params).path); }
export async function POST(request: NextRequest, context: Context) { return proxy(request, (await context.params).path); }
export async function PUT(request: NextRequest, context: Context) { return proxy(request, (await context.params).path); }
export async function DELETE(request: NextRequest, context: Context) { return proxy(request, (await context.params).path); }
