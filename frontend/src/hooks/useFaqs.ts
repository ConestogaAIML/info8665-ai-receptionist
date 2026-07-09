"use client";

import { useState, useEffect } from "react";
import { listFaqs } from "@/lib/api/faqs";
import type { BusinessFAQ } from "@/lib/types";

export function useFaqs(businessId: number | null) {
  const [faqs, setFaqs] = useState<BusinessFAQ[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (businessId === null) {
      setFaqs([]);
      setError(null);
      return;
    }

    const id = businessId;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    async function load() {
      try {
        const data = await listFaqs(id);
        if (!cancelled) {
          setFaqs(data.results);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load FAQs");
          setFaqs([]);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [businessId]);

  return { faqs, isLoading, error };
}
