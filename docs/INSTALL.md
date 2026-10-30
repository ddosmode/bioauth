# Install without changing Linux login

Clone this repository and run:

```bash
git clone https://github.com/ddosmode/bioauth.git
cd bioauth
bash scripts/install-user.sh
~/.local/bin/bioauth --help
```

This installs a virtual environment in `~/.local/share/bioauth/venv` and a command symlink in `~/.local/bin`. It does **not** modify PAM, system authentication, or privileged configuration.

The installer now downloads YuNet and SFace models from the OpenCV Zoo repository and verifies pinned SHA256 checksums. You can also run `bioauth install-models` manually. Installation aborts if checksums do not match.

Do not run the experimental PAM integration on production machines.
