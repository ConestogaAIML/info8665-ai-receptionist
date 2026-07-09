import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { AppointmentStatus } from "@/lib/types";

interface AppointmentFiltersProps {
  statusFilter: AppointmentStatus | "all";
  onStatusChange: (status: AppointmentStatus | "all") => void;
  dateFilter: string;
  onDateChange: (date: string) => void;
}

export function AppointmentFilters({
  statusFilter,
  onStatusChange,
  dateFilter,
  onDateChange,
}: AppointmentFiltersProps) {
  return (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <Tabs
        value={statusFilter}
        onValueChange={(value) => onStatusChange(value as AppointmentStatus | "all")}
      >
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="scheduled">Scheduled</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
          <TabsTrigger value="cancelled">Cancelled</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="flex items-center gap-2">
        <Input
          type="date"
          value={dateFilter}
          onChange={(event) => onDateChange(event.target.value)}
          className="w-auto min-w-[180px]"
        />
        {dateFilter ? (
          <button
            type="button"
            onClick={() => onDateChange("")}
            className="text-sm text-muted-foreground underline-offset-4 hover:underline"
          >
            Clear
          </button>
        ) : null}
      </div>
    </div>
  );
}
