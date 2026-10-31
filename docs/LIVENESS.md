# Enrollment challenge and fast verification

The randomized motion challenge now runs **only during enrollment**. Verification captures a single frame to minimize latency.

**Security warning:** Single-frame RGB face matching has NO reliable presentation-attack detection. A printed photograph, replayed video, or injected camera stream may authenticate. This change improves convenience, not security. **Never enable PAM login on this basis.**

GNOME integration currently provides a searchable `BioAuth — Face ID` Settings-category launcher, **not** a native panel inside GNOME Control Center. The launcher requires Zenity for interactive choices.

Latency target is not verified; cold camera start and model initialization may exceed 100 ms. Real-device benchmarks and a trained, validated passive PAD model are required.
