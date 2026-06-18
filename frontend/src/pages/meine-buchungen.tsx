import { useState } from "react"
import { Link } from "react-router-dom"
import { CalendarDays, CalendarX2, ChevronRight, Clock, MapPin } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { useBooking } from "@/lib/booking-context"
import { getRaum, getStandort, HEUTE, type Buchung } from "@/lib/mock-data"
import { formatDatum } from "@/lib/date"

export function MeineBuchungen() {
  const { meineBuchungen } = useBooking()

  // Chronologisch sortieren (nächste zuerst), getrennt nach kommend/vergangen.
  const sortiert = [...meineBuchungen].sort((a, b) =>
    (a.datum + a.startzeit).localeCompare(b.datum + b.startzeit),
  )
  const kommend = sortiert.filter((b) => b.datum >= HEUTE)
  const vergangen = sortiert.filter((b) => b.datum < HEUTE).reverse()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Meine Buchungen</h1>
        <p className="text-muted-foreground">
          Übersicht deiner Raumbuchungen an allen Standorten.
        </p>
      </div>

      {meineBuchungen.length === 0 ? (
        <LeerHinweis />
      ) : (
        <div className="space-y-8">
          <section className="space-y-3">
            <h2 className="text-sm font-medium text-muted-foreground">
              Kommende Buchungen
            </h2>
            {kommend.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Keine kommenden Buchungen.
              </p>
            ) : (
              <div className="space-y-3">
                {kommend.map((b) => (
                  <BuchungZeile key={b.id} buchung={b} />
                ))}
              </div>
            )}
          </section>

          {vergangen.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-sm font-medium text-muted-foreground">
                Vergangen
              </h2>
              <div className="space-y-3">
                {vergangen.map((b) => (
                  <BuchungZeile key={b.id} buchung={b} vergangen />
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  )
}

function BuchungZeile({
  buchung,
  vergangen = false,
}: {
  buchung: Buchung
  vergangen?: boolean
}) {
  const { storniereBuchung } = useBooking()
  const raum = getRaum(buchung.raumId)
  const standort = raum ? getStandort(raum.standortId) : undefined
  const [popoverOffen, setPopoverOffen] = useState(false)

  function handleStornieren() {
    storniereBuchung(buchung.id)
    setPopoverOffen(false)
    toast.success(`Buchung "${buchung.titel}" wurde storniert.`)
  }

  return (
    <Card className={vergangen ? "opacity-70" : undefined}>
      <CardContent className="flex items-center gap-4">
        <div className="flex-1 space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="font-medium">{buchung.titel}</span>
            {vergangen && (
              <Badge variant="secondary" className="font-normal">
                Vergangen
              </Badge>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <CalendarDays className="size-4" />
              {formatDatum(buchung.datum)}
            </span>
            <span className="flex items-center gap-1.5">
              <Clock className="size-4" />
              {buchung.startzeit}–{buchung.endzeit}
            </span>
            <span className="flex items-center gap-1.5">
              <MapPin className="size-4" />
              {raum?.name} · {standort?.name}
            </span>
          </div>
        </div>
        {vergangen ? (
          <ChevronRight className="size-5 shrink-0 text-muted-foreground" />
        ) : (
          <Popover open={popoverOffen} onOpenChange={setPopoverOffen}>
            <PopoverTrigger
              render={
                <Button variant="outline" size="sm">
                  Stornieren
                </Button>
              }
            />
            <PopoverContent className="w-64">
              <p className="text-sm font-medium">Buchung wirklich stornieren?</p>
              <div className="mt-3 flex justify-end gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPopoverOffen(false)}
                >
                  Abbrechen
                </Button>
                <Button variant="destructive" size="sm" onClick={handleStornieren}>
                  Stornieren
                </Button>
              </div>
            </PopoverContent>
          </Popover>
        )}
      </CardContent>
    </Card>
  )
}

function LeerHinweis() {
  return (
    <Card>
      <CardContent className="flex flex-col items-center gap-4 py-12 text-center">
        <CalendarX2 className="size-10 text-muted-foreground" />
        <div>
          <p className="font-medium">Noch keine Buchungen</p>
          <p className="text-sm text-muted-foreground">
            Du hast noch keine Konferenzräume gebucht.
          </p>
        </div>
        <Button nativeButton={false} render={<Link to="/">Raum finden</Link>} />
      </CardContent>
    </Card>
  )
}
