export const FAQ_CATEGORIES = [
  "hours",
  "location",
  "booking",
  "policy",
  "services",
  "payment",
] as const;

export type FaqCategory = (typeof FAQ_CATEGORIES)[number];

export const CATEGORY_COLORS: Record<FaqCategory, string> = {
  hours: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  location: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  booking: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  policy: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  services: "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200",
  payment: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
};

export const CONFIDENCE_THRESHOLD = 0.4;

export const APPOINTMENT_STATUSES = ["scheduled", "completed", "cancelled"] as const;

export const STATUS_STYLES: Record<
  (typeof APPOINTMENT_STATUSES)[number],
  { badge: string; dot: string; label: string }
> = {
  scheduled: {
    badge: "bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-200",
    dot: "bg-sky-500",
    label: "Scheduled",
  },
  completed: {
    badge: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200",
    dot: "bg-emerald-500",
    label: "Completed",
  },
  cancelled: {
    badge: "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-200",
    dot: "bg-rose-500",
    label: "Cancelled",
  },
};

export const RISK_STYLES = {
  low: "text-emerald-600 dark:text-emerald-400",
  medium: "text-amber-600 dark:text-amber-400",
  high: "text-rose-600 dark:text-rose-400",
} as const;
