# Debloat Android

**Less guesswork. More control.**

A portable agent skill for understanding an Android device, with guided onboarding, conservative package research and private Markdown reports.

**v0.3 read-only preview.** Device-changing operations are absent. No root, automatic cleanup or promised performance gains. Real-phone and live IDE validation remain release gates.

## Try it

Requires Python 3.10+. No pip dependencies.

```bash
python scripts/android_care.py guide
python scripts/android_care.py demo --output demo-android-audit.md
```

The demo is fictional. Open the resulting file in any Markdown viewer or text editor. See the [synthetic example](examples/demo-android-audit.md).

## Install in your agent

From this repository, choose a local project and agent:

```bash
python scripts/install_skill.py --agent codex --project /path/to/project --dry-run
python scripts/install_skill.py --agent codex --project /path/to/project
```

Use `cursor`, `claude`, or `antigravity` instead of `codex`; use `--user` instead of `--project PATH` for personal installation. Existing installations are never overwritten. Only the skill, runtime and references are copied; private reports are excluded.

| Agent | Project installation | Personal installation |
| --- | --- | --- |
| Codex | `.agents/skills/android-device-care` | `~/.agents/skills/android-device-care` |
| Cursor | `.cursor/skills/android-device-care` | `~/.cursor/skills/android-device-care` |
| Claude Code | `.claude/skills/android-device-care` | `~/.claude/skills/android-device-care` |
| Antigravity IDE | `.agents/skills/android-device-care` | `~/.gemini/config/skills/android-device-care` |

These paths were checked against official documentation; live activation in all four hosts is not yet validated. See [compatibility sources](docs/next-release-plan.md#compatibility-sources-checked). The agent needs local terminal access to the computer attached to the phone. Cloud skill discovery alone does not provide USB access.

Alternatively, extract [the portable ZIP](website/dist/debloat-android-skill.zip) and place its `android-device-care` directory in the corresponding skills directory. Ask your agent to use android-device-care. Run commands from the installed skill directory or use an absolute path to its entrypoint.

## Inspect a phone

Install Google's official [Android Platform Tools](https://developer.android.com/tools/releases/platform-tools). Follow the [onboarding guide](references/onboarding.md) to enable USB debugging and authorize a trusted computer.

```bash
python scripts/android_care.py doctor
python scripts/android_care.py audit --consent --output android-audit-report.md
```

`doctor` checks connection readiness without reading installed apps. Only pass `--consent` after agreeing to the inventory read. Development and demo requests do not authorize a phone scan. For multiple phones, select explicitly with `--serial DEVICE_ID`. Optional `--save-json` saves a private machine-readable copy.

## Safety and evidence

A fixed allowlist is checked at the ADB subprocess boundary, with no shell execution or mutation override. No disable, uninstall, settings-write or apply mode exists. This constrains the supplied adapter; it cannot sandbox an unrestricted agent or modified code.

Package-name clues are low-confidence research leads, not evidence of spying, malware or safe removal. Malformed and inconsistent inventories stop the audit. Optional missing observations stay visible. Backup status is always **not verified**; an inventory is not a backup.

The local code makes no network requests. Installed-app names can reveal personal information, and your AI provider may process anything the agent reads. Keep reports private. Reports use exclusive file creation, with owner-only permissions on POSIX and destination-folder ACLs on Windows. Revoke or turn off USB debugging when finished.

## Develop

```bash
python -m unittest discover -s tests -v
python scripts/package_skill.py --output debloat-android-skill.zip
python -m http.server 4173 --bind 127.0.0.1 --directory website/dist
```

- `SKILL.md`: guided agent behavior and boundaries.
- `android_care/`: read-only ADB, analysis, Markdown rendering and packaging.
- `references/`: onboarding, evidence limits and roadmap.
- `website/dist/`: dependency-free landing page with native CSS/Web Animations.
- `tests/`: fake-device, consent, output, installer and packaging regressions.

See [validation](docs/validation-v0.3.md) and [the implementation brief](docs/next-release-plan.md). Changes to device state remain disabled until separately implemented, reviewed and validated.

## License

MIT. No third-party package database is redistributed.

[Private website preview](https://droidwell.boldvine257.chatgpt.site) · [GitHub repository](https://github.com/HemantKumar822/debloat-android)

