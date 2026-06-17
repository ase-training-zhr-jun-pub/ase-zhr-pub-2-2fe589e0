import { Link, Navigate } from "react-router-dom"
import { CalendarDays, CheckCircle2, Clock, MapPin } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { useBooking } from "@/lib/booking-context"
import { berechneDauer, getRaum, getStandort } from "@/lib/mock-data"
import { formatDatumLang } from "@/lib/date"

export function BuchungBestaetigung() {
  const { letzteBuchung } = useBooking()

  // Direktaufruf ohne vorherige Buchung -> zurück zur Suche.
  if (!letzteBuchung) {
    return <Navigate to="/" replace />
  }

  const raum = getRaum(letzteBuchung.raumId)
  const standort = raum ? getStandort(raum.standortId) : undefined

  return (
    <div className="mx-auto max-w-lg space-y-6 py-4">
      <div className="flex flex-col items-center text-center">
        <CheckCircle2 className="size-14 text-emerald-600" />
        <h1 className="mt-4 text-2xl font-semibold tracking-tight">
          Buchung bestätigt
        </h1>
        <p className="text-muted-foreground">
          Dein Konferenzraum ist verbindlich reserviert.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{letzteBuchung.titel}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3 text-sm">
            <div className="flex items-center gap-3">
              <MapPin className="size-4 text-muted-foreground" />
              <span>
                <span className="font-medium">{raum?.name}</span> · {standort?.name}
                {raum && ` · ${raum.etage}, Raum ${raum.raumnummer}`}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <CalendarDays className="size-4 text-muted-foreground" />
              <span>{formatDatumLang(letzteBuchung.datum)}</span>
            </div>
            <div className="flex items-center gap-3">
              <Clock className="size-4 text-muted-foreground" />
              <span>
                {letzteBuchung.startzeit}–{letzteBuchung.endzeit} (
                {berechneDauer(letzteBuchung.startzeit, letzteBuchung.endzeit)})
              </span>
            </div>
          </div>

          {letzteBuchung.notiz && (
            <>
              <Separator />
              <div className="space-y-1 text-sm">
                <p className="text-muted-foreground">Notiz</p>
                <p>{letzteBuchung.notiz}</p>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <div className="flex flex-col gap-2 sm:flex-row">
        <Button
          className="flex-1"
          nativeButton={false}
          render={<Link to="/meine-buchungen">Zu meinen Buchungen</Link>}
        />
        <Button
          variant="outline"
          className="flex-1"
          nativeButton={false}
          render={<Link to="/">Weiteren Raum buchen</Link>}
        />
      </div>
    </div>
  )
}
