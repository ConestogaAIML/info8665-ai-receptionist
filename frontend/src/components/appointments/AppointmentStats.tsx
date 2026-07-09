import {
  CalendarCheckIcon,
  CalendarClockIcon,
  CalendarXIcon,
  SparklesIcon,
} from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import type { Appointment } from "@/lib/types";
import { cn } from "@/lib/utils";

interface AppointmentStatsProps {
  appointments: Appointment[];
  atRiskCount: number;
}

const STAT_ITEMS = [
  {
    key: "total",
    label: "Total",
    icon: CalendarClockIcon,
    accent: "from-violet-500/15 to-violet-500/5 text-violet-700 dark:text-violet-300",
    iconBg: "bg-violet-500/15 text-violet-600",
  },
  {
    key: "scheduled",
    label: "Scheduled",
    icon: CalendarCheckIcon,
    accent: "from-sky-500/15 to-sky-500/5 text-sky-700 dark:text-sky-300",
    iconBg: "bg-sky-500/15 text-sky-600",
  },
  {
    key: "completed",
    label: "Completed",
    icon: SparklesIcon,
    accent: "from-emerald-500/15 to-emerald-500/5 text-emerald-700 dark:text-emerald-300",
    iconBg: "bg-emerald-500/15 text-emerald-600",
  },
  {
    key: "at-risk",
    label: "At Risk",
    icon: CalendarXIcon,
    accent: "from-rose-500/15 to-rose-500/5 text-rose-700 dark:text-rose-300",
    iconBg: "bg-rose-500/15 text-rose-600",
  },
] as const;

export function AppointmentStats({ appointments, atRiskCount }: AppointmentStatsProps) {
  const counts = {
    total: appointments.length,
    scheduled: appointments.filter((a) => a.status === "scheduled").length,
    completed: appointments.filter((a) => a.status === "completed").length,
    "at-risk": atRiskCount,
  };

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {STAT_ITEMS.map((item) => {
        const Icon = item.icon;
        return (
          <Card
            key={item.key}
            className={cn(
              "overflow-hidden border-0 bg-gradient-to-br shadow-sm ring-1 ring-foreground/5",
              item.accent
            )}
          >
            <CardContent className="flex items-center justify-between pt-4">
              <div>
                <p className="text-sm font-medium opacity-80">{item.label}</p>
                <p className="mt-1 text-3xl font-semibold tracking-tight">
                  {counts[item.key]}
                </p>
              </div>
              <div className={cn("flex size-11 items-center justify-center rounded-2xl", item.iconBg)}>
                <Icon className="size-5" />
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
