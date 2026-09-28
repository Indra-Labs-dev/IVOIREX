import type { paths } from '../types/api';
type HealthResponse = paths['/health']['get']['responses'][200]['content']['application/json'];
const apiBase = process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:43101/api/v1';
export async function getApiHealth(): Promise<HealthResponse> {
  const healthUrl = new URL('/health', apiBase);
  const response = await fetch(healthUrl, { cache: 'no-store' });
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  return response.json() as Promise<HealthResponse>;
}
