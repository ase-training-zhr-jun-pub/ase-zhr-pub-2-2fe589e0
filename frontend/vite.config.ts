import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig, type Plugin } from "vite"

// --- Betrieb hinter dem Crucible-/VS-Code-Proxy -----------------------------
// Die App wird nicht unter localhost:5173, sondern unter einem Unterpfad
// (…/proxy/5173/) ausgeliefert. Den konkreten Pfad liefert VSCODE_PROXY_URI.
const proxyUri = process.env.VSCODE_PROXY_URI
const proxyUrl = proxyUri ? new URL(proxyUri.replace("{{port}}", "5173")) : null
// z.B. "/t/<token>/s/<session>/proxy/5173/" — lokal undefined.
const base = proxyUrl ? proxyUrl.pathname : "/"

/**
 * Vite-Dev nutzt überall absolute Pfade (z.B. "/@vite/client", "/src/...").
 * Über `base` bekommen diese URLs den Proxy-Prefix vorangestellt, sodass der
 * Browser sie korrekt anfragt. Der Proxy strippt den Prefix beim Weiterleiten
 * aber wieder — der Dev-Server sieht also "/@vite/client" statt
 * "<base>/@vite/client" und würde 404 liefern. Diese Middleware setzt den
 * Prefix serverseitig wieder davor und macht den Strip damit rückgängig.
 */
function proxyBasePrefix(): Plugin {
  const prefix = base.replace(/\/$/, "") // ohne abschließenden Slash
  return {
    name: "crucible-proxy-base-prefix",
    configureServer(server) {
      server.middlewares.use((req, _res, next) => {
        if (req.url && prefix && !req.url.startsWith(prefix + "/") && req.url !== prefix) {
          req.url = prefix + req.url
        }
        next()
      })
    },
  }
}

export default defineConfig({
  base,
  plugins: [react(), tailwindcss(), proxyBasePrefix()],
  server: {
    host: "0.0.0.0",
    // Vite blockt unbekannte Hosts; hinter dem Proxy daher alle erlauben.
    allowedHosts: true,
    // HMR-WebSocket über den HTTPS-Proxy (wss, Port 443) statt direkt.
    hmr: proxyUrl
      ? { protocol: "wss", host: proxyUrl.hostname, clientPort: 443, path: base }
      : undefined,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
