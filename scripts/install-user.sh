#!/usr/bin/env bash
set -euo pipefail
# User-level installation only. Does NOT modify PAM or system login.
if [[ "${EUID}" -eq 0 ]]; then
  echo "Run as a normal user (no sudo)." >&2
  exit 1
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${HOME}/.local/share/bioauth/venv"
mkdir -p "$(dirname "$VENV")" "${HOME}/.local/bin"
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install "$ROOT"
ln -sfn "$VENV/bin/bioauth" "${HOME}/.local/bin/bioauth"
echo "Installed: ${HOME}/.local/bin/bioauth"
echo "Download YuNet and SFace models as described in README before enrollment."
echo "PAM authentication has NOT been enabled."
