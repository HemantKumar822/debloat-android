"""Friendly command-line entry point for the Android Device Care agent skill."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from android_care.adb import ADB, AuditError
from android_care.analyzer import collect, demo_audit
from android_care.report import render


GUIDE = """
DEBLOAT ANDROID | Guided setup | v0.4 EXPERIMENTAL CHANGES

Hello! Start with an audit. Audits never change your phone.
Optional app disabling requires a separate reviewed plan and explicit approval.
Only inspect a phone you own or have permission to inspect.

1. Install Android SDK Platform Tools (ADB) on your trusted computer.
   Official download: https://developer.android.com/tools/releases/platform-tools
2. On your phone, open Settings > About phone > Build number.
   Tap Build number seven times (manufacturer menus may differ).
3. In Developer options, enable USB debugging.
4. Connect your phone with a data-capable USB cable.
   Unlock it and approve the RSA prompt only for a computer you trust.
5. Check the connection without reading installed apps:
      python scripts/android_care.py doctor
6. If you agree to read installed package names and basic device information:
      python scripts/android_care.py audit --consent

Use --serial ID if several phones are connected. Use devices to see their IDs.
Reports stay local, but cloud AI agents may process details they read.
Keep reports private. This inventory is NOT a backup; backup status is unknown.
No phone yet? Try: python scripts/android_care.py demo
After finishing, turn off USB debugging or revoke debugging access.
"""


def _say(message: str, *, file=None) -> None:
    """Keep a saved result successful even on legacy Windows console encodings."""
    stream = file if file is not None else sys.stdout
    encoding = getattr(stream, "encoding", None) or "utf-8"
    printable = message.encode(encoding, errors="backslashreplace").decode(encoding)
    print(printable, file=stream)


def _save_private(path: Path, content: str) -> None:
    # Exclusive creation prevents accidental overwrites and symlink-following.
    # Private mode protects installed-app lists from other local users on POSIX.
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
    except Exception:
        path.unlink(missing_ok=True)
        raise


def save_report(audit: dict, out: str, save_json: bool) -> Path:
    target = Path(out).expanduser().absolute()
    if target.suffix.lower() not in (".md", ".markdown"):
        raise ValueError("Choose an .md or .markdown output path for the report.")
    companion = target.with_suffix(".json")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or (save_json and companion.exists()):
        raise FileExistsError("A report with that name already exists. Choose a new --output path; existing files are never overwritten.")
    _save_private(target, render(audit))
    if save_json:
        try:
            _save_private(companion, json.dumps(audit, indent=2, ensure_ascii=False))
        except Exception:
            target.unlink(missing_ok=True)
            raise
    return target


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Guided Android care: audit, review, optional experimental disable and restore.")
    commands = parser.add_subparsers(dest="action")
    commands.add_parser("guide", help="Friendly USB debugging setup and privacy guidance")
    commands.add_parser("devices", help="List available ADB devices")
    doctor = commands.add_parser("doctor", help="Check connection and guide setup without reading app inventory")
    doctor.add_argument("--serial", help="Select a phone when several are connected")
    audit = commands.add_parser("audit", help="Read device state and produce offline report")
    audit.add_argument("--serial", help="Device ID, required when multiple phones are connected")
    audit.add_argument("--output", default="android-audit-report.md", help="Markdown report path")
    audit.add_argument("--save-json", action="store_true", help="Also save package data as private JSON")
    audit.add_argument("--consent", action="store_true", help="Confirm permission to read installed package names and device information")
    demo = commands.add_parser("demo", help="Generate a synthetic example report (no phone needed)")
    demo.add_argument("--output", default="demo-android-audit.md", help="Markdown report path")
    for action in ('plan', 'apply', 'restore'):
        change = commands.add_parser(action, help=f"Experimental single-app {action}; see references/changes.md")
        change.add_argument('--serial', required=True, help='Explicit selected device identifier')
        change.add_argument('--experimental', action='store_true', help='Acknowledge lack of physical-device validation')
        if action == 'plan':
            change.add_argument('--consent', action='store_true', help='Allow package, role, keyboard and device-policy checks')
            change.add_argument('--package', required=True)
            change.add_argument('--reason', required=True)
            change.add_argument('--evidence', required=True, help='Reviewed role, dependencies, source and expected impact')
            change.add_argument('--output', required=True, help='New private JSON plan; Markdown review saved alongside')
        else:
            change.add_argument('--plan' if action == 'apply' else '--recovery', required=True)
            change.add_argument('--approve', required=True, help='Full SHA-256 of the document explicitly approved by the user')
            change.add_argument('--receipt', required=True, help='New recovery/restore journal path')
            change.add_argument('--backup-acknowledged', action='store_true', help='User reviewed backup/recovery limits; not proof of a backup')
    args = parser.parse_args(argv)

    if args.action in (None, "guide"):
        _say(GUIDE)
        return 0
    try:
        if args.action in ('plan', 'apply', 'restore'):
            from android_care import changes
            if not args.experimental:
                raise AuditError('Changes are experimental and not validated on physical phones. Review references/changes.md before opting in with --experimental.')
            if args.action == 'plan' and not args.consent:
                raise AuditError('Plan preflight reads package, role, keyboard and device-policy state; explicit --consent required.')
            if args.action != 'plan' and not args.backup_acknowledged:
                raise AuditError('Review backup/recovery limits with the user before --backup-acknowledged. This flag does not verify a backup.')
            adapter = changes.ChangeADB()
            if args.action == 'plan':
                plan = changes.create_plan(adapter, args.serial, args.package, args.reason, args.evidence)
                target = Path(args.output)
                if target.suffix.lower() != '.json': raise ValueError('Plan output must be a .json file.')
                review = target.with_suffix('.md')
                if review.exists(): raise FileExistsError('Markdown review already exists; choose another path.')
                changes.save_document(target, plan)
                # JSON encoding inside a fenced block prevents untrusted evidence from becoming Markdown directives.
                encoded = json.dumps(plan, indent=2, ensure_ascii=True).replace('`', '\\u0060')
                _save_private(review, '# Review one app change\n\nExperimental: no physical-device validation.\n\n'
                    + 'Read the reason, evidence and risk below. Approval applies only to this document.\n\n```json\n'
                    + encoded + '\n```\n\nApproval SHA-256: `' + changes.digest(plan) + '`\n')
                _say(f'Plan saved: {target}\nRead the review: {review}\nApproval SHA-256: {changes.digest(plan)}\nNo app changed. Ask the user to review this exact plan before applying.')
            else:
                source = Path(args.plan if args.action == 'apply' else args.recovery)
                if source.stat().st_size > 100_000: raise ValueError('Change document is unexpectedly large.')
                document = json.loads(source.read_text(encoding='utf-8'))
                operation = changes.apply_plan if args.action == 'apply' else changes.restore
                result = operation(adapter, args.serial, document, args.approve, Path(args.receipt))
                _say(json.dumps(result, indent=2))
                _say('Check app access, notifications, calls and other essential functions on the phone. Keep the recovery receipt private. Revoke USB debugging when finished.')
            return 0
        if args.action == "audit" and not args.consent:
            raise AuditError("Inventory permission is required. Package names can reveal personal interests. "
                             "Cloud agents may process details they read. If you agree, run audit --consent.")
        if args.action == "demo":
            path = save_report(demo_audit(), args.output, False)
            _say(f"Your sample report is ready: {path}\n  Open it in a Markdown viewer or text editor. It uses fictional demo data.")
            return 0
        adb = ADB()
        if args.action == "doctor":
            try:
                adb.pick(args.serial)
            except AuditError as exc:
                _say(f"Setup needs attention: {exc}\nRun guide for step-by-step setup. No package inventory was read.")
                return 2
            _say("Connection ready. No package inventory was read.\n"
                  "If you agree to inventory collection, run: python scripts/android_care.py audit --consent"
                  + (f" --serial {args.serial}" if args.serial else "")
                  + "\nAfter finishing, turn off USB debugging or revoke access.")
            return 0
        if args.action == "devices":
            devices = adb.devices()
            if not devices:
                _say("No phones detected. Start with: python scripts/android_care.py guide")
            else:
                for device in devices:
                    message = {"device": "Ready", "unauthorized": "Waiting for approval on phone", "offline": "Offline"}.get(device.state, device.state)
                    _say(f"{device.serial} - {message}")
            return 0
        if args.action == "audit":
            phone = adb.pick(args.serial)
            _say("Connected. Reading device information and installed packages...")
            report = collect(adb, phone.serial)
            path = save_report(report, args.output, args.save_json)
            _say(f"\nRead-only audit complete.\n  Report: {path}\n  Packages: {report['summary']['total']} | Research candidates: {report['summary']['review']}\n  No settings or apps were changed. Open the Markdown report in a text editor or Markdown viewer.\n  When finished, turn off USB debugging or revoke access.")
            return 0
    except (AuditError, ValueError, PermissionError, OSError) as exc:
        state = ('A change may have occurred if a command was submitted. Keep the receipt; inspect state before retrying.'
                 if args.action in ('apply', 'restore') else 'No device-changing command was requested.')
        _say(f"Couldn't finish safely: {exc}\n{state}", file=sys.stderr)
        return 2
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

