"use client";

import { useCallback, useEffect, useState } from "react";
import { listClients } from "@/lib/api/clients";
import type { Client } from "@/lib/types";

export function useClients(enabled = true) {
  const [clients, setClients] = useState<Client[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!enabled) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await listClients();
      setClients(data.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load clients");
    } finally {
      setIsLoading(false);
    }
  }, [enabled]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { clients, isLoading, error, reload };
}
