#!/usr/bin/env python3
"""Patch GNOME Control Center source tree with a native BioAuth sidebar panel."""
import sys
from pathlib import Path

def replace_once(path, old, new):
    data = path.read_text()
    if new in data:
        return
    if old not in data:
        raise RuntimeError(f"Unsupported GNOME source layout: {path}")
    path.write_text(data.replace(old, new, 1))

def patch(root):
    root = Path(root)
    loader = root / "shell/cc-panel-loader.c"
    panels = root / "panels/meson.build"
    replace_once(loader, 'extern GType cc_applications_panel_get_type (void);',
                 'extern GType cc_bioauth_panel_get_type (void);\nextern GType cc_applications_panel_get_type (void);')
    replace_once(loader, '  PANEL_TYPE("applications",', '  PANEL_TYPE("bioauth",          cc_bioauth_panel_get_type,             NULL),\n  PANEL_TYPE("applications",')
    replace_once(panels, "  'applications',", "  'bioauth',\n  'applications',")
    target = root / "panels/bioauth"
    target.mkdir(exist_ok=True)
    (target / "meson.build").write_text("""panels_list += cappletname
desktop = 'gnome-@0@-panel.desktop'.format(cappletname)
i18n.merge_file(type: 'desktop', input: desktop + '.in', output: desktop,
  po_dir: po_dir, install: true, install_dir: control_center_desktopdir)
panels_libs += static_library(cappletname, files('cc-bioauth-panel.c'),
  include_directories: [top_inc, common_inc],
  dependencies: common_deps, c_args: cflags)
""")
    (target / "gnome-bioauth-panel.desktop.in").write_text("""[Desktop Entry]
Name=Face ID
Comment=BioAuth face authentication settings
Exec=gnome-control-center bioauth
Icon=avatar-default
Terminal=false
Type=Application
NoDisplay=true
Categories=GNOME;GTK;Settings;X-GNOME-PrivacySettings;
Keywords=Face;BioAuth;Biometrics;
""")
    (target / "cc-bioauth-panel.c").write_text(r'''#include <glib/gi18n.h>
#include "shell/cc-panel.h"

typedef struct {
  CcPanel parent_instance;
} CcBioauthPanel;
typedef CcPanelClass CcBioauthPanelClass;
G_DEFINE_TYPE (CcBioauthPanel, cc_bioauth_panel, CC_TYPE_PANEL)

static void
on_action (GtkButton *button, gpointer data)
{
  const char *action = g_object_get_data (G_OBJECT (button), "bioauth-action");
  const char *argv[] = { "/usr/bin/bioauth-ui", action, NULL };
  g_autoptr(GError) error = NULL;
  if (!g_spawn_async (NULL, (char **) argv, NULL,
                      G_SPAWN_SEARCH_PATH, NULL, NULL, NULL, &error))
    g_warning ("BioAuth action failed: %s", error->message);
}

static void
cc_bioauth_panel_init (CcBioauthPanel *self)
{
  GtkWidget *box = gtk_box_new (GTK_ORIENTATION_VERTICAL, 12);
  gtk_widget_set_margin_top (box, 24);
  gtk_widget_set_margin_start (box, 24);
  gtk_widget_set_margin_end (box, 24);
  gtk_widget_set_margin_bottom (box, 24);
  gtk_box_append (GTK_BOX (box), gtk_label_new (_("Face ID — BioAuth")));
  gtk_box_append (GTK_BOX (box), gtk_label_new (_("Experimental camera-based face login. A photo may defeat verification.")));
  const char *labels[] = { "Enroll and enable login", "Verify face", "Profile status", "Disable face login", NULL };
  const char *actions[] = { "activate", "verify", "status", "disable" };
  for (int i = 0; labels[i]; i++) {
    GtkWidget *button = gtk_button_new_with_label (labels[i]);
    g_object_set_data_full (G_OBJECT (button), "bioauth-action", g_strdup (actions[i]), g_free);
    g_signal_connect (button, "clicked", G_CALLBACK (on_action), NULL);
    gtk_box_append (GTK_BOX (box), button);
  }
  adw_navigation_page_set_child (ADW_NAVIGATION_PAGE (self), box);
}
static void
cc_bioauth_panel_class_init (CcBioauthPanelClass *klass)
{
}
''')
    print("Patched native BioAuth panel sources:", root)

if __name__ == "__main__":
    patch(sys.argv[1])
