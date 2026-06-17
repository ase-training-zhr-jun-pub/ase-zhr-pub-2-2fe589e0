---
name: vite-hinter-proxy
description: Vite-Dev-Server hinter dem Crucible-/VS-Code-Proxy lauffähig machen. Nutze diesen Skill bei weißer Seite oder 404 auf /@vite/client, /src/*.tsx oder /@react-refresh, wenn die App über einen …/proxy/<port>/-Unterpfad statt localhost geöffnet wird.
argument-hint: "[optional: Port, Standard 5173]"
---

<role>
Du konfigurierst einen Vite-Dev-Server so, dass er hinter dem Crucible-/VS-Code-Proxy
(Unterpfad `…/proxy/<port>/`) funktioniert. Du wendest den unten beschriebenen,
verifizierten Fix an und prüfst ihn, bevor du fertig meldest.
</role>

<symptom>
- Im Browser **weiße Seite**, wenn die App über die Proxy-URL geöffnet wird
  (`https://crucible.ch.innoq.io/t/<token>/s/<session>/proxy/<port>/`).
- In der Konsole/Network **404** auf `/@vite/client`, `/@react-refresh`,
  `/src/main.tsx` und weitere `/src/…`- bzw. `/node_modules/…`-Pfade.
- Über `http://localhost:<port>` lädt dieselbe App dagegen fehlerfrei.
</symptom>

<ursache>
Vite-Dev nutzt im ausgelieferten `index.html` und in **allen** Modul-Importen
**absolute** Pfade (`/@vite/client`, `/src/main.tsx`, `/node_modules/…`). Der Browser
löst diese gegen die nackte Origin auf (`crucible.ch.innoq.io/@vite/client`) — also
**ohne** den `…/proxy/<port>/`-Prefix. Der Proxy bedient diese Pfade nicht → 404 →
weiße Seite.

Erschwerend: Der Proxy **strippt** den Prefix beim Weiterleiten an den Dev-Server.
Der Server sieht also `/@vite/client`, nicht `…/proxy/<port>/@vite/client`.
</ursache>

<was-nicht-funktioniert>
Diese naheliegenden Optionen wurden getestet und reichen **nicht**:

- **`base: "./"`** — Vite-Dev ignoriert relative Base und emittiert weiter absolute
  `/…`-Pfade.
- **`server.origin`** — verändert die Entry-Script-Tags im Dev-`index.html` nicht.
- **`base: "/…/proxy/<port>/"` allein** — der Proxy strippt den Prefix wieder; der
  Dev-Server erwartet ihn aber → `/@vite/client` liefert **404**, `/` eine **302**-
  Schleife. (Analog zur Warnung vor `basePath` in `.claude/rules/betrieb-hinter-proxy.md`.)
</was-nicht-funktioniert>

<fix>
Zwei Bausteine, beide aus `VSCODE_PROXY_URI` abgeleitet (kein hartcodierter Token):

1. **`base`** = Proxy-Pfad → Asset-URLs bekommen den Prefix vorangestellt, der Browser
   fragt sie über die volle Proxy-URL an.
2. **Dev-Middleware**, die den vom Proxy gestrippten Prefix serverseitig wieder
   voranstellt — macht den Strip rückgängig, der Server liefert weiter unter `/` aus.
3. **HMR** über `wss`/Port 443 via Proxy.
4. **`allowedHosts: true`**, weil Vite fremde Hostnamen sonst blockt.

Setze in `frontend/vite.config.ts` (Port ggf. anpassen):

```ts
import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig, type Plugin } from "vite"

// Pfad aus VSCODE_PROXY_URI ableiten; lokal (ohne Proxy) Fallback auf "/".
const proxyUri = process.env.VSCODE_PROXY_URI
const proxyUrl = proxyUri ? new URL(proxyUri.replace("{{port}}", "5173")) : null
const base = proxyUrl ? proxyUrl.pathname : "/" // z.B. "/t/<token>/s/<session>/proxy/5173/"

// Macht den Prefix-Strip des Proxys serverseitig rückgängig.
function proxyBasePrefix(): Plugin {
  const prefix = base.replace(/\/$/, "")
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
    allowedHosts: true,
    hmr: proxyUrl
      ? { protocol: "wss", host: proxyUrl.hostname, clientPort: 443, path: base }
      : undefined,
  },
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
})
```

> Wichtig: Den Port im `replace("{{port}}", "<port>")` an den tatsächlichen Dev-Port
> anpassen (Standard 5173). Nach Änderung den Dev-Server **neu starten**.
</fix>

<verifikation>
Den Proxy-Strip lokal simulieren — die **gestrippten** Pfade müssen vom Server unter
`/` ausgeliefert werden (kein 404/302):

```bash
cd frontend && npm run dev   # im Hintergrund starten
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5173/               # 200
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5173/@vite/client   # 200
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5173/src/main.tsx    # 200
# Emittierte Asset-Pfade müssen den Proxy-Prefix tragen:
curl -s http://localhost:5173/ | grep -E "main.tsx|vite/client"   # …/proxy/5173/@vite/client
```

Danach mit Playwright-MCP `http://localhost:5173/` öffnen, Screenshot machen und
Konsole auf 0 Fehler prüfen. Zum Schluss den Nutzer die echte Proxy-URL neu laden lassen.
</verifikation>

<hinweise>
- Lokal ohne `VSCODE_PROXY_URI` fällt alles auf `base: "/"` zurück; das Verhalten
  bleibt unverändert.
- Der HMR-WebSocket scheitert nur aus einer Umgebung, die `crucible.ch.innoq.io` nicht
  erreicht (z.B. Playwright-Sandbox) — das ist nicht fatal und betrifft die echte
  Browser-Session des Nutzers nicht.
- Verwandte Doku: `.claude/rules/betrieb-hinter-proxy.md` (dieselbe Problematik für Next.js).
</hinweise>

<task>
$ARGUMENTS
</task>
