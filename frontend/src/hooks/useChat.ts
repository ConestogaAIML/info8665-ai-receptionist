"use client";

import { useState } from "react";
import { sendChatMessage } from "@/lib/api/chat";
import type { ChatResponse } from "@/lib/types";

export function useChat() {
  const [isLoading, setIsLoading] = useState(false);

  async function sendMessage(
    businessId: number,
    message: string
  ): Promise<ChatResponse> {
    setIsLoading(true);
    try {
      return await sendChatMessage(businessId, message);
    } finally {
      setIsLoading(false);
    }
  }

  return { sendMessage, isLoading };
}
