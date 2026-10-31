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
install -m 755 "$ROOT/scripts/bioauth-settings" "${HOME}/.local/bin/bioauth-settings"
mkdir -p "${HOME}/.local/share/applications"
cat > "${HOME}/.local/share/applications/bioauth-settings.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=BioAuth — Face ID
Comment=Face enrollment and local biometric settings
Exec=${HOME}/.local/bin/bioauth-settings
Icon=avatar-default
Terminal=true
Categories=Settings;Security;
Keywords=Face ID;FaceID;BioAuth;биометрия;лицо;
EOF
echo "Installed: ${HOME}/.local/bin/bioauth"
"$VENV/bin/bioauth" install-models
echo "YuNet and SFace models installed with SHA256 verification."
echo "PAM authentication has NOT been enabled."
