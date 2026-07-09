import {
  ClockIcon,
  MoreHorizontalIcon,
  PencilIcon,
  ScissorsIcon,
  Trash2Icon,
  UserIcon,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { STATUS_STYLES } from "@/lib/constants";
import type { Appointment } from "@/lib/types";
import { cn } from "@/lib/utils";

interface AppointmentCardProps {
  appointment: Appointment;
  onEdit: (appointment: Appointment) => void;
  onDelete: (appointment: Appointment) => void;
}

function formatDate(date: string) {
  return new Date(`${date}T00:00:00`).toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

function formatTime(time: string) {
  const [hours, minutes] = time.split(":").map(Number);
  const date = new Date();
  date.setHours(hours, minutes, 0, 0);
  return date.toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });
}

export function AppointmentCard({
  appointment,
  onEdit,
  onDelete,
}: AppointmentCardProps) {
  const statusStyle = STATUS_STYLES[appointment.status];

  return (
    <Card className="group border-border/60 bg-card/80 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md">
      <CardContent className="space-y-4 pt-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 space-y-1">
            <div className="flex items-center gap-2">
              <span
                className={cn("size-2 rounded-full", statusStyle.dot)}
                aria-hidden
              />
              <p className="truncate text-base font-semibold">
                {appointment.client_name}
              </p>
            </div>
            <p className="truncate text-sm text-muted-foreground">
              {appointment.service_name}
            </p>
          </div>
          <Badge className={cn("shrink-0 border-0", statusStyle.badge)}>
            {statusStyle.label}
          </Badge>
        </div>

        <div className="grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
          <div className="flex items-center gap-2 rounded-lg bg-muted/50 px-3 py-2">
            <ClockIcon className="size-4 shrink-0" />
            <span>
              {formatDate(appointment.appointment_date)} ·{" "}
              {formatTime(appointment.appointment_time)}
            </span>
          </div>
          <div className="flex items-center gap-2 rounded-lg bg-muted/50 px-3 py-2">
            <ScissorsIcon className="size-4 shrink-0" />
            <span className="truncate">{appointment.service_name}</span>
          </div>
        </div>

        {appointment.notes ? (
          <p className="rounded-lg border border-dashed px-3 py-2 text-sm text-muted-foreground">
            {appointment.notes}
          </p>
        ) : null}

        <div className="flex items-center justify-between border-t pt-3">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <UserIcon className="size-3.5" />
            Client #{appointment.client_id}
          </div>
          <div className="flex items-center gap-1 opacity-100 transition-opacity sm:opacity-0 sm:group-hover:opacity-100">
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={() => onEdit(appointment)}
              aria-label="Edit appointment"
            >
              <PencilIcon className="size-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={() => onDelete(appointment)}
              aria-label="Delete appointment"
              className="text-destructive hover:text-destructive"
            >
              <Trash2Icon className="size-3.5" />
            </Button>
            <Button variant="ghost" size="icon-sm" className="sm:hidden" aria-label="More actions">
              <MoreHorizontalIcon className="size-3.5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
