# Validation record — local v0.2 preview

Date: 2026-10-28. Development host: Windows, Python 3.12.14.

## Completed

- Restored the 18-file v0.1 archive into the user's chosen project root.
- Baseline: 12 of 13 unit tests passed. Demo generation failed when writing a
  checkmark to a Windows console. Removed nonessential Unicode from CLI output.
- Added regressions before the safety/onboarding/analysis changes. The failures
  reproduced missing consent enforcement, unrestricted internal process calls,
  malformed/inconsistent inventory acceptance, overbroad core-name matching,
  absent evidence metadata, and the Windows console failure.
- All 31 standard-library unit/integration tests pass. Fake-device CLI integration
  covers HTML and optional JSON export, with identifiers excluded.
- Browser checks pass using Playwright and installed Microsoft Edge: 32 synthetic
  rows, research filtering, combined search, empty state, full inventory in print
  mode, no document overflow at 1440px and 390px, no page errors, no HTTP requests.
- Visually inspected the generated full-page synthetic screenshot.
- Fixed the original print stylesheet hiding the entire inventory. Regression
  check failed with 0 printed rows before the fix and passed with all 32 afterward.
- Skill scenario check found that old instructions omitted the required consent
  flag. Updated instructions passed rechecks for authorized inventory, development
  without device consent, demands to disable packages, malformed data, and claims
  about backups/tracking. These are focused checks, not cross-agent certification.
- Skill Creator's structural validator passes. Its bundled schema rejected the
  prototype's top-level compatibility field; preserved that text under metadata.
  PyYAML is installed only in ignored `.tools/validation` for this development
  check, and is not a runtime requirement.
- Expanded CI configuration to Windows, Linux and macOS with Python 3.10/3.13.
  Those remote CI jobs have not run locally or on GitHub.
- Independent code review found another legacy-console case: non-ASCII output
  paths caused successful saves to be reported as failures. Extended the
  cp1252 regression to a Unicode filename, observed failure, and added safe
  console encoding. Report files retain their original Unicode paths and UTF-8
  contents; only unprintable console characters are escaped.

## Not validated / release gates

- No real phone or emulator was inspected. ADB was not available on PATH during
  this session. Platform Tools must be installed separately for real audits.
- OEM output differences, work profiles, secondary users, transport changes and
  concurrent package changes need device-matrix testing. A consistent parsed
  snapshot does not prove complete inventory coverage.
- Package classification still uses names only. No third-party package database,
  permissions analysis, tracker detection, dependency resolution or performance
  profiling has been integrated.
- Backup verification and device-changing operations are absent. No audit report
  constitutes a backup or guaranteed rollback.
- GitHub repository creation, publication, branch protection, remote CI execution,
  release packaging and broad agent compatibility are future work.

## Reproduce

```bash
python -m unittest discover -s tests -v
python -m compileall -q android_care scripts tests
python scripts/android_care.py guide
python scripts/android_care.py demo --output reports/demo.html
node tests/report-browser.cjs
```

The last command requires optional Playwright development dependencies; see the
README. Do not run a real-device audit as a substitute for these tests.
