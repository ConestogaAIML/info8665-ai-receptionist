"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertTriangleIcon, LoaderCircleIcon, RefreshCwIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { listAtRiskAppointments } from "@/lib/api/appointmentPrediction";
import type { AtRiskAppointment } from "@/lib/types";

type AtRiskPanelProps = {
  onCountChange?: (count: number) => void;
  refreshKey?: number;
};

export function AtRiskPanel({ onCountChange, refreshKey = 0 }: AtRiskPanelProps) {
  const [items, setItems] = useState<AtRiskAppointment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listAtRiskAppointments();
      setItems(data.results);
      onCountChange?.(data.count);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load at-risk clients");
      onCountChange?.(0);
    } finally {
      setIsLoading(false);
    }
  }, [onCountChange]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className="flex size-9 items-center justify-center rounded-xl bg-rose-500/15 text-rose-600">
              <AlertTriangleIcon className="size-4" />
            </div>
            <div>
              <CardTitle>At-Risk Clients</CardTitle>
              <CardDescription>
                High profile risk from saved assessments (new + returning)
              </CardDescription>
            </div>
          </div>
          <Button
            variant="outline"
            size="icon-sm"
            onClick={() => void load()}
            aria-label="Refresh at-risk list"
          >
            <RefreshCwIcon className="size-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8 text-muted-foreground">
            <LoaderCircleIcon className="size-5 animate-spin" />
          </div>
        ) : error ? (
          <div className="space-y-3">
            <p className="text-sm text-destructive">{error}</p>
            <Button variant="outline" size="sm" onClick={() => void load()}>
              Retry
            </Button>
          </div>
        ) : items.length === 0 ? (
          <p className="rounded-lg bg-muted/50 px-3 py-4 text-sm text-muted-foreground">
            No high-risk clients yet. Run Slot Advisor and save a customer assessment.
          </p>
        ) : (
          <div className="space-y-2">
            {items.slice(0, 8).map((item) => (
              <div
                key={item.assessment_id}
                className="flex items-center justify-between rounded-lg border px-3 py-2.5"
              >
                <div>
                  <p className="text-sm font-medium">{item.client_name}</p>
                  <p className="text-xs text-muted-foreground">
                    {item.reason ??
                      (item.is_new_customer ? "New customer" : "Returning")}
                    {item.customer_id ? ` · #${item.customer_id}` : ""}
                    {" · "}
                    {item.requires_confirmation ? "Confirmation recommended" : "Monitor"}
                  </p>
                </div>
                <Badge variant="destructive">
                  {Math.round(item.profile_risk * 100)}% risk
                </Badge>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
