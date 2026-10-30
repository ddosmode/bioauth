# Install without changing Linux login

Clone this repository and run:

```bash
git clone https://github.com/ddosmode/bioauth.git
cd bioauth
bash scripts/install-user.sh
~/.local/bin/bioauth --help
```

This installs a virtual environment in `~/.local/share/bioauth/venv` and a command symlink in `~/.local/bin`. It does **not** modify PAM, system authentication, or privileged configuration.

The ONNX models are intentionally not fetched by this installer. Obtain YuNet and SFace models from the OpenCV model repository, verify their provenance, and place them in `~/.config/bioauth/models` as described in README.

Do not run the experimental PAM integration on production machines.
