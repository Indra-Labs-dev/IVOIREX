import { NextRequest, NextResponse } from 'next/server';

const apiBase = process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:43101/api/v1';
const accessCookie = 'ivoirex_access';
const refreshCookie = 'ivoirex_refresh';
const cookieOptions = { httpOnly: true, secure: process.env.COOKIE_SECURE === 'true', sameSite: 'lax' as const, path: '/' };

type TokenPair = { access_token: string; refresh_token: string };

function endpoint(path: string): URL {
  return new URL(path, `${apiBase.replace(/\/$/, '')}/`);
}

function setTokens(response: NextResponse, tokens: TokenPair) {
  const accessMinutes = Number(process.env.JWT_ACCESS_MINUTES ?? 15);
  const refreshDays = Number(process.env.JWT_REFRESH_DAYS ?? 14);
  response.cookies.set(accessCookie, tokens.access_token, { ...cookieOptions, maxAge: (Number.isFinite(accessMinutes) ? accessMinutes : 15) * 60 });
  response.cookies.set(refreshCookie, tokens.refresh_token, { ...cookieOptions, maxAge: (Number.isFinite(refreshDays) ? refreshDays : 14) * 24 * 60 * 60 });
}

function clearTokens(response: NextResponse) {
  response.cookies.set(accessCookie, '', { ...cookieOptions, maxAge: 0 });
  response.cookies.set(refreshCookie, '', { ...cookieOptions, maxAge: 0 });
}

function assertSameOrigin(request: NextRequest): NextResponse | null {
  const origin = request.headers.get('origin');
  const host = request.headers.get('x-forwarded-host') ?? request.headers.get('host');
  const protocol = request.headers.get('x-forwarded-proto') ?? request.nextUrl.protocol.replace(':', '');
  if (!origin || !host || origin !== `${protocol}://${host}`) {
    return NextResponse.json({ detail: 'Requête d’origine invalide.' }, { status: 403 });
  }
  return null;
}

async function backend(path: string, init?: RequestInit): Promise<Response> {
  return fetch(endpoint(path), { ...init, cache: 'no-store', headers: { 'Content-Type': 'application/json', ...init?.headers } });
}

function clientAddressHeaders(request: NextRequest): Record<string, string> {
  if (process.env.TRUST_CLIENT_IP_HEADERS !== 'true') return {};
  const forwarded = request.headers.get('x-forwarded-for') ?? request.headers.get('x-real-ip');
  if (!forwarded) return {};
  const address = forwarded.split(',')[0]?.trim();
  return address ? { 'X-Forwarded-For': address } : {};
}

async function currentProfile(request: NextRequest): Promise<{ result: Response; tokens?: TokenPair }> {
  let access = request.cookies.get(accessCookie)?.value;
  const refresh = request.cookies.get(refreshCookie)?.value;
  if (!access && !refresh) return { result: new Response(null, { status: 401 }) };

  let result = access ? await backend('profile/me', { headers: { Authorization: `Bearer ${access}` } }) : new Response(null, { status: 401 });
  if (result.status === 401 && refresh) {
    const renewed = await backend('auth/refresh', { method: 'POST', headers: clientAddressHeaders(request), body: JSON.stringify({ refresh_token: refresh }) });
    if (!renewed.ok) return { result: new Response(null, { status: 401 }) };
    const tokens = (await renewed.json()) as TokenPair;
    access = tokens.access_token;
    result = await backend('profile/me', { headers: { Authorization: `Bearer ${access}` } });
    return { result, tokens };
  }
  return { result };
}

export async function GET(request: NextRequest) {
  const { result, tokens } = await currentProfile(request);
  if (result.status === 401) {
    const response = NextResponse.json({ authenticated: false });
    if (request.cookies.has(accessCookie) || request.cookies.has(refreshCookie)) clearTokens(response);
    return response;
  }
  if (!result.ok) return NextResponse.json({ detail: 'Impossible de charger le profil.' }, { status: 502 });
  const response = NextResponse.json({ authenticated: true, profile: await result.json() });
  if (tokens) setTokens(response, tokens);
  return response;
}

export async function POST(request: NextRequest) {
  const originError = assertSameOrigin(request);
  if (originError) return originError;
  const body = await request.json().catch(() => null) as { action?: string; email?: string; username?: string; password?: string; profile?: Record<string, unknown> } | null;
  if (!body) return NextResponse.json({ detail: 'Corps JSON invalide.' }, { status: 400 });

  if (body.action === 'login' || body.action === 'register') {
    const path = body.action === 'login' ? 'auth/login' : 'auth/register';
    const credentials = { email: body.email, password: body.password, ...(body.action === 'register' ? { username: body.username } : {}) };
    const signedIn = await backend(path, { method: 'POST', headers: clientAddressHeaders(request), body: JSON.stringify(credentials) });
    const signedInBody = await signedIn.json().catch(() => ({})) as TokenPair & { user?: unknown; detail?: string };
    if (!signedIn.ok) return NextResponse.json({ detail: signedInBody.detail ?? 'Connexion impossible.' }, { status: signedIn.status });
    const profile = await backend('profile/me', { headers: { Authorization: `Bearer ${signedInBody.access_token}` } });
    if (!profile.ok) return NextResponse.json({ detail: 'Le profil ne peut pas être chargé.' }, { status: 502 });
    const response = NextResponse.json({ authenticated: true, profile: await profile.json() });
    setTokens(response, signedInBody);
    return response;
  }

  if (body.action === 'save-profile' && body.profile) {
    const { result, tokens } = await currentProfile(request);
    if (result.status === 401) return NextResponse.json({ detail: 'Ta session a expiré. Reconnecte-toi.' }, { status: 401 });
    if (!result.ok) return NextResponse.json({ detail: 'Impossible de valider ta session.' }, { status: 502 });
    const access = tokens?.access_token ?? request.cookies.get(accessCookie)?.value;
    const saved = await backend('profile/me', { method: 'PUT', headers: { Authorization: `Bearer ${access}` }, body: JSON.stringify(body.profile) });
    const savedBody = await saved.json().catch(() => ({}));
    const response = NextResponse.json(savedBody, { status: saved.status });
    if (tokens) setTokens(response, tokens);
    return response;
  }

  return NextResponse.json({ detail: 'Action inconnue.' }, { status: 400 });
}

export async function DELETE(request: NextRequest) {
  const originError = assertSameOrigin(request);
  if (originError) return originError;
  let access = request.cookies.get(accessCookie)?.value;
  const refresh = request.cookies.get(refreshCookie)?.value;
  if (refresh) {
    const renewed = await backend('auth/refresh', { method: 'POST', headers: clientAddressHeaders(request), body: JSON.stringify({ refresh_token: refresh }) });
    if (renewed.ok) access = ((await renewed.json()) as TokenPair).access_token;
  }
  if (access) await backend('auth/logout', { method: 'POST', headers: { Authorization: `Bearer ${access}` } });
  const response = NextResponse.json({ authenticated: false });
  clearTokens(response);
  return response;
}
