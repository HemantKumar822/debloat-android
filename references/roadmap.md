# Release status and roadmap

## v0.4 experimental guided actions

Read-only audits and Markdown reports remain. New single-app plan/apply/restore workflow uses explicit device selection, approval digest, fresh preflight, 15-minute expiry, durable private receipt and state verification. Third-party owner-user apps only; system/core apps and uncertain state are blocked. No uninstall, data clearing, settings/permission writes or batch cleanup.

Automated tests use simulated ADB. **No physical-device validation.**

## Required before a stable full release

- Emulator and physical OEM/API matrix including unexpected dumpsys formats.
- Interrupted-command recovery, app updates, USB loss and essential-phone-function checks.
- Independent security review and live skill activation in each IDE.
- Device/build-specific reviewed system-package evidence, source licensing and expiry.
- Critical dependency protections beyond names and current default roles.
- Supported device/build matrix based on results, not universal-compatibility claims.

System-package changes stay blocked until evidence and device validation are complete. Do not claim v0.4 is stable, universally safe, or proven to improve speed, battery or privacy.
