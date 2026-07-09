"use client";

import { useState, useRef, type KeyboardEvent } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { SendIcon } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  disabled: boolean;
}

export function ChatInput({ onSend, isLoading, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function handleSend() {
    const msg = value.trim();
    if (!msg || isLoading || disabled) return;
    onSend(msg);
    setValue("");
    textareaRef.current?.focus();
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  const sendButton = (
    <Button
      onClick={handleSend}
      disabled={disabled || isLoading || !value.trim()}
      size="sm"
      className="shrink-0 self-end"
    >
      <SendIcon className="size-4" />
      <span className="sr-only">Send</span>
    </Button>
  );

  return (
    <div className="flex gap-2 border-t px-4 py-3">
      <Textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={
          disabled ? "Select a business to start chatting..." : "Ask a question... (Enter to send)"
        }
        disabled={disabled || isLoading}
        rows={1}
        className="min-h-[40px] max-h-32 resize-none"
      />

      {disabled ? (
        <Tooltip>
          <TooltipTrigger render={<span tabIndex={0} className="shrink-0 self-end" />}>
            {sendButton}
          </TooltipTrigger>
          <TooltipContent>Select a business first</TooltipContent>
        </Tooltip>
      ) : (
        sendButton
      )}
    </div>
  );
}
