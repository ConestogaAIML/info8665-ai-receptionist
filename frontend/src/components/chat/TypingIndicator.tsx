"use client";

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-2">
      <div className="flex gap-1">
        <span className="size-2 rounded-full bg-muted-foreground animate-bounce [animation-delay:0ms]" />
        <span className="size-2 rounded-full bg-muted-foreground animate-bounce [animation-delay:150ms]" />
        <span className="size-2 rounded-full bg-muted-foreground animate-bounce [animation-delay:300ms]" />
      </div>
    </div>
  );
}
