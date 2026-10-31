#!/usr/bin/env bash
set -euo pipefail
# Non-destructive compatibility probe for GNOME Control Center native sidebar.
echo "BioAuth native Settings compatibility check"
if ! command -v gnome-control-center >/dev/null 2>&1; then
  echo "ERROR: GNOME Control Center not installed." >&2; exit 2
fi
os_id="$(. /etc/os-release; echo "${ID:-unknown}")"
os_version="$(. /etc/os-release; echo "${VERSION_ID:-unknown}")"
gnome_version="$(gnome-control-center --version 2>&1 | head -n 1)"
session="${XDG_CURRENT_DESKTOP:-unknown}"
printf 'OS: %s %s\nDesktop: %s\nControl Center: %s\n' "$os_id" "$os_version" "$session" "$gnome_version"
echo "Native sidebar panels are compiled into the distribution-specific Control Center."
echo "This project does not replace or patch system GNOME packages automatically."
echo "Status: native panel integration is not yet implemented for this build."
exit 3
