import { apiFetch } from "@/lib/api/client";
import type { ChatResponse } from "@/lib/types";

export async function sendChatMessage(
  businessId: number,
  message: string
): Promise<ChatResponse> {
  return apiFetch<ChatResponse>(
    `/api/businesses/${businessId}/chat/`,
    businessId,
    {
      method: "POST",
      body: JSON.stringify({ message }),
    }
  );
}
