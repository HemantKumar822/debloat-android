# Debloat Android — Android audit

v0.3 read-only preview

Generated: 2026-10-29 09:44 UTC

Mode: DEMO — SYNTHETIC DATA

No changes performed. This report is an inventory, not a security verdict.

## Summary

| Measure | Packages |
| --- | --- |
| Installed | 32 |
| System | 23 |
| Third-party | 9 |
| Research candidates | 4 |
| Protected-pattern matches | 10 |
| Already disabled | 1 |

## Device snapshot

Basic properties reported by Android. No serial number is saved.

| Property | Value |
| --- | --- |
| Manufacturer | Example Mobile |
| Model | Aurora X (fictional) |
| Android | 15 |
| SDK | 35 |
| Security patch | 2026-09-05 |

Battery: 76% at inspection; not a battery-health measurement.

## Package research

Name signals are weak clues, not proof of tracking or safe removal. Protected-pattern matches are advisory and incomplete; other packages may also be essential.

| Candidate | Confidence | Reason | Next step |
| --- | --- | --- | --- |
| com.vendor.analytics | low — name only | Package name suggests promotional, analytics, or recommendation functionality. This is not proof of tracking or safe removal. | Identify its exact role, publisher, dependencies and importance to this device before considering changes. |
| com.vendor.appmarket | low — name only | Package name suggests promotional, analytics, or recommendation functionality. This is not proof of tracking or safe removal. | Identify its exact role, publisher, dependencies and importance to this device before considering changes. |
| com.vendor.hotapps | low — name only | Package name suggests promotional, analytics, or recommendation functionality. This is not proof of tracking or safe removal. | Identify its exact role, publisher, dependencies and importance to this device before considering changes. |
| com.vendor.promotions | low — name only | Package name suggests promotional, analytics, or recommendation functionality. This is not proof of tracking or safe removal. | Identify its exact role, publisher, dependencies and importance to this device before considering changes. |

## Full inventory

State reflects the package listing at inspection time.

| Package | Type | State | Finding | Confidence | Reason | Next step |
| --- | --- | --- | --- | --- | --- | --- |
| android | System | Enabled | Protected | name-based | Core Android/Google infrastructure naming pattern; do not modify without verified device-specific evidence. | Leave unchanged. |
| com.android.bluetooth | System | Enabled | Protected | name-based | Core Android/Google infrastructure naming pattern; do not modify without verified device-specific evidence. | Leave unchanged. |
| com.android.phone | System | Enabled | Protected | name-based | Core Android/Google infrastructure naming pattern; do not modify without verified device-specific evidence. | Leave unchanged. |
| com.android.providers.downloads | System | Enabled | Protected | name-based | Core Android/Google infrastructure naming pattern; do not modify without verified device-specific evidence. | Leave unchanged. |
| com.android.providers.settings | System | Enabled | Protected | name-based | Core Android/Google infrastructure naming pattern; do not modify without verified device-specific evidence. | Leave unchanged. |
| com.android.settings | System | Enabled | Protected | name-based | Core Android/Google infrastructure naming pattern; do not modify without verified device-specific evidence. | Leave unchanged. |
| com.android.systemui | System | Enabled | Protected | name-based | Core Android/Google infrastructure naming pattern; do not modify without verified device-specific evidence. | Leave unchanged. |
| com.example.budget | Third-party | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.example.calendar | Third-party | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.example.education | Third-party | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.example.fitness | Third-party | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.example.messenger | Third-party | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.example.music | Third-party | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.example.podcast | Third-party | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.example.reader | Third-party | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.google.android.apps.maps | System | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.google.android.apps.photos | System | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.google.android.gms | System | Enabled | Protected | name-based | Core Android/Google infrastructure naming pattern; do not modify without verified device-specific evidence. | Leave unchanged. |
| com.google.android.gsf | System | Enabled | Protected | name-based | Core Android/Google infrastructure naming pattern; do not modify without verified device-specific evidence. | Leave unchanged. |
| com.google.android.permissioncontroller | System | Enabled | Protected | name-based | Core Android/Google infrastructure naming pattern; do not modify without verified device-specific evidence. | Leave unchanged. |
| com.google.android.youtube | System | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.vendor.analytics | System | Enabled | Research first | low — name only | Package name suggests promotional, analytics, or recommendation functionality. This is not proof of tracking or safe removal. | Identify its exact role, publisher, dependencies and importance to this device before considering changes. |
| com.vendor.appmarket | System | Enabled | Research first | low — name only | Package name suggests promotional, analytics, or recommendation functionality. This is not proof of tracking or safe removal. | Identify its exact role, publisher, dependencies and importance to this device before considering changes. |
| com.vendor.camera | System | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.vendor.hotapps | System | Enabled | Research first | low — name only | Package name suggests promotional, analytics, or recommendation functionality. This is not proof of tracking or safe removal. | Identify its exact role, publisher, dependencies and importance to this device before considering changes. |
| com.vendor.launcher | System | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.vendor.notes | System | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.vendor.oldwallpapers | System | Disabled | Already disabled | observed state | ADB reports that this package is already disabled. | Do not assume it was disabled by this tool. Investigate only if something is broken. |
| com.vendor.promotions | System | Enabled | Research first | low — name only | Package name suggests promotional, analytics, or recommendation functionality. This is not proof of tracking or safe removal. | Identify its exact role, publisher, dependencies and importance to this device before considering changes. |
| com.vendor.updater | System | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| com.vendor.weather | System | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |
| org.mozilla.firefox | Third-party | Enabled | Unclassified | insufficient evidence | No reliable conclusion from package name and installation category alone. | Leave unchanged unless there is a specific problem to investigate. |

## Evidence coverage

Synthetic example: no device queries were performed.

No query evidence recorded.

## Backup status

Unknown — Not verified. Not a backup.

This inventory cannot confirm that photos, messages, accounts or app data can be restored. It provides no recovery guarantee or permission for changes.

## Limitations

- Names and package states do not establish malicious behavior, dependencies, or safe-to-disable status.
- This audit does not inspect network traffic, app code, permissions, or per-user package variations.
- A single battery snapshot is not a battery-health or performance benchmark.
- Backup status is not verified. An inventory report is not a personal-data backup or recovery guarantee.
- No phone configuration was changed. No app was uninstalled or disabled.

## Notes

- Demo data is fictional. Do not use these package names as a debloat list.

## Next steps

1. Identify each candidate's publisher, exact role, OEM purpose and device-specific dependencies using reliable documentation.
2. Discuss possible benefits, risks and alternatives. Leave packages unchanged while evidence is incomplete.
3. Verify a separate backup and recovery plan before considering any future, separately approved changes. This version cannot perform those changes.
4. Turn off USB debugging or revoke this computer's debugging access when finished.

Keep this offline Markdown report private. Installed-app lists can reveal personal interests; cloud agents may process details they read.
