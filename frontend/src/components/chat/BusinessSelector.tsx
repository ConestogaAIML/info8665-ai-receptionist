"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import type { Business } from "@/lib/types";

interface BusinessSelectorProps {
  businesses: Business[];
  selectedId: number | null;
  onSelect: (id: number) => void;
  isLoading: boolean;
}

export function BusinessSelector({
  businesses,
  selectedId,
  onSelect,
  isLoading,
}: BusinessSelectorProps) {
  if (isLoading) {
    return <Skeleton className="h-8 w-56" />;
  }

  return (
    <Select
      value={selectedId ?? undefined}
      onValueChange={(val) => {
        if (val != null) onSelect(val as number);
      }}
    >
      <SelectTrigger className="w-56">
        <SelectValue placeholder="Select a business" />
      </SelectTrigger>
      <SelectContent>
        {businesses.map((biz) => (
          <SelectItem key={biz.id} value={biz.id}>
            {biz.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
