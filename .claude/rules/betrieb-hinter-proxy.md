# Betrieb hinter dem Proxy (Crucible / VS Code)

In der Trainings-Umgebung wird die App **nicht** unter `localhost:3000` im Browser
geöffnet, sondern über einen Proxy unter einem Unterpfad:

```
https://crucible.ch.innoq.io/t/<token>/s/<session>/proxy/3000/
```

Der konkrete Pfad steht in der Env-Variable `VSCODE_PROXY_URI`
(z. B. `https://crucible.ch.innoq.io/t/.../s/.../proxy/{{port}}/`).

## Symptom

Im Browser viele **404** auf `/_next/static/chunks/*.js` (webpack.js, main-app.js,
page.js …), die Seite bleibt beim Laden hängen.

## Ursache

Next.js erzeugt standardmäßig **absolute** Asset-Pfade (`/_next/...`). Der Browser
löst die gegen die nackte Origin auf (`crucible.ch.innoq.io/_next/...`) — also **ohne**
den `…/proxy/3000/`-Prefix. Der Proxy findet dort nichts → 404. Dasselbe passiert mit
absoluten `fetch("/api/...")`-Aufrufen.

## Fix

1. **Assets** – in `next.config.mjs` `assetPrefix` aus `VSCODE_PROXY_URI` ableiten
   (mit Fallback `undefined` für lokal):

   ```js
   const proxyUri = process.env.VSCODE_PROXY_URI;
   const assetPrefix = proxyUri
     ? new URL(proxyUri.replace("{{port}}", "3000")).pathname.replace(/\/$/, "")
     : undefined;
   const nextConfig = { assetPrefix };
   ```

   Damit bekommen Asset-URLs den Proxy-Pfad vorangestellt; der Proxy strippt ihn beim
   Weiterleiten wieder, sodass die Dateien unter `/_next/...` auf `localhost:3000`
   gefunden werden.

2. **API-Calls** – im Client **relativ** statt absolut fetchen (kein führender Slash):

   ```js
   fetch("api/standorte")   // nicht "/api/standorte"
   ```

   Das funktioniert lokal (`localhost:3000/api/standorte`) und hinter dem Proxy
   (`…/proxy/3000/api/standorte`) gleichermaßen.

3. Nach Änderung an `next.config.mjs` den Dev-Server **neu starten** (`npm run dev`).

> Hinweis: `basePath` ist hier **nicht** geeignet, weil der Proxy den Pfad-Prefix beim
> Weiterleiten entfernt — der Dev-Server würde die Seiten dann unter dem falschen Pfad
> erwarten und 404 liefern.

## Vite (Frontend-Prototyp)

Das Frontend nutzt **Vite**, nicht Next.js. Dieselbe Proxy-Problematik (weiße Seite,
404 auf `/@vite/client`, `/src/*.tsx`) tritt dort auf, der Fix unterscheidet sich aber.
→ Skill **`vite-hinter-proxy`** (`.claude/skills/vite-hinter-proxy/`) enthält Ursache,
verifizierte `vite.config.ts`-Konfiguration und Verifikationsschritte.
