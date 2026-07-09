import { apiFetch } from "@/lib/api/client";
import type { BusinessFAQListResponse } from "@/lib/types";

export async function listFaqs(businessId: number): Promise<BusinessFAQListResponse> {
  return apiFetch<BusinessFAQListResponse>(
    `/api/businesses/${businessId}/faqs/?is_active=true`,
    businessId
  );
}
