# Experimental change workflow — v0.4

## Scope and limitations

One reviewed third-party app on active owner user 0, with no other users/profiles. System/core apps, active Android roles, keyboard, managed/admin devices, shared UIDs and sensitive bound services are blocked. Unknown output fails closed. Disabling stops an app and its background activity/notifications; it does not uninstall or clear data.

Tests use simulated ADB output. No physical-device/OEM/API matrix is validated. This is not a universal automatic cleaner. Review personal-data backup and recovery access; the CLI cannot verify either. Restoration cannot undo missed messages or guarantee ADB access.

## Plan

Audit and research the exact app first. Establish role, dependencies, source and expected impact. Obtain consent for expanded package, build, user, device-policy, role and keyboard checks. Raw dumps are not saved; a serial/build hash and app version/state are saved with reviewer evidence.

Templates below require actual values and are not permission to act on any example package:

~~~bash
python scripts/android_care.py plan --experimental --consent --serial DEVICE_ID --package com.example.optionalapp --reason "USER-REVIEWED REASON" --evidence "REPLACE WITH ROLE, DEPENDENCIES, SOURCES AND EXPECTED IMPACT" --output reports/change-plan.json
~~~

Read reports/change-plan.md. Obtain user approval of the exact plan and its full SHA-256. Plans expire in 15 minutes. Device/build/version/state drift requires a new plan. Evidence text is required but its truth is not automatically verified.

## Apply

Only after the user reviews and approves the plan, accepts the experimental limitation and acknowledges backup/recovery limits:

~~~bash
python scripts/android_care.py apply --experimental --backup-acknowledged --serial DEVICE_ID --plan reports/change-plan.json --approve FULL_PLAN_SHA256 --receipt reports/recovery.json
~~~

Flags assert caller approval; they cannot prove human consent. The skill must not self-approve. Preflight repeats, then an exclusive/fsynced receipt is written BEFORE any change. Existing receipt files are never overwritten. The command disables one app for user 0 and verifies the result.

Keep the receipt even on failure. Its immutable status "prepared" means the command MAY have happened. Successful terminal output says verified-disabled. Check navigation, calls, messaging, keyboard, connectivity, notifications and usual apps before considering another change. Stop on unexpected behavior.

## Restore

Read the receipt, explain the restoration, obtain approval, and compute its canonical digest:

~~~bash
python -c "import json; from pathlib import Path; from android_care.changes import digest; print(digest(json.loads(Path('reports/recovery.json').read_text(encoding='utf-8'))))"
python scripts/android_care.py restore --experimental --backup-acknowledged --serial DEVICE_ID --recovery reports/recovery.json --approve FULL_RECEIPT_SHA256 --receipt reports/restore-receipt.json
~~~

Restore checks device/build/version and disabled-user state. Original default state uses default-state; original enabled state uses enable. Already-restored state is a no-op. Different versions or states block restoration rather than guessing. Use a new restore-receipt path for a retry after inspecting previous results. Do not invent receipts or reconstruct from memory.

If USB is lost, reconnect/unlock and inspect before retrying. No automatic retries or batch/rollback loops. The tool cannot recover broken boot, guarantee USB access or restore personal data. Receipts are private recovery records, not backups.

## Technical basis

Android distinguishes default, enabled and disabled-user states in its [package-manager source](https://android.googlesource.com/platform/frameworks/base/+/73b787b38a0b25c7cfa3fec69e1cbddbd1b1a0b8/services/core/java/com/android/server/pm/PackageManagerShellCommand.java). The separate executor only accepts fixed reads and three package operations. It is not a sandbox against modified code or an unrestricted agent.
