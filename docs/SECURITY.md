# Security model and limitations

BioAuth 0.2 is an experimental **1:1** face-verification system, not a certified authentication factor.

- A commodity RGB webcam cannot reliably distinguish a live face from a photo or replay without tested anti-spoofing measures.
- Keep password authentication available. PAM integration is opt-in and must be independently reviewed.
- New enrollment stores embeddings only, with owner-only permissions; older installations may retain JPG frames and should be audited manually.
- Biometrics cannot be rotated like passwords. Never commit enrollment data or import third-party personal databases.
- The threshold is not calibrated for security-sensitive deployments.
- Do not enable biometric login for privileged accounts until a threat model, independent security review, and anti-spoofing evaluation are complete.
