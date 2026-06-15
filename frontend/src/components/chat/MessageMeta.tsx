"use client";

import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { CATEGORY_COLORS, type FaqCategory } from "@/lib/constants";

interface MessageMetaProps {
  category: string | null;
  confidence: number;
  fallback: boolean;
  matchedQuestion: string | null;
  timestamp: Date;
}

function formatTime(date: Date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function MessageMeta({
  category,
  confidence,
  fallback,
  matchedQuestion,
  timestamp,
}: MessageMetaProps) {
  const categoryColor =
    category && category in CATEGORY_COLORS
      ? CATEGORY_COLORS[category as FaqCategory]
      : "bg-gray-100 text-gray-800";

  const confidencePct = Math.round(confidence * 100);

  return (
    <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
      {category && (
        <Badge className={`text-xs ${categoryColor} border-0`}>
          {category}
        </Badge>
      )}

      {fallback ? (
        <Badge variant="outline" className="text-xs border-amber-400 text-amber-600">
          Low confidence
        </Badge>
      ) : (
        <Tooltip>
          <TooltipTrigger render={<div className="flex items-center gap-1.5 cursor-default" />}>
            <Progress value={confidencePct} className="w-16 h-1.5" />
            <span className="tabular-nums">{confidencePct}%</span>
          </TooltipTrigger>
          <TooltipContent>
            {matchedQuestion
              ? `Matched: "${matchedQuestion}"`
              : `Confidence: ${confidencePct}%`}
          </TooltipContent>
        </Tooltip>
      )}

      <span className="ml-auto">{formatTime(timestamp)}</span>
    </div>
  );
}
