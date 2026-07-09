import { apiFetch } from "@/lib/api/client";
import type { ServiceListResponse } from "@/lib/types";

const BUSINESS_ID = 1;

export async function listServices(): Promise<ServiceListResponse> {
  return apiFetch<ServiceListResponse>("/api/services/?is_active=true", BUSINESS_ID);
}
