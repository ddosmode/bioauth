# PAM security audit — preliminary, NOT approved for production

## Findings
- **Critical:** The historical PAM recipe uses `auth sufficient pam_exec.so`, potentially bypassing other authentication checks. Do not enable this recipe.
- **High:** `pam_exec` and the wrapper run in privileged authentication contexts. They require explicit executable and environment control, and isolation of biometric templates.
- **High:** RGB-only verification has no robust anti-spoofing; photographs and replay attacks are in scope.
- **High:** The CLI currently checks system and per-user enrollment locations; system authorization and file ownership policy require redesign.
- **Medium:** Authentication timeout is 2.5 seconds; camera/model initialization may cause unreliable login.
- **Medium:** Logging, account lockout, rate limits, and recovery have not been independently assessed.

## Current mitigation
The user installer never modifies PAM. The PAM bridge remains experimental. **Do not copy the existing PAM example into system configuration.** Keep password authentication enabled.

## Release gate
Independent security review, threat model, anti-spoofing testing, explicit PAM policy design, permissions audit, integration testing in a disposable VM, and recovery procedure are required before enabling system login.
