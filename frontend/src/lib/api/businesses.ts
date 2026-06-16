import { apiFetch } from "@/lib/api/client";
import type { BusinessListResponse } from "@/lib/types";

export async function listBusinesses(): Promise<BusinessListResponse> {
  return apiFetch<BusinessListResponse>("/api/businesses/", 1);
}
