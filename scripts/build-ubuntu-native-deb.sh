#!/usr/bin/env bash
set -Eeuo pipefail
# Build a self-contained BioAuth-enabled GNOME Control Center package.
# Execute in an isolated Ubuntu 26.04 build environment (e.g., CI container).
export DEBIAN_FRONTEND=noninteractive
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/dist}"
mkdir -p "$OUT" /tmp/bioauth-native-build
. /etc/os-release
if [[ "$ID" != "ubuntu" || "$VERSION_ID" != "26.04" ]]; then
  echo "This binary build targets Ubuntu 26.04 (detected: $ID $VERSION_ID)" >&2
  exit 2
fi
apt-get update
apt-get install -y --no-install-recommends ca-certificates git python3 python3-opencv python3-numpy python3-gi wget xz-utils dpkg-dev gettext meson ninja-build pkg-config build-essential devscripts
cat > /etc/apt/sources.list.d/bioauth-build-sources.sources <<'SOURCES'
Types: deb-src
URIs: http://archive.ubuntu.com/ubuntu/
Suites: resolute resolute-updates resolute-backports
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

Types: deb-src
URIs: http://security.ubuntu.com/ubuntu/
Suites: resolute-security
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
SOURCES
apt-get update
apt-get build-dep -y --no-install-recommends gnome-control-center
cd /tmp/bioauth-native-build
apt-get source gnome-control-center
SRC="$(find . -maxdepth 1 -mindepth 1 -type d -name 'gnome-control-center-*' | head -1)"
if [[ -z "$SRC" ]]; then echo "GNOME source extraction failed" >&2; exit 1; fi
python3 "$ROOT/scripts/patch-gnome-control-center.py" "$SRC"
meson setup build "$SRC" --prefix=/opt/bioauth/native --buildtype=release
meson compile -C build -j 2
PKG="/tmp/bioauth-native-build/package"
mkdir -p "$PKG"
DESTDIR="$PKG" meson install -C build
# Only the native GNOME binary and assets, not foreign launcher services,
# are installed under /opt. The system app gets a reversible wrapper.
if [[ ! -x "$PKG/opt/bioauth/native/bin/gnome-control-center" ]]; then
  echo "GNOME binary was not produced" >&2; exit 1
fi
mkdir -p "$PKG/usr/share/applications" "$PKG/usr/lib/bioauth" "$PKG/usr/bin" "$PKG/usr/share/bioauth/models" "$PKG/DEBIAN"
cp "$PKG/opt/bioauth/native/share/applications/gnome-bioauth-panel.desktop" "$PKG/usr/share/applications/gnome-bioauth-panel.desktop"
cp -a "$ROOT/src" "$PKG/usr/lib/bioauth/"
find "$PKG/usr/lib/bioauth" -name __pycache__ -type d -prune -exec rm -rf {} +
# No pip/network needed on the installed machine; distro OpenCV and NumPy are dependencies.
cat > "$PKG/usr/bin/bioauth" <<'BIN'
#!/bin/sh
export PYTHONPATH="/usr/lib/bioauth${PYTHONPATH:+:$PYTHONPATH}"
exec /usr/bin/python3 -m src.cli "$@"
BIN
chmod 755 "$PKG/usr/bin/bioauth"
cp "$ROOT/scripts/bioauth-ui" "$PKG/usr/bin/bioauth-ui"
chmod 755 "$PKG/usr/bin/bioauth-ui"
python3 - "$PKG/usr/share/bioauth/models" "$ROOT" <<'PY'
import sys
sys.path.insert(0, sys.argv[2])
from src.models import install_models
print(install_models(destination=sys.argv[1]))
PY
# Models are public data; make readable by the desktop user.
chmod -R a+rX "$PKG/usr/share/bioauth/models"
cat > "$PKG/DEBIAN/control" <<'CONTROL'
Package: bioauth-faceid
Version: 0.5.0
Section: gnome
Priority: optional
Architecture: amd64
Maintainer: BioAuth Project <noreply@github.com>
Depends: gnome-control-center (>= 1:50~), gnome-control-center (<< 1:51~), python3, python3-opencv, python3-numpy, python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1, policykit-1, ${misc:Depends}
Description: Native BioAuth Face ID panel inside GNOME Settings on Ubuntu 26.04
 Installs a matching GNOME Control Center with the Face ID sidebar panel.
 Preserves and restores Ubuntu's original GNOME binary through dpkg-divert.
CONTROL
# Do not include a literal substitution variable that dpkg-deb cannot resolve.
sed -i 's/, ${misc:Depends}//' "$PKG/DEBIAN/control"
cat > "$PKG/DEBIAN/postinst" <<'POSTINST'
#!/bin/sh
set -eu
if [ "${1:-}" = configure ]; then
  if [ -x /usr/bin/gnome-control-center ] && ! dpkg-divert --list /usr/bin/gnome-control-center | grep -q bioauth-faceid; then
    dpkg-divert --package bioauth-faceid --add --rename --divert /usr/bin/gnome-control-center.bioauth-original /usr/bin/gnome-control-center
  fi
  if [ -x /usr/bin/gnome-control-center.bioauth-original ]; then
    cat > /usr/bin/gnome-control-center <<'WRAPPER'
#!/bin/sh
if [ -x /opt/bioauth/native/bin/gnome-control-center ]; then
  export XDG_DATA_DIRS="/opt/bioauth/native/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
  exec /opt/bioauth/native/bin/gnome-control-center "$@"
fi
exec /usr/bin/gnome-control-center.bioauth-original "$@"
WRAPPER
    chmod 755 /usr/bin/gnome-control-center
  fi
  command -v update-desktop-database >/dev/null && update-desktop-database /usr/share/applications || true
fi
exit 0
POSTINST
cat > "$PKG/DEBIAN/postrm" <<'POSTRM'
#!/bin/sh
set -eu
case "${1:-}" in
  remove|purge|abort-install)
    if dpkg-divert --list /usr/bin/gnome-control-center | grep -q bioauth-faceid; then
      if [ -e /usr/bin/gnome-control-center ] && grep -q '/opt/bioauth/native/bin/gnome-control-center' /usr/bin/gnome-control-center 2>/dev/null; then
        rm -f /usr/bin/gnome-control-center
      fi
      dpkg-divert --package bioauth-faceid --remove --rename --divert /usr/bin/gnome-control-center.bioauth-original /usr/bin/gnome-control-center
    fi
    ;;
esac
exit 0
POSTRM
chmod 755 "$PKG/DEBIAN/postinst" "$PKG/DEBIAN/postrm"
# Do not include conflicting GNOME .desktop/DBus launcher files installed by Meson.
rm -f "$PKG/opt/bioauth/native/share/applications/org.gnome.Settings.desktop"
rm -f "$PKG/opt/bioauth/native/share/dbus-1/services/org.gnome.Settings.service"
dpkg-deb --build --root-owner-group "$PKG" "$OUT/BioAuth-FaceID-Ubuntu-26.04-amd64.deb"
dpkg-deb -I "$OUT/BioAuth-FaceID-Ubuntu-26.04-amd64.deb"
dpkg-deb -c "$OUT/BioAuth-FaceID-Ubuntu-26.04-amd64.deb" | grep -E '(/gnome-control-center|bioauth-panel.desktop|/bin/bioauth)' | head -35
