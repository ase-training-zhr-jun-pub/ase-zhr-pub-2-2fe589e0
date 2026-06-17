import { useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { ChevronLeft, ImageIcon, MapPin, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Separator } from "@/components/ui/separator"
import { AusstattungListe } from "@/components/ausstattung-badge"
import { VerfuegbarkeitBadge } from "@/pages/raeume-finden"
import { useBooking } from "@/lib/booking-context"
import {
  berechneDauer,
  getRaum,
  getStandort,
  istRaumVerfuegbar,
} from "@/lib/mock-data"
import { formatDatumLang } from "@/lib/date"

export function RaumDetail() {
  const { raumId } = useParams()
  const navigate = useNavigate()
  const { suche, bucheRaum } = useBooking()

  const [titel, setTitel] = useState("")
  const [notiz, setNotiz] = useState("")

  const raum = raumId ? getRaum(raumId) : undefined

  if (!raum) {
    return (
      <div className="space-y-4">
        <p className="text-muted-foreground">Dieser Raum existiert nicht.</p>
        <Button
          variant="outline"
          nativeButton={false}
          render={<Link to="/">Zurück zur Raumliste</Link>}
        />
      </div>
    )
  }

  const standort = getStandort(raum.standortId)
  const verfuegbar = istRaumVerfuegbar(
    raum.id,
    suche.datum,
    suche.startzeit,
    suche.endzeit,
  )
  const titelGueltig = titel.trim().length > 0
  const absendbar = verfuegbar && titelGueltig

  function absenden() {
    if (!absendbar || !raum) return
    bucheRaum({
      raumId: raum.id,
      datum: suche.datum,
      startzeit: suche.startzeit,
      endzeit: suche.endzeit,
      titel: titel.trim(),
      notiz: notiz.trim() || undefined,
    })
    navigate("/buchung/bestaetigung")
  }

  return (
    <div className="space-y-6">
      <Button
        variant="ghost"
        className="-ml-2 h-8 text-muted-foreground"
        nativeButton={false}
        render={
          <Link to="/">
            <ChevronLeft className="size-4" />
            Zurück zur Raumliste
          </Link>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        {/* Raumdetails (CLVN-006) */}
        <Card className="overflow-hidden">
          <div className="grid aspect-[16/7] place-items-center bg-muted text-muted-foreground">
            <ImageIcon className="size-10" />
          </div>
          <CardHeader>
            <div className="flex items-start justify-between gap-2">
              <CardTitle className="text-2xl">{raum.name}</CardTitle>
              <VerfuegbarkeitBadge verfuegbar={verfuegbar} />
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <Users className="size-4" />
                {raum.kapazitaet} Personen
              </span>
              <span className="flex items-center gap-1.5">
                <MapPin className="size-4" />
                {standort?.name} · {raum.etage} · Raum {raum.raumnummer}
              </span>
            </div>
          </CardHeader>
          <CardContent className="space-y-5">
            <p className="text-sm">{raum.beschreibung}</p>
            <div className="space-y-2">
              <h3 className="text-sm font-medium">Ausstattung</h3>
              <AusstattungListe ausstattung={raum.ausstattung} />
            </div>
          </CardContent>
        </Card>

        {/* Buchung (CLVN-016 / CLVN-019) */}
        <Card className="h-fit lg:sticky lg:top-24">
          <CardHeader>
            <CardTitle>Buchung</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <dl className="space-y-1.5 text-sm">
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Raum</dt>
                <dd className="font-medium">{raum.name}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Standort</dt>
                <dd className="font-medium">{standort?.name}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-muted-foreground">Datum</dt>
                <dd className="text-right font-medium">
                  {formatDatumLang(suche.datum)}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Zeit</dt>
                <dd className="font-medium">
                  {suche.startzeit}–{suche.endzeit} (
                  {berechneDauer(suche.startzeit, suche.endzeit)})
                </dd>
              </div>
            </dl>

            <Separator />

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

            {!verfuegbar && (
              <p className="text-sm text-destructive">
                Dieser Raum ist im gewählten Zeitraum belegt. Bitte wähle einen
                anderen Raum oder Zeitraum.
              </p>
            )}

            <Button className="w-full" disabled={!absendbar} onClick={absenden}>
              Buchung absenden
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
