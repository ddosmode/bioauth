# BioAuth — Face recognition for everyday Linux computers

**Your old computer has a webcam. Why shouldn't it recognize you?**

BioAuth is an open-source face-verification prototype for Linux, including older iMacs running Linux. It detects your face, converts its learned features into a compact numerical vector, and compares that vector with one saved earlier — locally, without a cloud service.

> **Early prototype, not production-grade security.** This is **not Apple Face ID**, nor a reverse-engineering of it. Unlike Apple's depth/infrared-based systems, this implementation uses an ordinary camera and currently has no liveness detection. Photos or video replays may fool it. Do not use it as the sole protection for sensitive systems.

## The big idea — explained simply

A photo is a grid of pixels. A recognition model turns a detected and aligned face into a **128-number embedding**: a list of learned features. When you return, it computes another vector and checks how similar the two are.

```text
Webcam → detect face (YuNet) → align face → 128-number vector (SFace)
                                               │
Saved vector ───────────────────────────────────┤
                                               ↓
                                     cosine similarity
                                               ↓
                                      match / no match
```

It's not a magical secret and not a simple pixel-by-pixel photo comparison. The neural network **learns** a useful representation; the vector is not a lossless copy of the photo. BioAuth uses OpenCV YuNet and SFace ONNX models. The current cosine similarity threshold is `0.40` — a prototype choice, not a certified security level.

## Current features

- Linux webcam capture using OpenCV / V4L2.
- Face detection, alignment, and 128-dimensional feature extraction.
- Three enrollment slots: `primary`, `alternative`, and `mask`.
- CLI commands: `enroll`, `verify`, `status`, `reset`.
- Experimental PAM authentication wrapper.
- On-device processing; no cloud verification service.

## Try it (development setup)

Requirements: Linux, Python 3, a V4L2-compatible camera, NumPy, and OpenCV with `FaceDetectorYN` and `FaceRecognizerSF` (typically `opencv-contrib-python`).

```bash
git clone https://github.com/ddosmode/bioauth.git
cd bioauth
python3 -m venv .venv
source .venv/bin/activate
pip install numpy opencv-contrib-python
```

Download the official YuNet and SFace ONNX models separately and put them in `~/.config/bioauth/models/` or `/etc/bioauth/models/`:

```text
face_detection_yunet_2023mar.onnx
face_recognition_sface_2021dec.onnx
```

Then:

```bash
python3 -m src.cli enroll "$USER" --slot primary
python3 -m src.cli status "$USER"
python3 -m src.cli verify "$USER"
python3 -m unittest discover -s tests
```

For a different webcam, pass `--device 1` **before** the command, e.g. `python3 -m src.cli --device 1 verify "$USER"`. Model downloading and portable installation are not automated yet.

## How the code is organized

| File | Purpose |
| --- | --- |
| `src/capture.py` | Captures a webcam frame |
| `src/detector.py` | Finds faces using YuNet |
| `src/recognizer.py` | Creates and compares SFace vectors |
| `src/cli.py` | Enrollment and verification commands |
| `pam/` | Experimental Linux PAM integration |
| `tests/` | Basic tests; some need local enrollment |
| `Makefile` | Test and installation targets |

## Security and privacy matter

The current enrollment code stores **both** the biometric vector (`.npy`) **and** the original camera frame (`.jpg`) in a local user/system configuration directory. Treat both as sensitive data. Never commit biometric profiles or share them in bug reports. The PAM wrapper currently contains a machine-specific filesystem path; review and fix it before attempting system integration. Keep a working password fallback and test failure cases before touching login or `sudo` configuration.

## Roadmap

- [ ] Portable installer and verified model downloads.
- [ ] Remove hard-coded paths from PAM integration.
- [ ] Harden permissions and storage of biometric profiles.
- [ ] Add liveness / anti-spoofing detection.
- [ ] Measure false acceptance, false rejection, and speed on real devices.
- [ ] Add automated CI tests and sample fixtures without personal data.
- [ ] Improve camera discovery and desktop enrollment UI.
- [ ] Document supported Linux distributions and hardware.

## Contributing

Contributions are welcome: issues, documentation, testing on old hardware, accessibility improvements, and pull requests. Include your Linux distribution, webcam model, OpenCV version, and reproducible steps. **Do not upload personal face photos or embeddings.**

## Philosophy

**The core idea is understandable: camera → learned numerical features → similarity comparison.** The difficult part isn't making a match — it's making the authentication robust against spoofing and failures. That's the challenge worth solving together.

BioAuth is independent and is not affiliated with Apple. **License pending:** until an explicit license is added, standard copyright restrictions apply.
