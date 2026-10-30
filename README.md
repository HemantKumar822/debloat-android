# Debloat Android

**Less guesswork. More control.**

A portable agent skill for understanding an Android device and reviewing optional app changes, with guided onboarding, conservative package research and private Markdown reports.

**v0.4 experimental actions.** Audit first, then optionally review, disable and restore one third-party app. No root, uninstall, data clearing or settings writes. System apps are blocked. Physical-device and live IDE validation remain release gates.

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

The audit adapter remains read-only. A separate experimental change executor supports plan/apply/restore with explicit per-plan approval, fresh preflight, expiry, a durable recovery receipt and result verification. It only supports one reviewed third-party app on owner user 0. It is not a sandbox around an unrestricted agent. Read the [complete action workflow](references/changes.md) before opting in; no physical-device validation has been performed.

Package-name clues are low-confidence research leads, not evidence of spying, malware or safe removal. Malformed and inconsistent inventories stop the audit. Optional missing observations stay visible. Backup status is always **not verified**; an inventory is not a backup.

The local code makes no network requests. Installed-app names can reveal personal information, and your AI provider may process anything the agent reads. Keep reports private. Reports use exclusive file creation, with owner-only permissions on POSIX and destination-folder ACLs on Windows. Revoke or turn off USB debugging when finished.

## Develop

```bash
python -m unittest discover -s tests -v
python scripts/package_skill.py --output debloat-android-skill.zip
python -m http.server 4173 --bind 127.0.0.1 --directory website/dist
```

- `SKILL.md`: guided agent behavior and boundaries.
- `android_care/`: read-only auditing, experimental guarded changes, Markdown rendering and packaging.
- `references/`: onboarding, evidence limits and roadmap.
- `website/dist/`: dependency-free landing page with native CSS/Web Animations.
- `tests/`: fake-device, consent, output, installer and packaging regressions.

See [validation](docs/validation-v0.3.md) and [the implementation brief](docs/next-release-plan.md). Experimental third-party app changes now exist; stable release and system-package support remain gated on device validation.

## License

MIT. No third-party package database is redistributed.

[Private website preview](https://droidwell.boldvine257.chatgpt.site) · [GitHub repository](https://github.com/HemantKumar822/debloat-android)


Fresh computer (Git, Python and access to this private repository required):

```bash
git clone https://github.com/HemantKumar822/debloat-android.git debloat-android
python debloat-android/scripts/install_skill.py --agent codex --user
```

On macOS/Linux use `python3` if that is your Python command. Choose another supported agent as needed. Do not reuse an existing clone destination; run the installer from your existing checkout instead. The portable ZIP also includes `scripts/install_skill.py`; run it from the extracted skill folder.
