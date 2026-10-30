# bioauth

Biometric Face Authentication PAM module for Linux using OpenCV (YuNet + SFace).

## Overview

`bioauth` provides fast and lightweight facial recognition for Linux authentication (`sudo`, screen lock, GDM).

- **Detector**: YuNet ONNX (lightweight face detection model).
- **Recognizer**: SFace ONNX (128-dimensional facial embedding representation).
- **Architecture**: Modular Python service with fail-fast PAM integration (`pam_exec.so`).
- **Safety**: Safe fallback to standard PAM password prompts on any failure, camera busy state, or unrecognized face.

## Project Structure

```
bioauth/
├── src/
│   ├── capture.py      # Camera capture handling with strict timeouts
│   ├── detector.py     # YuNet face detector wrapper
│   ├── recognizer.py   # SFace face embedding & matching wrapper
│   └── cli.py          # Command-line interface (enrollment / verify)
├── pam/
│   ├── bioauth         # PAM configuration profile
│   └── bioauth-pam     # Executable wrapper for pam_exec
├── tests/              # Unit test suite
├── Makefile            # Build and installation helper
└── AGENTS.md           # Coding standards and guidelines
```

## Requirements

- Python 3.12+
- OpenCV with `FaceDetectorYN` and `FaceRecognizerSF` support
- PAM support (`pam_exec.so`)

## Installation

```bash
make test
sudo make install
```

## License

MIT
