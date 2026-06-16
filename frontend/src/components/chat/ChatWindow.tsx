"use client";

import { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { TypingIndicator } from "@/components/chat/TypingIndicator";
import type { ChatMessage } from "@/lib/types";
import { MessageSquareIcon } from "lucide-react";

interface ChatWindowProps {
  messages: ChatMessage[];
  isTyping: boolean;
  hasSelectedBusiness: boolean;
}

export function ChatWindow({ messages, isTyping, hasSelectedBusiness }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  if (!hasSelectedBusiness) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 text-muted-foreground">
        <MessageSquareIcon className="size-10 opacity-30" />
        <p className="text-sm">Select a business above to start chatting</p>
      </div>
    );
  }

  if (messages.length === 0 && !isTyping) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 text-muted-foreground">
        <MessageSquareIcon className="size-10 opacity-30" />
        <p className="text-sm">Ask a question to get started</p>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1 px-4">
      <div className="flex flex-col gap-4 py-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isTyping && (
          <div className="flex gap-3">
            <TypingIndicator />
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
