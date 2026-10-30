# v0.4 validation — 2026-10-30

## Implemented

Separate experimental single-app plan/apply/restore executor. Explicit owner user 0, fresh package/build/version/state checks, approval digest, 15-minute plan expiry, conservative system/role/admin/service/shared-UID guards, durable exclusive recovery receipt, exact default/enabled restoration and verification. Audit adapter remains read-only. Markdown plan review, CLI gates, skill/reference/installer and curated ZIP updated.

## Evidence

- Full Python suite: 62 tests passed, including simulated CLI plan/apply/restore.
- Regression coverage: stale/edited plans, foreign device and version drift, uncertain submitted writes, immutable receipts, restore idempotence, exact original state, malformed/unsupported policy and roles, profiles, sensitive services, command injection and CLI opt-in gates.
- Independent review identified admin section parsing, package-versus-permission flag classification and recovery-envelope sizing issues; fixed with regression tests.
- JavaScript syntax checks for site.js, theme.js and motion.js passed.
- Browser: pure-black body computed rgb(0,0,0), theme button border 0px and transparent background; light/dark switching works; desktop no horizontal overflow; mobile 390px document width matches viewport; pause/resume works; no console errors observed.
- Native canvas pixel lattice, edge motion and scroll parallax retained with reduced-motion checks and visibility suspension. No motion-library dependency required.

## Not validated

No phone was connected, queried or changed for this work. No emulator/physical-device matrix, OEM parsing certification, independent dependency proof, real USB-loss recovery or live IDE activation matrix. This is an experimental action release, not the full stable/system-debloating vision. System-package actions, uninstall, data clearing, settings/permission writes and batching remain unsupported.

The package-manager state semantics follow AOSP; runtime role/admin query support is device-dependent and unknown output blocks changes. Simulated tests are not evidence of universal device safety. Concrete human approval remains an agent workflow requirement; a hash/flag cannot authenticate it.

