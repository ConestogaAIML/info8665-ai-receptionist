"use client";

import { useCallback, useEffect, useState } from "react";
import { listServices } from "@/lib/api/services";
import type { Service } from "@/lib/types";

export function useServices(enabled = true) {
  const [services, setServices] = useState<Service[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!enabled) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await listServices();
      setServices(data.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load services");
    } finally {
      setIsLoading(false);
    }
  }, [enabled]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { services, isLoading, error, reload };
}
