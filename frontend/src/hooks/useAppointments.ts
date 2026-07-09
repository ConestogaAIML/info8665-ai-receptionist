"use client";

import { useCallback, useEffect, useState } from "react";
import {
  createAppointment,
  deleteAppointment,
  listAppointments,
  updateAppointment,
} from "@/lib/api/appointments";
import type { Appointment, AppointmentInput, AppointmentStatus } from "@/lib/types";

export function useAppointments(enabled = true) {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<{
    appointment_date?: string;
    status?: AppointmentStatus;
  }>({});

  const load = useCallback(async () => {
    if (!enabled) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await listAppointments(filters);
      setAppointments(data.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load appointments");
    } finally {
      setIsLoading(false);
    }
  }, [enabled, filters]);

  useEffect(() => {
    load();
  }, [load]);

  async function addAppointment(payload: AppointmentInput) {
    const created = await createAppointment(payload);
    setAppointments((prev) => [created, ...prev]);
    return created;
  }

  async function editAppointment(id: number, payload: AppointmentInput) {
    const updated = await updateAppointment(id, payload);
    setAppointments((prev) => prev.map((a) => (a.id === id ? updated : a)));
    return updated;
  }

  async function removeAppointment(id: number) {
    await deleteAppointment(id);
    setAppointments((prev) => prev.filter((a) => a.id !== id));
  }

  return {
    appointments,
    isLoading,
    error,
    filters,
    setFilters,
    reload: load,
    addAppointment,
    editAppointment,
    removeAppointment,
  };
}
