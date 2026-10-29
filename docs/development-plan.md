# Local prototype hardening — 2026-10-28

The user requested local setup and continued implementation, with device changes
disabled. Preserve the standard-library Python architecture and offline report.
GitHub publication and real-phone inspection are separate later steps.

1. Reproduce baseline tests; add regressions for Windows console output,
   command-boundary bypasses, ambiguous connection states, and consent.
2. Add `doctor` connection guidance without package reads. Require
   `audit --consent` before creating an ADB adapter.
3. Reject malformed/inconsistent inventories; preserve unknown enabled state
   when disabled-state evidence is missing; record command-level provenance.
4. Add report sections for evidence coverage, backup uncertainty, and next steps.
5. Update onboarding and repository guidance; generate a synthetic preview.
6. Run the complete suite, CLI smoke checks, and browser report checks.

Validation uses fake devices only. No real ADB operations are authorized by this
development task. No change engine, bypass switch, or executable rollback is added.
