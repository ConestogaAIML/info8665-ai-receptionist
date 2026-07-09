"use client";

import { useMemo, useState } from "react";
import {
  CalendarPlusIcon,
  DatabaseIcon,
  LoaderCircleIcon,
  PlugIcon,
  RefreshCwIcon,
  SparklesIcon,
} from "lucide-react";

import { AppointmentCard } from "@/components/appointments/AppointmentCard";
import { AppointmentFilters } from "@/components/appointments/AppointmentFilters";
import { AppointmentFormDialog } from "@/components/appointments/AppointmentFormDialog";
import { AppointmentStats } from "@/components/appointments/AppointmentStats";
import { AtRiskPanel } from "@/components/appointments/AtRiskPanel";
import { PredictionPanel } from "@/components/appointments/PredictionPanel";
import { AppNav } from "@/components/layout/AppNav";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useAppointments } from "@/hooks/useAppointments";
import { useClients } from "@/hooks/useClients";
import { useServices } from "@/hooks/useServices";
import { getToken } from "@/lib/api/auth";
import { seedDemoData } from "@/lib/api/seedDemoData";
import type { Appointment, AppointmentStatus } from "@/lib/types";

type AuthState = "idle" | "loading" | "connected" | "error";

export function AppointmentsPage() {
  const [authState, setAuthState] = useState<AuthState>("idle");
  const [authError, setAuthError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<AppointmentStatus | "all">("all");
  const [dateFilter, setDateFilter] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAppointment, setEditingAppointment] = useState<Appointment | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [atRiskCount, setAtRiskCount] = useState(0);
  const [isSeeding, setIsSeeding] = useState(false);
  const [seedMessage, setSeedMessage] = useState<string | null>(null);

  const connected = authState === "connected";
  const {
    appointments,
    isLoading,
    error,
    setFilters,
    reload,
    addAppointment,
    editAppointment,
    removeAppointment,
  } = useAppointments(connected);
  const { clients, reload: reloadClients } = useClients(connected);
  const { services, reload: reloadServices } = useServices(connected);

  const needsSampleData = connected && clients.length === 0 && services.length === 0;

  const filteredAppointments = useMemo(() => {
    return appointments
      .filter((appointment) =>
        statusFilter === "all" ? true : appointment.status === statusFilter
      )
      .filter((appointment) =>
        dateFilter ? appointment.appointment_date === dateFilter : true
      )
      .sort((a, b) => {
        const aKey = `${a.appointment_date}T${a.appointment_time}`;
        const bKey = `${b.appointment_date}T${b.appointment_time}`;
        return aKey.localeCompare(bKey);
      });
  }, [appointments, statusFilter, dateFilter]);

  async function handleConnect() {
    setAuthState("loading");
    setAuthError(null);
    try {
      await getToken(1);
      setAuthState("connected");
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : "Failed to connect");
      setAuthState("error");
    }
  }

  function handleStatusChange(status: AppointmentStatus | "all") {
    setStatusFilter(status);
    setFilters({
      appointment_date: dateFilter || undefined,
      status: status === "all" ? undefined : status,
    });
  }

  function handleDateChange(date: string) {
    setDateFilter(date);
    setFilters({
      appointment_date: date || undefined,
      status: statusFilter === "all" ? undefined : statusFilter,
    });
  }

  function openCreateDialog() {
    setEditingAppointment(null);
    setDialogOpen(true);
  }

  function openEditDialog(appointment: Appointment) {
    setEditingAppointment(appointment);
    setDialogOpen(true);
  }

  async function handleLoadSamples() {
    setIsSeeding(true);
    setActionError(null);
    setSeedMessage(null);
    try {
      const result = await seedDemoData();
      await Promise.all([reloadClients(), reloadServices(), reload()]);
      setSeedMessage(result.message);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Failed to load sample data");
    } finally {
      setIsSeeding(false);
    }
  }

  async function handleDelete(appointment: Appointment) {
    if (!confirm(`Delete appointment for ${appointment.client_name}?`)) return;
    setActionError(null);
    try {
      await removeAppointment(appointment.id);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Failed to delete appointment");
    }
  }

  if (!connected) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-[radial-gradient(circle_at_top,_rgba(139,92,246,0.12),_transparent_35%),linear-gradient(to_bottom,_#fafafa,_#ffffff)] px-4 dark:bg-[radial-gradient(circle_at_top,_rgba(139,92,246,0.18),_transparent_35%),linear-gradient(to_bottom,_#111111,_#0a0a0a)]">
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="flex size-16 items-center justify-center rounded-3xl bg-violet-500/15">
            <SparklesIcon className="size-8 text-violet-600" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">Appointment Studio</h1>
          <p className="max-w-md text-sm text-muted-foreground">
            Connect to manage bookings, view schedules, and run AI no-show predictions.
          </p>
        </div>

        {authError ? (
          <Alert variant="destructive" className="max-w-sm">
            <AlertDescription className="text-xs">{authError}</AlertDescription>
          </Alert>
        ) : null}

        <Button onClick={handleConnect} disabled={authState === "loading"} className="gap-2">
          {authState === "loading" ? (
            <LoaderCircleIcon className="size-4 animate-spin" />
          ) : (
            <PlugIcon className="size-4" />
          )}
          {authState === "loading" ? "Connecting…" : authState === "error" ? "Retry" : "Connect"}
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(139,92,246,0.10),_transparent_30%),linear-gradient(to_bottom,_#fafafa,_#ffffff)] dark:bg-[radial-gradient(circle_at_top,_rgba(139,92,246,0.16),_transparent_30%),linear-gradient(to_bottom,_#111111,_#0a0a0a)]">
      <header className="sticky top-0 z-20 border-b bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-4 sm:px-6">
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-[0.2em] text-violet-600">
              AI Receptionist
            </p>
            <h1 className="truncate text-xl font-semibold tracking-tight">Appointments</h1>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <AppNav />
            <Button variant="outline" size="icon-sm" onClick={() => reload()} aria-label="Refresh">
              <RefreshCwIcon className="size-4" />
            </Button>
            {needsSampleData ? (
              <Button
                variant="outline"
                onClick={handleLoadSamples}
                disabled={isSeeding}
                className="gap-2"
              >
                {isSeeding ? (
                  <LoaderCircleIcon className="size-4 animate-spin" />
                ) : (
                  <DatabaseIcon className="size-4" />
                )}
                <span className="hidden sm:inline">Load Sample Data</span>
              </Button>
            ) : null}
            <Button onClick={openCreateDialog} className="gap-2">
              <CalendarPlusIcon className="size-4" />
              <span className="hidden sm:inline">Book Appointment</span>
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_320px] xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-6">
          <AppointmentStats
            appointments={appointments}
            atRiskCount={atRiskCount}
          />

          <section className="space-y-4 rounded-2xl border bg-card/70 p-4 shadow-sm backdrop-blur sm:p-5">
            <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">Schedule</h2>
                <p className="text-sm text-muted-foreground">
                  Manage salon bookings with filters and quick actions.
                </p>
              </div>
              <p className="text-sm text-muted-foreground">
                {filteredAppointments.length} shown
              </p>
            </div>

            <AppointmentFilters
              statusFilter={statusFilter}
              onStatusChange={handleStatusChange}
              dateFilter={dateFilter}
              onDateChange={handleDateChange}
            />

            {(error || actionError) && (
              <Alert variant="destructive">
                <AlertDescription>{error ?? actionError}</AlertDescription>
              </Alert>
            )}

            {seedMessage ? (
              <Alert>
                <AlertDescription>{seedMessage}</AlertDescription>
              </Alert>
            ) : null}

            {needsSampleData ? (
              <div className="rounded-xl border border-dashed border-violet-300/50 bg-violet-500/5 px-4 py-3 text-sm text-muted-foreground">
                <p className="font-medium text-foreground">No clients or services yet</p>
                <p className="mt-1">
                  Load sample salon data to fill the booking form, or add records via the API docs.
                </p>
                <Button
                  onClick={handleLoadSamples}
                  disabled={isSeeding}
                  className="mt-3 gap-2"
                  size="sm"
                >
                  {isSeeding ? (
                    <LoaderCircleIcon className="size-4 animate-spin" />
                  ) : (
                    <DatabaseIcon className="size-4" />
                  )}
                  Load Sample Data
                </Button>
              </div>
            ) : null}

            {isLoading ? (
              <div className="grid gap-4 md:grid-cols-2">
                {Array.from({ length: 4 }).map((_, index) => (
                  <Skeleton key={index} className="h-44 rounded-xl" />
                ))}
              </div>
            ) : filteredAppointments.length === 0 ? (
              <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed bg-muted/20 px-6 py-16 text-center">
                <CalendarPlusIcon className="size-10 text-muted-foreground/70" />
                <h3 className="mt-4 text-lg font-medium">No appointments yet</h3>
                <p className="mt-2 max-w-sm text-sm text-muted-foreground">
                  {needsSampleData
                    ? "Load sample data first, then book your first appointment."
                    : "Create your first booking or adjust filters to see existing appointments."}
                </p>
                {needsSampleData ? (
                  <Button onClick={handleLoadSamples} disabled={isSeeding} className="mt-6 gap-2">
                    {isSeeding ? (
                      <LoaderCircleIcon className="size-4 animate-spin" />
                    ) : (
                      <DatabaseIcon className="size-4" />
                    )}
                    Load Sample Data
                  </Button>
                ) : (
                  <Button onClick={openCreateDialog} className="mt-6 gap-2">
                    <CalendarPlusIcon className="size-4" />
                    Book Appointment
                  </Button>
                )}
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                {filteredAppointments.map((appointment) => (
                  <AppointmentCard
                    key={appointment.id}
                    appointment={appointment}
                    onEdit={openEditDialog}
                    onDelete={handleDelete}
                  />
                ))}
              </div>
            )}
          </section>
        </div>

        <aside className="space-y-4">
          <PredictionPanel />
          <AtRiskPanel onCountChange={setAtRiskCount} />
        </aside>
      </main>

      <AppointmentFormDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        clients={clients}
        services={services}
        appointment={editingAppointment}
        onLoadSamples={handleLoadSamples}
        isLoadingSamples={isSeeding}
        onSubmit={async (payload) => {
          if (editingAppointment) {
            await editAppointment(editingAppointment.id, payload);
          } else {
            await addAppointment(payload);
          }
        }}
      />
    </div>
  );
}
