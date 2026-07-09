"use client";

import { useState } from "react";
import {
  BrainCircuitIcon,
  CalendarDaysIcon,
  ClockIcon,
  LoaderCircleIcon,
  SparklesIcon,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { predictAppointment } from "@/lib/api/appointmentPrediction";
import { RISK_STYLES } from "@/lib/constants";
import type { PredictionResponse } from "@/lib/types";
import { cn } from "@/lib/utils";

function riskLevel(risk: number) {
  if (risk < 0.3) return "low";
  if (risk <= 0.6) return "medium";
  return "high";
}

export function PredictionPanel() {
  const [age, setAge] = useState("35");
  const [waitingDays, setWaitingDays] = useState("3");
  const [smsReceived, setSmsReceived] = useState("1");
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handlePredict() {
    setIsLoading(true);
    setError(null);
    try {
      const response = await predictAppointment({
        age: Number(age),
        waiting_days: Number(waitingDays),
        sms_received: Number(smsReceived),
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setIsLoading(false);
    }
  }

  const risk = result ? riskLevel(result.no_show_risk) : null;

  return (
    <Card className="border-violet-200/60 bg-gradient-to-b from-violet-50/80 to-card shadow-sm dark:border-violet-900/40 dark:from-violet-950/20">
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="flex size-9 items-center justify-center rounded-xl bg-violet-500/15 text-violet-600">
            <BrainCircuitIcon className="size-4" />
          </div>
          <div>
            <CardTitle>AI Slot Advisor</CardTitle>
            <CardDescription>Predict no-show risk and best booking time</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3">
          <div className="space-y-2">
            <Label htmlFor="age">Client age</Label>
            <Input
              id="age"
              type="number"
              min={0}
              value={age}
              onChange={(event) => setAge(event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="waiting-days">Waiting days</Label>
            <Input
              id="waiting-days"
              type="number"
              min={0}
              value={waitingDays}
              onChange={(event) => setWaitingDays(event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="sms">SMS reminder sent</Label>
            <select
              id="sms"
              value={smsReceived}
              onChange={(event) => setSmsReceived(event.target.value)}
              className="flex h-9 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              <option value="1">Yes</option>
              <option value="0">No</option>
            </select>
          </div>
        </div>

        <Button onClick={handlePredict} disabled={isLoading} className="w-full gap-2">
          {isLoading ? (
            <LoaderCircleIcon className="size-4 animate-spin" />
          ) : (
            <SparklesIcon className="size-4" />
          )}
          Run Prediction
        </Button>

        {error ? <p className="text-sm text-destructive">{error}</p> : null}

        {result ? (
          <div className="space-y-4 rounded-xl border bg-background/80 p-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">No-show risk</span>
                <span className={cn("font-semibold", risk ? RISK_STYLES[risk] : "")}>
                  {Math.round(result.no_show_risk * 100)}%
                </span>
              </div>
              <Progress value={result.no_show_risk * 100} className="h-2" />
              <p className="text-sm font-medium">{result.recommendation}</p>
            </div>

            <div className="grid gap-2 text-sm">
              <div className="flex items-center gap-2 rounded-lg bg-muted/60 px-3 py-2">
                <CalendarDaysIcon className="size-4 text-violet-600" />
                <span>Best day: {result.preferred_weekday}</span>
              </div>
              <div className="flex items-center gap-2 rounded-lg bg-muted/60 px-3 py-2">
                <ClockIcon className="size-4 text-violet-600" />
                <span>Best time: {result.preferred_hour}</span>
              </div>
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
