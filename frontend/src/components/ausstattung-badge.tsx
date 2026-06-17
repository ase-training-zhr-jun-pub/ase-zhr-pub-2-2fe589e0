import {
  Monitor,
  PenLine,
  Video,
  Projector,
  Presentation,
  Phone,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import type { Ausstattung } from "@/lib/mock-data"

const ICONS: Record<Ausstattung, typeof Monitor> = {
  Bildschirm: Monitor,
  Whiteboard: PenLine,
  Videokonferenz: Video,
  Beamer: Projector,
  Flipchart: Presentation,
  Telefonkonferenz: Phone,
}

export function AusstattungBadge({ ausstattung }: { ausstattung: Ausstattung }) {
  const Icon = ICONS[ausstattung]
  return (
    <Badge variant="secondary" className="gap-1 font-normal">
      <Icon className="size-3.5" />
      {ausstattung}
    </Badge>
  )
}

export function AusstattungListe({ ausstattung }: { ausstattung: Ausstattung[] }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {ausstattung.map((a) => (
        <AusstattungBadge key={a} ausstattung={a} />
      ))}
    </div>
  )
}
