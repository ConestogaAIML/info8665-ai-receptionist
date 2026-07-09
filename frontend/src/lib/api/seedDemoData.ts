import { apiFetch } from "@/lib/api/client";

const BUSINESS_ID = 1;

export interface SeedDemoResponse {
  message: string;
  clients_added: number;
  services_added: number;
  appointments_added: number;
  clients_total: number;
  services_total: number;
}

export async function seedDemoData(): Promise<SeedDemoResponse> {
  return apiFetch<SeedDemoResponse>("/api/dev/seed-appointments/", BUSINESS_ID, {
    method: "POST",
  });
}
