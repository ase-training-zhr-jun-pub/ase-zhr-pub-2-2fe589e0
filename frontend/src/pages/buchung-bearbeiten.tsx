// Seite zum Ändern / Verschieben einer bestehenden Buchung (CLVN-027).

import { useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { de } from "date-fns/locale"
import { CalendarIcon, ChevronLeft } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Calendar } from "@/components/ui/calendar"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Separator } from "@/components/ui/separator"
import { useBooking } from "@/lib/booking-context"
import {
  getRaum,
  getRaeumeByStandort,
  ZEITSLOTS,
} from "@/lib/mock-data"
import { dateToIso, formatDatum, isoToDate } from "@/lib/date"
import { cn } from "@/lib/utils"

export function BuchungBearbeiten() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { meineBuchungen, aendereBuchung } = useBooking()

  // Buchung aus eigenem Bestand laden
  const buchung = meineBuchungen.find((b) => b.id === id)

  // Formular-State (mit Ausgangswerten vorbelegt)
  const [datum, setDatum] = useState(buchung?.datum ?? "")
  const [startzeit, setStartzeit] = useState(buchung?.startzeit ?? "")
  const [endzeit, setEndzeit] = useState(buchung?.endzeit ?? "")
  const [raumId, setRaumId] = useState(buchung?.raumId ?? "")
  const [titel, setTitel] = useState(buchung?.titel ?? "")
  const [notiz, setNotiz] = useState(buchung?.notiz ?? "")
  const [fehler, setFehler] = useState<string | null>(null)

  // Buchung nicht gefunden
  if (!buchung) {
    return (
      <div className="space-y-4">
        <p className="text-muted-foreground">
          Diese Buchung wurde nicht gefunden oder gehört dir nicht.
        </p>
        <Button
          variant="outline"
          nativeButton={false}
          render={<Link to="/meine-buchungen">Zurück zu meinen Buchungen</Link>}
        />
      </div>
    )
  }

  // Räume am selben Standort ermitteln
  const aktuellerRaum = getRaum(buchung.raumId)
  const standortId = aktuellerRaum?.standortId ?? ""
  const raeumeListe = getRaeumeByStandort(standortId)

  const zeitraumGueltig = endzeit > startzeit
  const titelGueltig = titel.trim().length > 0
  const speicherbar = zeitraumGueltig && titelGueltig

  function speichern() {
    if (!speicherbar) return
    setFehler(null)

    const ergebnis = aendereBuchung(buchung!.id, {
      datum,
      startzeit,
      endzeit,
      raumId,
      titel: titel.trim(),
      notiz: notiz.trim() || undefined,
    })

    if (ergebnis.ok) {
      toast.success("Buchung erfolgreich geändert.")
      navigate("/meine-buchungen")
    } else {
      setFehler(ergebnis.grund)
    }
  }

  return (
    <div className="space-y-6">
      <Button
        variant="ghost"
        className="-ml-2 h-8 text-muted-foreground"
        nativeButton={false}
        render={
          <Link to="/meine-buchungen">
            <ChevronLeft className="size-4" />
            Zurück zu meinen Buchungen
          </Link>
        }
      />

      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Buchung ändern</h1>
        <p className="text-muted-foreground">
          Passe Datum, Uhrzeit, Raum oder Details deiner Buchung an.
        </p>
      </div>

      <Card className="max-w-lg">
        <CardHeader>
          <CardTitle>Buchungsdetails</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Datum */}
          <div className="space-y-2">
            <Label>Datum</Label>
            <Popover>
              <PopoverTrigger
                render={
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start font-normal",
                      !datum && "text-muted-foreground",
                    )}
                  >
                    <CalendarIcon className="size-4" />
                    {datum ? formatDatum(datum) : "Datum wählen"}
                  </Button>
                }
              />
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  locale={de}
                  selected={datum ? isoToDate(datum) : undefined}
                  onSelect={(date) => date && setDatum(dateToIso(date))}
                  disabled={{ before: new Date() }}
                  autoFocus
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* Startzeit / Endzeit */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="startzeit">Von</Label>
              <Select value={startzeit} onValueChange={(v) => v && setStartzeit(v)}>
                <SelectTrigger id="startzeit" className="w-full">
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

            <div className="space-y-2">
              <Label htmlFor="endzeit">Bis</Label>
              <Select value={endzeit} onValueChange={(v) => v && setEndzeit(v)}>
                <SelectTrigger id="endzeit" className="w-full">
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
          </div>

          {!zeitraumGueltig && (
            <p className="text-sm text-destructive">
              Die Endzeit muss nach der Startzeit liegen.
            </p>
          )}

          {/* Raumwahl (selber Standort) */}
          <div className="space-y-2">
            <Label htmlFor="raum">Raum</Label>
            <Select value={raumId} onValueChange={(v) => v && setRaumId(v)}>
              <SelectTrigger id="raum" className="w-full">
                <SelectValue>
                  {(v) => getRaum(v as string)?.name ?? "Raum wählen"}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {raeumeListe.map((r) => (
                  <SelectItem key={r.id} value={r.id}>
                    {r.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Separator />

          {/* Titel */}
          <div className="space-y-2">
            <Label htmlFor="titel">
              Meetingtitel <span className="text-destructive">*</span>
            </Label>
            <Input
              id="titel"
              value={titel}
              onChange={(e) => setTitel(e.target.value)}
              placeholder="z.B. Sprint Planning Team Phoenix"
            />
          </div>

          {/* Notiz */}
          <div className="space-y-2">
            <Label htmlFor="notiz">Notiz (optional)</Label>
            <Textarea
              id="notiz"
              value={notiz}
              onChange={(e) => setNotiz(e.target.value)}
              placeholder="z.B. Whiteboard vorbereiten"
              rows={3}
            />
          </div>

          {/* Fehlermeldung */}
          {fehler && <p className="text-sm text-destructive">{fehler}</p>}

          {/* Aktionen */}
          <div className="flex gap-3 pt-2">
            <Button className="flex-1" disabled={!speicherbar} onClick={speichern}>
              Speichern
            </Button>
            <Button
              variant="outline"
              className="flex-1"
              nativeButton={false}
              render={<Link to="/meine-buchungen">Abbrechen</Link>}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
