import { apiFetch, apiFetchVoid } from "@/lib/api/client";
import type {
  Appointment,
  AppointmentInput,
  AppointmentListResponse,
  AppointmentStatus,
} from "@/lib/types";

const BUSINESS_ID = 1;

function buildQuery(params: Record<string, string | undefined>) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value) search.set(key, value);
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

export async function listAppointments(filters?: {
  appointment_date?: string;
  status?: AppointmentStatus;
  client_id?: number;
}): Promise<AppointmentListResponse> {
  return apiFetch<AppointmentListResponse>(
    `/api/appointments/${buildQuery({
      appointment_date: filters?.appointment_date,
      status: filters?.status,
      client_id: filters?.client_id?.toString(),
    })}`,
    BUSINESS_ID
  );
}

export async function createAppointment(
  payload: AppointmentInput
): Promise<Appointment> {
  return apiFetch<Appointment>("/api/appointments/", BUSINESS_ID, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateAppointment(
  id: number,
  payload: AppointmentInput
): Promise<Appointment> {
  return apiFetch<Appointment>(`/api/appointments/${id}/`, BUSINESS_ID, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteAppointment(id: number): Promise<void> {
  return apiFetchVoid(`/api/appointments/${id}/`, BUSINESS_ID, {
    method: "DELETE",
  });
}
