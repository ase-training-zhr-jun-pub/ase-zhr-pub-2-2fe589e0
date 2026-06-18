import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { de } from "date-fns/locale"
import { CalendarIcon, Check, MapPin, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { AusstattungListe } from "@/components/ausstattung-badge"
import { useBooking, type Suche } from "@/lib/booking-context"
import {
  berechneDauer,
  getRaeumeByStandort,
  getStandort,
  istRaumVerfuegbar,
  STANDORTE,
  ZEITSLOTS,
  type Raum,
} from "@/lib/mock-data"
import { dateToIso, formatDatum, isoToDate } from "@/lib/date"
import { cn } from "@/lib/utils"

export function RaeumeFinden() {
  const { suche, setSuche } = useBooking()
  const navigate = useNavigate()
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const standort = getStandort(suche.standortId)
  const raeume = getRaeumeByStandort(suche.standortId)
  const zeitraumGueltig = suche.endzeit > suche.startzeit

  // Der aktuell ausgewählte Raum (immer aus der sichtbaren Trefferliste, da die
  // Auswahl bei Änderung der Suche zurückgesetzt wird).
  const selectedRaum = selectedId
    ? raeume.find((r) => r.id === selectedId)
    : undefined

  // Auswahl zurücksetzen, wenn sich die Suche ändert – ein nicht mehr
  // sichtbarer oder belegter Raum soll nicht ausgewählt bleiben. State-Anpassung
  // beim Rendern statt im Effect (React-Empfehlung "you might not need an effect").
  const sucheKey = `${suche.standortId}|${suche.datum}|${suche.startzeit}|${suche.endzeit}`
  const [letzteSuche, setLetzteSuche] = useState(sucheKey)
  if (sucheKey !== letzteSuche) {
    setLetzteSuche(sucheKey)
    setSelectedId(null)
  }

  // Klick auf den bereits gewählten Raum hebt die Auswahl wieder auf.
  function toggleAuswahl(raumId: string) {
    setSelectedId((aktuell) => (aktuell === raumId ? null : raumId))
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Räume finden</h1>
        <p className="text-muted-foreground">
          Wähle Standort, Datum und Zeitraum, um verfügbare Konferenzräume zu sehen.
        </p>
      </div>

      {/* Filterleiste */}
      <Card>
        <CardContent className="flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-end">
          <div className="flex flex-col gap-1.5">
            <Label>Standort</Label>
            <Select
              value={suche.standortId}
              onValueChange={(standortId) => standortId && setSuche({ standortId })}
            >
              <SelectTrigger className="w-full sm:w-[180px]">
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

          <div className="flex flex-col gap-1.5">
            <Label>Datum</Label>
            <Popover>
              <PopoverTrigger
                render={
                  <Button
                    variant="outline"
                    className="w-full justify-start font-normal sm:w-[180px]"
                  >
                    <CalendarIcon className="size-4" />
                    {formatDatum(suche.datum)}
                  </Button>
                }
              />
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  locale={de}
                  selected={isoToDate(suche.datum)}
                  onSelect={(date) => date && setSuche({ datum: dateToIso(date) })}
                  disabled={{ before: new Date() }}
                  autoFocus
                />
              </PopoverContent>
            </Popover>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label>Von</Label>
            <Select
              value={suche.startzeit}
              onValueChange={(startzeit) => startzeit && setSuche({ startzeit })}
            >
              <SelectTrigger className="w-full sm:w-[110px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ZEITSLOTS.map((z) => (
                  <SelectItem key={z} value={z}>
                    {z}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label>Bis</Label>
            <Select
              value={suche.endzeit}
              onValueChange={(endzeit) => endzeit && setSuche({ endzeit })}
            >
              <SelectTrigger className="w-full sm:w-[110px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ZEITSLOTS.map((z) => (
                  <SelectItem key={z} value={z}>
                    {z}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="text-sm text-muted-foreground sm:pb-2">
            {zeitraumGueltig
              ? `Dauer: ${berechneDauer(suche.startzeit, suche.endzeit)}`
              : "Endzeit muss nach der Startzeit liegen"}
          </div>
        </CardContent>
      </Card>

      {/* Ergebnis */}
      <div className="flex items-baseline justify-between">
        <h2 className="text-lg font-medium">
          {raeume.length} Räume in {standort?.name}
        </h2>
        <span className="text-sm text-muted-foreground">
          {formatDatum(suche.datum)} · {suche.startzeit}–{suche.endzeit}
        </span>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {raeume.map((raum) => (
          <RaumKarte
            key={raum.id}
            raum={raum}
            verfuegbar={
              zeitraumGueltig &&
              istRaumVerfuegbar(raum.id, suche.datum, suche.startzeit, suche.endzeit)
            }
            selected={raum.id === selectedId}
            onSelect={() => toggleAuswahl(raum.id)}
          />
        ))}
      </div>

      {/* Auswahl-Zusammenfassung & Bestätigung (CLVN-029 / CLVN-030).
          Erscheint nur bei getroffener Auswahl und verschwindet wieder, sobald
          die Auswahl aufgehoben oder die Suche geändert wird. */}
      {selectedRaum && (
        <AuswahlZusammenfassung
          raum={selectedRaum}
          suche={suche}
          gueltig={zeitraumGueltig}
          onBestaetigen={() => navigate(`/raeume/${selectedRaum.id}`)}
        />
      )}
    </div>
  )
}

export function AuswahlZusammenfassung({
  raum,
  suche,
  gueltig,
  onBestaetigen,
}: {
  raum: Raum
  suche: Suche
  gueltig: boolean
  onBestaetigen: () => void
}) {
  const standort = getStandort(raum.standortId)
  return (
    <Card className="border-primary lg:sticky lg:bottom-4">
      <CardHeader>
        <CardTitle>Deine Auswahl</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-6 sm:grid-cols-2">
        {/* Raumdetails */}
        <div className="space-y-2">
          <div className="flex items-center justify-between gap-2">
            <span className="font-medium">{raum.name}</span>
            <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <Users className="size-4" />
              {raum.kapazitaet} Personen
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <MapPin className="size-4" />
            {standort?.name} · {raum.etage}
          </div>
          <AusstattungListe ausstattung={raum.ausstattung} />
        </div>

        {/* Zeitraum */}
        <dl className="space-y-1.5 text-sm sm:border-l sm:pl-6">
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">Datum</dt>
            <dd className="text-right font-medium">{formatDatum(suche.datum)}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">Zeit</dt>
            <dd className="font-medium">
              {suche.startzeit}–{suche.endzeit}
            </dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">Dauer</dt>
            <dd className="font-medium">
              {berechneDauer(suche.startzeit, suche.endzeit)}
            </dd>
          </div>
        </dl>
      </CardContent>
      <CardFooter>
        <Button className="w-full" disabled={!gueltig} onClick={onBestaetigen}>
          Auswahl bestätigen
        </Button>
      </CardFooter>
    </Card>
  )
}

export function RaumKarte({
  raum,
  verfuegbar,
  selected,
  onSelect,
}: {
  raum: Raum
  verfuegbar: boolean
  selected: boolean
  onSelect: () => void
}) {
  return (
    <Card className={cn("flex flex-col", selected && "ring-2 ring-primary")}>
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle>{raum.name}</CardTitle>
          <VerfuegbarkeitBadge verfuegbar={verfuegbar} />
        </div>
        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <Users className="size-4" />
          {raum.kapazitaet} Personen · {raum.etage}
        </div>
      </CardHeader>
      <CardContent className="flex-1">
        <AusstattungListe ausstattung={raum.ausstattung} />
      </CardContent>
      <CardFooter>
        <Button
          className="w-full"
          variant={verfuegbar ? "default" : "outline"}
          disabled={!verfuegbar}
          aria-pressed={verfuegbar ? selected : undefined}
          onClick={onSelect}
        >
          {verfuegbar ? (
            selected ? (
              <>
                <Check className="size-4" />
                Ausgewählt
              </>
            ) : (
              "Auswählen"
            )
          ) : (
            "Nicht verfügbar"
          )}
        </Button>
      </CardFooter>
    </Card>
  )
}

export function VerfuegbarkeitBadge({ verfuegbar }: { verfuegbar: boolean }) {
  return verfuegbar ? (
    <Badge className="shrink-0 border-transparent bg-emerald-600 text-white">
      Verfügbar
    </Badge>
  ) : (
    <Badge variant="destructive" className="shrink-0">
      Belegt
    </Badge>
  )
}

