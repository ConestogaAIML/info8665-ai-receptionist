"use client";

import { useState, useEffect } from "react";
import { listBusinesses } from "@/lib/api/businesses";
import type { Business } from "@/lib/types";

export function useBusinesses(enabled = true) {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled) return;

    let cancelled = false;
    setIsLoading(true);

    async function load() {
      try {
        const data = await listBusinesses();
        if (!cancelled) {
          setBusinesses(data.results.filter((b) => b.is_active));
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load businesses");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => { cancelled = true; };
  }, [enabled]);

  return { businesses, isLoading, error };
}
