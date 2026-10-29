# Development roadmap — planned, not implemented

## Current: v0.3 — guided and read-only

- Cross-platform Python CLI; fixed read-only ADB allowlist.
- USB authorization support and safe multi-device handling.
- Basic model/OS/security patch/battery snapshot and package state inventory.
- Cautious keyword-based research prompts; no claimed tracker detection.
- Responsive, offline Markdown report with local filtering and print-to-PDF.
- Synthetic demo and unit tests.
- Connection-only `doctor`, inventory consent gate, strict query parsing.
- Process-boundary command validation, evidence coverage and backup uncertainty.
- Browser regression checks for filtering, mobile layout and full inventory printing.

## Next: evidence and interpretation (not implemented)

- Strictly versioned OEM package intelligence from independently reviewed sources; source/provenance tracking, licensing review, expiry dates.
- Per-package research dossier with category, evidence, dependencies, false positives, confidence and citations.
- More granular local-only permissions and background-process audit; explicit user consent for any expanded data collection.
- Privacy-first redaction controls and optional export of minimal de-identified aggregate findings.
- Compare audit baselines without performance claims unless evidence permits.

## Proposed: v0.3 — opt-in changes (high-risk; separate security review)

- Implement a new isolated change executor with narrow typed operations, not raw ADB strings.
- Complete and verified safety allowlist + permanent blocklist, vendor/build rules.
- Precondition verification, full personal backup checklist, targeted confirmation by package, dry-run plan, tamper-evident change journal, idempotent replay, and rollback.
- Default to lower-risk alternatives when available, with explicit side effects.
- Block changes to core security and communication roles; reject incomplete evidence.
- Test across multiple emulators/Android API levels and a diverse real-device matrix. Test failure-to-connect and recovery scenarios.

## Proposed: v1.0 — integration

- Validate skill trigger behavior on Codex, Claude Code, Gemini CLI and compatible local agents.
- Package `SKILL.md` for GitHub skill installers; independent security audit.
- Add interactive explainable risk views and optionally an on-device companion, only if users need them.

**Release gates:** No direct mutation paths are merged into this read-only preview. No marketing claim of "privacy-safe", "faster" or "universal" without measurable support. Don't copy copyleft package databases into an MIT repo without a licensing strategy.

