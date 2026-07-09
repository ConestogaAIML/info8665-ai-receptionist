import { apiFetch } from "@/lib/api/client";
import type { ClientListResponse } from "@/lib/types";

const BUSINESS_ID = 1;

export async function listClients(search?: string): Promise<ClientListResponse> {
  const query = search ? `?search=${encodeURIComponent(search)}` : "";
  return apiFetch<ClientListResponse>(`/api/clients/${query}`, BUSINESS_ID);
}
