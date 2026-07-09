"use client";

import { useEffect, useState } from "react";
import { DatabaseIcon, LoaderCircleIcon, XIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Appointment, AppointmentInput, AppointmentStatus } from "@/lib/types";
import type { Client } from "@/lib/types";
import type { Service } from "@/lib/types";

interface AppointmentFormDialogProps {
  open: boolean;
  onClose: () => void;
  clients: Client[];
  services: Service[];
  appointment?: Appointment | null;
  onLoadSamples?: () => Promise<void>;
  isLoadingSamples?: boolean;
  onSubmit: (payload: AppointmentInput) => Promise<void>;
}

const EMPTY_FORM: AppointmentInput = {
  client_id: 0,
  service_id: 0,
  appointment_date: "",
  appointment_time: "10:00",
  status: "scheduled",
  notes: "",
};

export function AppointmentFormDialog({
  open,
  onClose,
  clients,
  services,
  appointment,
  onLoadSamples,
  isLoadingSamples = false,
  onSubmit,
}: AppointmentFormDialogProps) {
  const [form, setForm] = useState<AppointmentInput>(EMPTY_FORM);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;

    if (appointment) {
      setForm({
        client_id: appointment.client_id,
        service_id: appointment.service_id,
        appointment_date: appointment.appointment_date,
        appointment_time: appointment.appointment_time,
        status: appointment.status,
        notes: appointment.notes,
      });
    } else {
      const today = new Date().toISOString().slice(0, 10);
      setForm({
        ...EMPTY_FORM,
        appointment_date: today,
        client_id: clients[0]?.id ?? 0,
        service_id: services[0]?.id ?? 0,
      });
    }
    setError(null);
  }, [open, appointment, clients, services]);

  if (!open) return null;

  const missingOptions = clients.length === 0 || services.length === 0;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!form.client_id || !form.service_id) {
      setError("Please select a client and service.");
      return;
    }

    setIsSaving(true);
    setError(null);
    try {
      await onSubmit(form);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save appointment");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button
        type="button"
        className="absolute inset-0 bg-background/70 backdrop-blur-sm"
        onClick={onClose}
        aria-label="Close dialog"
      />
      <div className="relative z-10 w-full max-w-lg rounded-2xl border bg-card p-6 shadow-2xl">
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold">
              {appointment ? "Edit Appointment" : "Book Appointment"}
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Schedule a client visit with service details and notes.
            </p>
          </div>
          <Button variant="ghost" size="icon-sm" onClick={onClose}>
            <XIcon className="size-4" />
          </Button>
        </div>

        {missingOptions && !appointment ? (
          <div className="mb-4 rounded-xl border border-dashed px-4 py-4 text-center text-sm">
            <p className="font-medium">Client and service lists are empty</p>
            <p className="mt-1 text-muted-foreground">
              Load sample data to populate the dropdowns instantly.
            </p>
            {onLoadSamples ? (
              <Button
                type="button"
                onClick={() => onLoadSamples()}
                disabled={isLoadingSamples}
                className="mt-3 gap-2"
                size="sm"
              >
                {isLoadingSamples ? (
                  <LoaderCircleIcon className="size-4 animate-spin" />
                ) : (
                  <DatabaseIcon className="size-4" />
                )}
                Load Sample Data
              </Button>
            ) : null}
          </div>
        ) : null}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="client">Client</Label>
              <Select
                value={form.client_id ? String(form.client_id) : ""}
                onValueChange={(value) =>
                  setForm((prev) => ({ ...prev, client_id: Number(value) }))
                }
              >
                <SelectTrigger id="client" className="w-full">
                  <SelectValue placeholder="Select client" />
                </SelectTrigger>
                <SelectContent>
                  {clients.map((client) => (
                    <SelectItem key={client.id} value={String(client.id)}>
                      {client.first_name} {client.last_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="service">Service</Label>
              <Select
                value={form.service_id ? String(form.service_id) : ""}
                onValueChange={(value) =>
                  setForm((prev) => ({ ...prev, service_id: Number(value) }))
                }
              >
                <SelectTrigger id="service" className="w-full">
                  <SelectValue placeholder="Select service" />
                </SelectTrigger>
                <SelectContent>
                  {services.map((service) => (
                    <SelectItem key={service.id} value={String(service.id)}>
                      {service.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="date">Date</Label>
              <Input
                id="date"
                type="date"
                value={form.appointment_date}
                onChange={(event) =>
                  setForm((prev) => ({
                    ...prev,
                    appointment_date: event.target.value,
                  }))
                }
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="time">Time</Label>
              <Input
                id="time"
                type="time"
                value={form.appointment_time}
                onChange={(event) =>
                  setForm((prev) => ({
                    ...prev,
                    appointment_time: event.target.value,
                  }))
                }
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="status">Status</Label>
            <Select
              value={form.status}
              onValueChange={(value) =>
                setForm((prev) => ({
                  ...prev,
                  status: value as AppointmentStatus,
                }))
              }
            >
              <SelectTrigger id="status" className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="scheduled">Scheduled</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <textarea
              id="notes"
              value={form.notes}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, notes: event.target.value }))
              }
              rows={3}
              className="flex min-h-20 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              placeholder="Special requests, allergies, preferred stylist..."
            />
          </div>

          {error ? <p className="text-sm text-destructive">{error}</p> : null}

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSaving || missingOptions} className="gap-2">
              {isSaving ? <LoaderCircleIcon className="size-4 animate-spin" /> : null}
              {appointment ? "Save Changes" : "Book Appointment"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
