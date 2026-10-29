# v0.3 validation

Validated locally on Windows, 2026-10-29, using Python 3.12.14.

- Python unit/integration suite covers ADB allowlisting, consent, malformed inventory handling, Markdown escaping, exclusive output, installer paths and portable packages.
- No live phone was scanned. No device-changing API exists.
- Local browser checks: desktop and 390px mobile hero, no horizontal overflow at mobile width, installation tab selection, keyboard ArrowRight selection, clipboard success feedback, native FAQ disclosure, documentation rendering; no browser console errors observed.
- Reduced-motion CSS and JavaScript guards reviewed in source; OS-level reduced-motion emulation was not performed.
- Installation paths were checked against official agent docs (linked in next-release-plan.md). Installed CLI execution is tested independently of current directory. Live skill activation in each IDE remains unverified.
- Initial tests hit sandbox temporary-folder permissions. Pointing TEMP/TMP to an ignored workspace test folder resolves this infrastructure issue.

## Release gates

Real-device audits across Android/OEM versions, real IDE discovery and permissions, and broader screen-reader checks remain outstanding. Package classifications are only name heuristics, with no dependency graph, tracker proof, permission analysis or backup verification. Any future change engine needs a separate design, emulator/device trials, failure and rollback tests, and independent review.

The v0.2 validation document is historical; its HTML-report browser checks do not describe the current Markdown renderer.

Final suite: 45 tests passed. Skill frontmatter validator passed; JavaScript syntax check passed. Independent review identified and fixed wildcard bundle inclusion and Python 3.10/3.11 reparse-point detection; both received regression coverage. Real Windows junction behavior under Python 3.10 remains untested.
