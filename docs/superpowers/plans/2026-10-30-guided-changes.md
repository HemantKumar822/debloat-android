# Guided changes and black theme

User delegated implementation and design decisions. Keep Python 3.10+, no runtime dependencies, local Markdown outputs, no deletion or settings writes.

## Design
Separate the read-only audit adapter from an experimental typed change adapter. Start with a single reviewed third-party package on owner user 0; reject system/core packages, multi-user devices, active roles, device administration, shared UID and sensitive bound services. This is a conservative first action scope, not universal system debloating.

Plan records device/build identity, package version and original enabled setting, reviewer reason and evidence. Approval is the SHA-256 of the full plan. Expire plans after 15 minutes and repeat preflight before apply. Create and fsync an exclusive recovery receipt before any write. On uncertain outcomes stop; never claim nothing changed. Restore exact default/enabled state from that receipt, checking identity and version again. No automatic batch, uninstall, data clearing, permission changes or settings writes.

The release is 0.4 experimental. Real-device/OEM validation remains a release blocker for a stable full version; disclose this prominently. Development does not authorize touching a phone.

Visual direction: preserve warm light mode; true black #000 dark canvas, #090909 surfaces, #f1eee9 text, warm orange accent. Remove theme button border/background while retaining keyboard focus. A low-opacity pixel lattice responds to pointer and scroll; pause and reduced motion remain supported.

## Implementation and checks
- [ ] Add failing tests for planning, consent, stale/tampered plans, state drift, command injection, uncertain mutation, durable receipt and exact restore.
- [ ] Implement separate changes module and plan/apply/restore CLI with explicit experimental opt-in.
- [ ] Update skill instructions, references, installer message, packaging manifest, README and website capability copy.
- [ ] Implement black theme and restrained continuous pixel lattice.
- [ ] Run full tests, syntax checks, browser checks and independent safety review; rebuild curated ZIP.
- [ ] Publish matching website and GitHub source; report physical-device validation limit.

ADB state semantics source: https://android.googlesource.com/platform/frameworks/base/+/73b787b38a0b25c7cfa3fec69e1cbddbd1b1a0b8/services/core/java/com/android/server/pm/PackageManagerShellCommand.java
