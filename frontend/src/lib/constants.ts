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
