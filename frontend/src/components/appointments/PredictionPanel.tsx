"use client";

import { useMemo, useState } from "react";
import {
  BrainCircuitIcon,
  CalendarCheckIcon,
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
import { createAppointment } from "@/lib/api/appointments";
import { predictAppointment } from "@/lib/api/appointmentPrediction";
import { RISK_STYLES } from "@/lib/constants";
import type { Client, PredictionResponse, Service } from "@/lib/types";
import { cn } from "@/lib/utils";

function riskLevel(risk: number) {
  if (risk < 0.3) return "low";
  if (risk <= 0.6) return "medium";
  return "high";
}

const WEEKDAY_TO_JS: Record<string, number> = {
  Sunday: 0,
  Monday: 1,
  Tuesday: 2,
  Wednesday: 3,
  Thursday: 4,
  Friday: 5,
  Saturday: 6,
};

/** Convert "2:00 PM" → "14:00" */
export function parsePreferredHour(label: string): string {
  const match = label.trim().match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
  if (!match) return "09:00";
  let hour = Number(match[1]);
  const minutes = match[2];
  const period = match[3].toUpperCase();
  if (period === "AM" && hour === 12) hour = 0;
  if (period === "PM" && hour !== 12) hour += 12;
  return `${String(hour).padStart(2, "0")}:${minutes}`;
}

/** Next occurrence of weekday at least `minDaysAhead` from today (YYYY-MM-DD). */
export function resolvePreferredDate(weekdayName: string, minDaysAhead: number): string {
  const target = WEEKDAY_TO_JS[weekdayName];
  const base = new Date();
  base.setHours(12, 0, 0, 0);

  const startOffset = Math.max(1, minDaysAhead);
  for (let offset = startOffset; offset < startOffset + 14; offset++) {
    const candidate = new Date(base);
    candidate.setDate(base.getDate() + offset);
    if (target === undefined || candidate.getDay() === target) {
      return candidate.toISOString().slice(0, 10);
    }
  }

  const fallback = new Date(base);
  fallback.setDate(base.getDate() + startOffset);
  return fallback.toISOString().slice(0, 10);
}

type PredictionPanelProps = {
  clients: Client[];
  services: Service[];
  onAssessmentSaved?: () => void;
  onBooked?: () => void;
};

export function PredictionPanel({
  clients,
  services,
  onAssessmentSaved,
  onBooked,
}: PredictionPanelProps) {
  const [mode, setMode] = useState<"existing" | "new">("new");
  const [clientId, setClientId] = useState("");
  const [clientName, setClientName] = useState("");
  const [age, setAge] = useState("35");
  const [waitingDays, setWaitingDays] = useState("3");
  const [smsReceived, setSmsReceived] = useState("1");
  const [serviceId, setServiceId] = useState("");
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isBooking, setIsBooking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bookMessage, setBookMessage] = useState<string | null>(null);

  const activeServices = useMemo(
    () => services.filter((service) => service.is_active),
    [services]
  );

  const selectedServiceId = serviceId || (activeServices[0] ? String(activeServices[0].id) : "");

  const bookingPreview = useMemo(() => {
    if (!result) return null;
    const date = resolvePreferredDate(result.preferred_weekday, Number(waitingDays) || 1);
    const time = parsePreferredHour(result.preferred_hour);
    return { date, time };
  }, [result, waitingDays]);

  async function handlePredict() {
    setIsLoading(true);
    setError(null);
    setBookMessage(null);
    try {
      if (mode === "existing" && !clientId) {
        throw new Error("Select an existing client");
      }
      if (mode === "new" && !clientName.trim()) {
        throw new Error("Enter a name for the new customer");
      }

      const response = await predictAppointment({
        age: Number(age),
        waiting_days: Number(waitingDays),
        sms_received: Number(smsReceived),
        client_id: mode === "existing" ? Number(clientId) : null,
        client_name: mode === "new" ? clientName.trim() : null,
        save: true,
      });
      setResult(response);
      onAssessmentSaved?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleBookRecommended() {
    if (!result || !bookingPreview) return;
    setIsBooking(true);
    setError(null);
    setBookMessage(null);
    try {
      if (!result.client_id) {
        throw new Error("Missing client from prediction — run prediction again");
      }
      if (!selectedServiceId) {
        throw new Error("Select a service before booking");
      }

      const appointment = await createAppointment({
        client_id: result.client_id,
        service_id: Number(selectedServiceId),
        appointment_date: bookingPreview.date,
        appointment_time: bookingPreview.time,
        status: "scheduled",
        notes: `Auto-booked from AI Slot Advisor (${result.preferred_weekday} ${result.preferred_hour}). Risk ${Math.round(result.no_show_risk * 100)}%.`,
      });

      setBookMessage(
        `Booked ${result.client_name} for ${appointment.appointment_date} at ${appointment.appointment_time}.`
      );
      onBooked?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to book appointment");
    } finally {
      setIsBooking(false);
    }
  }

  const bestRisk = result ? riskLevel(result.no_show_risk) : null;
  const profileLevel = result ? riskLevel(result.profile_risk) : null;

  return (
    <Card className="border-violet-200/60 bg-gradient-to-b from-violet-50/80 to-card shadow-sm dark:border-violet-900/40 dark:from-violet-950/20">
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="flex size-9 items-center justify-center rounded-xl bg-violet-500/15 text-violet-600">
            <BrainCircuitIcon className="size-4" />
          </div>
          <div>
            <CardTitle>AI Slot Advisor</CardTitle>
            <CardDescription>
              Predict best day/time, then book that slot for the customer in one click
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3">
          <div className="space-y-2">
            <Label htmlFor="customer-mode">Customer</Label>
            <select
              id="customer-mode"
              value={mode}
              onChange={(event) => setMode(event.target.value as "existing" | "new")}
              className="flex h-9 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              <option value="new">New customer</option>
              <option value="existing">Existing client</option>
            </select>
          </div>

          {mode === "new" ? (
            <div className="space-y-2">
              <Label htmlFor="client-name">Customer name</Label>
              <Input
                id="client-name"
                placeholder="e.g. Alex Rivera"
                value={clientName}
                onChange={(event) => setClientName(event.target.value)}
              />
            </div>
          ) : (
            <div className="space-y-2">
              <Label htmlFor="client-id">Existing client</Label>
              <select
                id="client-id"
                value={clientId}
                onChange={(event) => setClientId(event.target.value)}
                className="flex h-9 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              >
                <option value="">Select client…</option>
                {clients.map((client) => (
                  <option key={client.id} value={client.id}>
                    {client.first_name} {client.last_name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="service-id">Service (for booking)</Label>
            <select
              id="service-id"
              value={selectedServiceId}
              onChange={(event) => setServiceId(event.target.value)}
              className="flex h-9 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              {activeServices.length === 0 ? (
                <option value="">No services — load sample data</option>
              ) : (
                activeServices.map((service) => (
                  <option key={service.id} value={service.id}>
                    {service.name}
                  </option>
                ))
              )}
            </select>
          </div>

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
          Save & Run Prediction
        </Button>

        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        {bookMessage ? <p className="text-sm font-medium text-emerald-700">{bookMessage}</p> : null}

        {result ? (
          <div className="space-y-4 rounded-xl border bg-background/80 p-4">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="rounded-full bg-muted px-2 py-1">
                {result.client_name ?? "Customer"}
              </span>
              <span className="rounded-full bg-muted px-2 py-1">
                {result.is_new_customer ? "New customer" : "Returning"}
              </span>
              {result.is_high_risk ? (
                <span className="rounded-full bg-rose-500/15 px-2 py-1 font-medium text-rose-700">
                  High risk (stored)
                </span>
              ) : (
                <span className="rounded-full bg-emerald-500/15 px-2 py-1 font-medium text-emerald-700">
                  Not high risk
                </span>
              )}
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Best-slot risk</span>
                <span className={cn("font-semibold", bestRisk ? RISK_STYLES[bestRisk] : "")}>
                  {Math.round(result.no_show_risk * 100)}%
                </span>
              </div>
              <Progress value={result.no_show_risk * 100} className="h-2" />
              <p className="text-sm font-medium">{result.recommendation}</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Profile risk (high-risk flag)</span>
                <span className={cn("font-semibold", profileLevel ? RISK_STYLES[profileLevel] : "")}>
                  {Math.round(result.profile_risk * 100)}%
                </span>
              </div>
              <Progress value={result.profile_risk * 100} className="h-2" />
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
              {bookingPreview ? (
                <div className="rounded-lg border border-violet-200/70 bg-violet-50/60 px-3 py-2 text-violet-900 dark:border-violet-900/40 dark:bg-violet-950/30 dark:text-violet-100">
                  Will book: <strong>{result.client_name}</strong> on{" "}
                  <strong>{bookingPreview.date}</strong> at{" "}
                  <strong>{bookingPreview.time}</strong>
                </div>
              ) : null}
            </div>

            <Button
              onClick={handleBookRecommended}
              disabled={isBooking || !selectedServiceId}
              className="w-full gap-2"
            >
              {isBooking ? (
                <LoaderCircleIcon className="size-4 animate-spin" />
              ) : (
                <CalendarCheckIcon className="size-4" />
              )}
              Book recommended appointment
            </Button>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
