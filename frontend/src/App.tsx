import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import { AppLayout } from "@/components/app-layout"
import { BookingProvider } from "@/lib/booking-context"
import { Toaster } from "@/components/ui/sonner"
import { RaeumeFinden } from "@/pages/raeume-finden"
import { RaumDetail } from "@/pages/raum-detail"
import { BuchungBestaetigung } from "@/pages/buchung-bestaetigung"
import { MeineBuchungen } from "@/pages/meine-buchungen"
import { BuchungBearbeiten } from "@/pages/buchung-bearbeiten"

function App() {
  return (
    <BookingProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<RaeumeFinden />} />
            <Route path="/raeume/:raumId" element={<RaumDetail />} />
            <Route path="/buchung/bestaetigung" element={<BuchungBestaetigung />} />
            <Route path="/buchung/:id/bearbeiten" element={<BuchungBearbeiten />} />
            <Route path="/meine-buchungen" element={<MeineBuchungen />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster />
    </BookingProvider>
  )
}

export default App
