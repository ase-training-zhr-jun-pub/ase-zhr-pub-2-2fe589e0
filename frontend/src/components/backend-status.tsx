import { useEffect, useState } from "react"
import { fetchHello } from "@/lib/api"
import { cn } from "@/lib/utils"

type Status =
  | { state: "loading" }
  | { state: "ok"; message: string }
  | { state: "error"; message: string }

/**
 * Kleiner Verbindungs-Indikator: fragt beim Laden den `/api/hello`-Endpunkt
 * des Backends an und zeigt das Ergebnis. Dient als Smoke-Test der
 * Front-/Backend-Verbindung (Übung 2).
 */
export function BackendStatus() {
  const [status, setStatus] = useState<Status>({ state: "loading" })

  useEffect(() => {
    let aktiv = true
    fetchHello()
      .then((text) => aktiv && setStatus({ state: "ok", message: text }))
      .catch(
        (err) =>
          aktiv && setStatus({ state: "error", message: String(err?.message ?? err) }),
      )
    return () => {
      aktiv = false
    }
  }, [])

  const dot =
    status.state === "ok"
      ? "bg-green-500"
      : status.state === "error"
        ? "bg-red-500"
        : "bg-yellow-500 animate-pulse"

  const label =
    status.state === "loading"
      ? "Verbinde mit Backend …"
      : status.state === "ok"
        ? `Backend: ${status.message}`
        : `Backend nicht erreichbar (${status.message})`

  return (
    <div
      className="flex items-center gap-2 text-xs text-muted-foreground"
      title="Verbindung zum Booking-Service (/api/hello)"
    >
      <span className={cn("inline-block size-2 rounded-full", dot)} />
      <span>{label}</span>
    </div>
  )
}
