"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { MessageMeta } from "@/components/chat/MessageMeta";
import type { ChatMessage } from "@/lib/types";
import { BotIcon, UserIcon } from "lucide-react";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      <Avatar size="sm" className="mt-1 shrink-0">
        <AvatarFallback className="bg-muted">
          {isUser ? (
            <UserIcon className="size-3.5 text-muted-foreground" />
          ) : (
            <BotIcon className="size-3.5 text-primary" />
          )}
        </AvatarFallback>
      </Avatar>

      <div className={`max-w-[75%] ${isUser ? "items-end" : "items-start"} flex flex-col`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-sm"
              : "bg-muted text-foreground rounded-tl-sm"
          }`}
        >
          {message.content}
        </div>

        {!isUser && message.meta && (
          <MessageMeta
            category={message.meta.category}
            confidence={message.meta.confidence}
            fallback={message.meta.fallback}
            matchedQuestion={message.meta.matched_question}
            timestamp={message.timestamp}
          />
        )}

        {isUser && (
          <span className="mt-1 text-xs text-muted-foreground">
            {message.timestamp.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        )}
      </div>
    </div>
  );
}
