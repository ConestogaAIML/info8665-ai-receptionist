import { apiFetch } from "@/lib/api/client";
import type {
  AtRiskListResponse,
  PredictionRequest,
  PredictionResponse,
} from "@/lib/types";

const BUSINESS_ID = 1;

export async function predictAppointment(
  payload: PredictionRequest
): Promise<PredictionResponse> {
  return apiFetch<PredictionResponse>("/api/appointments/predict", BUSINESS_ID, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listAtRiskAppointments(): Promise<AtRiskListResponse> {
  return apiFetch<AtRiskListResponse>("/api/appointments/at-risk/", BUSINESS_ID);
}
