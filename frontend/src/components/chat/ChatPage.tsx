"use client";

import { useState } from "react";
import { BusinessSelector } from "@/components/chat/BusinessSelector";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { ChatInput } from "@/components/chat/ChatInput";
import { AppNav } from "@/components/layout/AppNav";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { useBusinesses } from "@/hooks/useBusinesses";
import { useChat } from "@/hooks/useChat";
import { getToken } from "@/lib/api/auth";
import type { Business, ChatMessage } from "@/lib/types";
import { BotIcon, PlugIcon, LoaderCircleIcon } from "lucide-react";

type AuthState = "idle" | "loading" | "connected" | "error";

export function ChatPage() {
  const [authState, setAuthState] = useState<AuthState>("idle");
  const [authError, setAuthError] = useState<string | null>(null);

  const { businesses, isLoading: isLoadingBiz, error: bizError } = useBusinesses(
    authState === "connected"
  );
  const { sendMessage, isLoading } = useChat();

  const [selectedBusiness, setSelectedBusiness] = useState<Business | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatError, setChatError] = useState<string | null>(null);

  async function handleConnect() {
    setAuthState("loading");
    setAuthError(null);
    try {
      await getToken(1);
      setAuthState("connected");
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : "Failed to connect");
      setAuthState("error");
    }
  }

  function handleSelectBusiness(id: number) {
    const biz = businesses.find((b) => b.id === id) ?? null;
    setSelectedBusiness(biz);
    setMessages([]);
    setChatError(null);
  }

  async function handleSend(text: string) {
    if (!selectedBusiness) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setChatError(null);

    try {
      const response = await sendMessage(selectedBusiness.id, text);
      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        timestamp: new Date(),
        meta: {
          matched_question: response.matched_question,
          category: response.category,
          confidence: response.confidence,
          fallback: response.fallback,
        },
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "Failed to send message");
    }
  }

  if (authState !== "connected") {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-6 bg-muted/30">
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="flex size-14 items-center justify-center rounded-2xl bg-primary/10">
            <BotIcon className="size-7 text-primary" />
          </div>
          <h1 className="text-xl font-semibold">AI Receptionist</h1>
          <p className="max-w-xs text-sm text-muted-foreground">
            Connect to the backend to start chatting with the FAQ assistant.
          </p>
        </div>

        {authError && (
          <Alert variant="destructive" className="max-w-xs">
            <AlertDescription className="text-xs">{authError}</AlertDescription>
          </Alert>
        )}

        <Button
          onClick={handleConnect}
          disabled={authState === "loading"}
          className="gap-2"
        >
          {authState === "loading" ? (
            <LoaderCircleIcon className="size-4 animate-spin" />
          ) : (
            <PlugIcon className="size-4" />
          )}
          {authState === "loading" ? "Connecting…" : authState === "error" ? "Retry" : "Connect"}
        </Button>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      <header className="flex items-center gap-3 border-b px-4 py-3 shrink-0">
        <BotIcon className="size-5 text-primary" />
        <h1 className="text-base font-semibold">AI Receptionist</h1>
        <div className="ml-auto flex items-center gap-3">
          <AppNav />
          <BusinessSelector
            businesses={businesses}
            selectedId={selectedBusiness?.id ?? null}
            onSelect={handleSelectBusiness}
            isLoading={isLoadingBiz}
          />
        </div>
      </header>

      {(bizError || chatError) && (
        <Alert variant="destructive" className="mx-4 mt-3 shrink-0">
          <AlertDescription>{bizError ?? chatError}</AlertDescription>
        </Alert>
      )}

      <ChatWindow
        messages={messages}
        isTyping={isLoading}
        hasSelectedBusiness={selectedBusiness !== null}
      />

      <ChatInput
        onSend={handleSend}
        isLoading={isLoading}
        disabled={selectedBusiness === null}
      />
    </div>
  );
}
