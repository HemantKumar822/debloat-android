# Evidence quality and safety policy

## Confidence rules

- **Observed fact**: ADB reports package X installed, disabled, or system-classified *in the observed package context*. Cite that observation as observed, not as an explanation of behavior.
- **Weak signal**: A package ID contains a name fragment such as `analytics`, `adservice`, or `appmarket`. These may be legitimate system components and must be presented only as *research candidates*.
- **Externally documented**: Manufacturer docs and reputable package analyses might explain purpose. Check Android version, OEM skin, region, and dependencies; record citations and uncertainty.
- **Verified candidate for a future change**: Need model/build-specific evidence, no vital dependencies, a documented rollback, appropriate backups, and explicit informed approval. The experimental change workflow accepts reviewer evidence but cannot independently prove it; system apps remain blocked. Read changes.md before any action.

## Never infer

- A library or package name alone proves tracking or maliciousness.
- An app is safe to disable because it sounds like an ad service.
- Disabled packages improve phone responsiveness or battery life.
- An app missing from a heuristic blocklist is safe to disable.
- Saving package states replaces a personal data backup.

## Sensitive components to treat with exceptional care

Launcher, SystemUI, phone/dialer, SMS, connectivity, SIM/eSIM, IMS, emergency calling, device policy, accessibility, permission controller, account and authentication managers, Play services, update agents, backup, encryption, keyboards, biometric services, and OEM-specific equivalents. The actual list is device-specific; the list above is not exhaustive.

## Reporting and user trust

- Explain what was measured and what was not.
- Record unavailability and gaps when a query fails; don't silently score unknown data as clean.
- Keep data local by default; avoid identifiers and private content not strictly needed.
- The user must remain in control; don't rush them through warnings.
- Before a stable change-engine release, require emulator/device testing, failure handling, privilege boundaries, idempotence, restoration and independent code review. v0.4 includes opt-in third-party changes with simulated tests; stable release still requires physical validation.

## Collection boundary

The CLI requires `audit --consent` before ADB initialization. This flag records
an explicit invocation choice, not proof of ownership or informed consent: an
agent must obtain authorization from the human first. `doctor` only discovers
connection state. All process invocations are discovery or exact allowlisted
reads, use a validated device identifier, have timeouts, and use no host shell.

The adapter is not a sandbox against arbitrary Python or external tools. There
is no mutation capability in the distributed CLI. Changing an app requires a
separate future design, validation and release, not another approval flag.

Primary and category package output must contain only package records. Category
sets must be consistent with the primary inventory. Empty filtered lists can
be valid; they are recorded as empty rather than missing. Optional failed reads
are recorded without raw error text or identifiers. These checks detect some
incomplete snapshots, but cannot prove that Android returned every package.

## Sources to consult

- [Android ADB documentation](https://developer.android.com/tools/adb)
- [Android Developer options](https://developer.android.com/studio/debug/dev-options)
- [UAD-NG](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation) for community intelligence, with independent verification and attention to GPL-3.0 licensing before data reuse.
- [Agent Skills specification](https://agentskills.io/specification)

