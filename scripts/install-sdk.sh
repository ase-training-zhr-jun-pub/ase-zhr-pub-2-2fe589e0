#!/usr/bin/env bash
#
# install-sdk.sh — Installiert das Swift-SDK (Toolchain) für die Backend-
# Entwicklung mit Vapor (siehe docs/architektur/adrs/ADR-001).
#
# Verwendet Swiftly, den offiziellen Swift-Toolchain-Installer (swift.org),
# und installiert die von der Toolchain benötigten System-Bibliotheken.
# Das Skript ist idempotent: läuft Swift bereits, wird es übersprungen.
#
# Nach einem Neustart des Codespaces ggf. erneut ausführen:
#   ./scripts/install-sdk.sh
#
set -euo pipefail

log() { printf '\033[1;34m[install-sdk]\033[0m %s\n' "$*"; }

SWIFTLY_HOME="${SWIFTLY_HOME_DIR:-$HOME/.local/share/swiftly}"
SWIFTLY_ENV="$SWIFTLY_HOME/env.sh"

# System-Bibliotheken, die die Swift-Toolchain zur Laufzeit und zum Bauen von
# Paketen (SwiftPM/Vapor) benötigt. g++ zieht die passende libstdc++-*-dev der
# Distribution (Debian 13: gcc-14), daher kein fest verdrahtetes libstdc++-N-dev.
SWIFT_DEPS=(
  binutils gcc g++ pkg-config uuid-dev
  libicu-dev libcurl4-openssl-dev libedit-dev libsqlite3-dev
  libncurses-dev libpython3-dev libxml2-dev
)

load_env() { [ -f "$SWIFTLY_ENV" ] && . "$SWIFTLY_ENV" && hash -r || true; }
swift_runs() { command -v swift >/dev/null 2>&1 && swift --version >/dev/null 2>&1; }

install_system_deps() {
  log "Installiere System-Abhängigkeiten der Toolchain ..."
  sudo apt-get update -y
  sudo apt-get install -y "${SWIFT_DEPS[@]}"
}

# 1) Läuft Swift bereits? -> fertig.
load_env
if swift_runs; then
  log "Swift ist bereits einsatzbereit: $(swift --version | head -1)"
  exit 0
fi

# 2) Toolchain via Swiftly installieren, falls noch kein swift-Binary vorhanden.
if ! command -v swift >/dev/null 2>&1; then
  log "Installiere Grundpakete (curl, ca-certificates) ..."
  sudo apt-get update -y
  sudo apt-get install -y curl ca-certificates

  ARCH="$(uname -m)"
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  log "Lade Swiftly für $ARCH ..."
  curl -fsSL -o "$TMP/swiftly.tar.gz" "https://download.swift.org/swiftly/linux/swiftly-${ARCH}.tar.gz"
  tar zxf "$TMP/swiftly.tar.gz" -C "$TMP"

  # Hinweis Plattform: Swiftly erkennt Debian 13 (trixie) nicht automatisch
  # ("Unsupported Linux platform"). Wir geben daher explizit die kompatible
  # Debian-12-Toolchain an – ihre Binaries laufen unter der neueren glibc von
  # trixie. Überschreibbar per Umgebungsvariable SWIFT_PLATFORM.
  SWIFT_PLATFORM="${SWIFT_PLATFORM:-debian12}"
  log "Initialisiere Swiftly und installiere die neueste Swift-Toolchain (Plattform: $SWIFT_PLATFORM) ..."
  "$TMP/swiftly" init --assume-yes --quiet-shell-followup --overwrite --platform "$SWIFT_PLATFORM"
  load_env
fi

# 3) System-Abhängigkeiten installieren (Swiftly gibt sie nur aus, installiert
#    sie aber nicht selbst).
install_system_deps

# 4) Verifizieren.
load_env
if swift_runs; then
  log "Installiert: $(swift --version | head -1)"
  log "Fertig. In neuen Terminals steht 'swift' automatisch auf dem PATH"
  log "(über $SWIFTLY_ENV, in das Shell-Profil eingetragen)."
else
  log "FEHLER: Swift lässt sich nach der Installation nicht ausführen." >&2
  swift --version || true
  exit 1
fi
