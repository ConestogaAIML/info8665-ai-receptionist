import type { TokenResponse } from "@/lib/types";

const TOKEN_CACHE = new Map<number, { token: string; expiresAt: number }>();
const TTL_MS = 55 * 60 * 1000;

export async function getToken(businessId: number): Promise<string> {
  const cached = TOKEN_CACHE.get(businessId);
  if (cached && Date.now() < cached.expiresAt) {
    return cached.token;
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const res = await fetch(`${apiUrl}/auth/token?business_id=${businessId}`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error(`Auth failed: ${res.status} ${res.statusText}`);
  }

  const data: TokenResponse = await res.json();
  TOKEN_CACHE.set(businessId, {
    token: data.access_token,
    expiresAt: Date.now() + TTL_MS,
  });

  return data.access_token;
}
