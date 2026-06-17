#!/usr/bin/env bash
#
# install-sdk.sh — Installiert das Python-SDK (Toolchain) für die Backend-
# Entwicklung mit FastAPI (siehe docs/architektur/adrs/ADR-004).
#
# Installiert den Python-3-Interpreter, das venv-Modul (inkl. ensurepip) und
# pip — also alles, was zum Anlegen einer virtuellen Umgebung und zum
# Installieren der Backend-Dependencies nötig ist. Das Skript ist idempotent:
# ist die Toolchain bereits einsatzbereit, passiert nichts.
#
# Nach einem Neustart des Codespaces ggf. erneut ausführen:
#   ./scripts/install-sdk.sh
#
set -euo pipefail

log() { printf '\033[1;34m[install-sdk]\033[0m %s\n' "$*"; }

# Python-Interpreter, venv (ensurepip) und pip. python3-venv zieht die zur
# Distribution passende Variante (z. B. python3.13-venv) nach.
PYTHON_DEPS=(python3 python3-venv python3-pip)

# Einsatzbereit = python3 vorhanden UND venv/ensurepip nutzbar (sonst schlägt
# `python3 -m venv` mit "ensurepip is not available" fehl).
python_ready() {
  command -v python3 >/dev/null 2>&1 && python3 -c 'import venv, ensurepip' >/dev/null 2>&1
}

# 1) Schon alles da? -> fertig.
if python_ready; then
  log "Python ist bereits einsatzbereit: $(python3 --version) (venv + pip verfügbar)"
  exit 0
fi

# 2) Toolchain via apt installieren.
log "Installiere Python-Toolchain (${PYTHON_DEPS[*]}) ..."
sudo apt-get update -y
sudo apt-get install -y "${PYTHON_DEPS[@]}"

# 3) Verifizieren.
if python_ready; then
  log "Installiert: $(python3 --version) (venv + pip verfügbar)"
  log "Fertig. Dependencies installiert der postCreateCommand bzw.:"
  log "  python3 -m venv backend/.venv && backend/.venv/bin/pip install -r backend/requirements.txt"
else
  log "FEHLER: Python lässt sich nach der Installation nicht wie erwartet nutzen." >&2
  python3 --version || true
  exit 1
fi
