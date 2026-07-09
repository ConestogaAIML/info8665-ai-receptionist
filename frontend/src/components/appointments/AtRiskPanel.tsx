"use client";

import { useEffect, useState } from "react";
import { AlertTriangleIcon, LoaderCircleIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { listAtRiskAppointments } from "@/lib/api/appointmentPrediction";
import type { AtRiskAppointment } from "@/lib/types";

export function AtRiskPanel({ onCountChange }: { onCountChange?: (count: number) => void }) {
  const [items, setItems] = useState<AtRiskAppointment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await listAtRiskAppointments();
        if (!cancelled) {
          setItems(data.results);
          onCountChange?.(data.count);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load at-risk clients");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [onCountChange]);

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="flex size-9 items-center justify-center rounded-xl bg-rose-500/15 text-rose-600">
            <AlertTriangleIcon className="size-4" />
          </div>
          <div>
            <CardTitle>At-Risk Clients</CardTitle>
            <CardDescription>High no-show probability from ML model</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8 text-muted-foreground">
            <LoaderCircleIcon className="size-5 animate-spin" />
          </div>
        ) : error ? (
          <p className="text-sm text-destructive">{error}</p>
        ) : items.length === 0 ? (
          <p className="rounded-lg bg-muted/50 px-3 py-4 text-sm text-muted-foreground">
            No high-risk clients detected right now.
          </p>
        ) : (
          <div className="space-y-2">
            {items.slice(0, 5).map((item) => (
              <div
                key={item.customer_id}
                className="flex items-center justify-between rounded-lg border px-3 py-2.5"
              >
                <div>
                  <p className="text-sm font-medium">Customer #{item.customer_id}</p>
                  <p className="text-xs text-muted-foreground">
                    {item.requires_confirmation ? "Confirmation recommended" : "Monitor closely"}
                  </p>
                </div>
                <Badge variant="destructive">
                  {Math.round(item.no_show_risk * 100)}% risk
                </Badge>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
