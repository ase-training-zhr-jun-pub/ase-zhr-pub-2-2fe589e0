import { NavLink, Outlet } from "react-router-dom"
import { CalendarDays, MapPin } from "lucide-react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useBooking } from "@/lib/booking-context"
import { getStandort, STANDORTE } from "@/lib/mock-data"
import { cn } from "@/lib/utils"

const NAV = [
  { to: "/", label: "Räume finden", end: true },
  { to: "/meine-buchungen", label: "Meine Buchungen", end: false },
]

export function AppLayout() {
  const { suche, setSuche } = useBooking()

  return (
    <div className="flex min-h-svh flex-col bg-background">
      <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur">
        <div className="mx-auto flex h-16 w-full max-w-6xl items-center gap-6 px-4 sm:px-6">
          {/* Brand */}
          <NavLink to="/" className="flex items-center gap-2 font-semibold">
            <span className="grid size-8 place-items-center rounded-md bg-primary text-primary-foreground">
              <CalendarDays className="size-5" />
            </span>
            <span className="text-lg tracking-tight">Calvin</span>
          </NavLink>

          {/* Primärnavigation */}
          <nav className="hidden items-center gap-1 sm:flex">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  cn(
                    "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:text-foreground",
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          {/* Standort-Auswahl (jederzeit änderbar, CLVN-002) */}
          <div className="ml-auto flex items-center gap-2">
            <MapPin className="size-4 text-muted-foreground" />
            <Select
              value={suche.standortId}
              onValueChange={(standortId) => standortId && setSuche({ standortId })}
            >
              <SelectTrigger className="w-[140px]" aria-label="Standort auswählen">
                <SelectValue>{(v) => getStandort(v as string)?.name}</SelectValue>
              </SelectTrigger>
              <SelectContent>
                {STANDORTE.map((s) => (
                  <SelectItem key={s.id} value={s.id}>
                    {s.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Mobile-Navigation */}
        <nav className="flex items-center gap-1 border-t px-4 py-2 sm:hidden">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  "flex-1 rounded-md px-3 py-2 text-center text-sm font-medium transition-colors",
                  isActive
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:text-foreground",
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">
        <Outlet />
      </main>
    </div>
  )
}
