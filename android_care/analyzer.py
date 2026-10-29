"""Evidence-conservative parsing and classification for a read-only audit."""
from __future__ import annotations

from datetime import datetime, timezone
import re

from android_care.adb import AuditError

PACKAGE_RE = re.compile(r"^package:([a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z0-9_]+)*)$")

# Protection is advisory in this read-only version; never treat it as an exhaustive list.
PROTECTED_PREFIXES = (
    "android", "com.android.", "com.google.android.gms",
    "com.google.android.gsf", "com.google.android.permissioncontroller",
    "com.google.android.modulemetadata", "com.google.android.networkstack",
)
# These signals identify candidates for *research*, never proof of tracking or bloat.
REVIEW_TOKENS = (
    "advert", "analytics", "telemetry", "promotion", "promotions",
    "hotapps", "hotgames", "appmarket", "recommendation", "recommendations",
    "gamecenter", "userexperience", "adservice", "adservices", "pushads",
)


def parse_packages(raw: str) -> set[str]:
    names = set()
    for line in raw.splitlines():
        match = PACKAGE_RE.fullmatch(line.strip())
        if match:
            names.add(match.group(1))
    return names


def parse_battery(raw: str) -> dict:
    values = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()
    level = values.get("level", "")
    try:
        level_value = int(level)
        if not 0 <= level_value <= 100:
            level_value = None
    except ValueError:
        level_value = None
    return {"level": level_value, "status": values.get("status", "Unknown")}


def classify(name: str, system: bool, disabled: bool) -> dict:
    if any(name == prefix.rstrip(".") or name.startswith(prefix.rstrip(".") + ".")
           for prefix in PROTECTED_PREFIXES):
        return {
            "group": "protected", "reason": "Core Android/Google infrastructure naming pattern; do not modify without verified device-specific evidence.",
            "confidence": "name-based", "next": "Leave unchanged.",
        }
    if disabled:
        return {
            "group": "already-disabled", "reason": "ADB reports that this package is already disabled.",
            "confidence": "observed state", "next": "Do not assume it was disabled by this tool. Investigate only if something is broken.",
        }
    if any(token in name.lower() for token in REVIEW_TOKENS):
        return {
            "group": "review", "reason": "Package name suggests promotional, analytics, or recommendation functionality. This is not proof of tracking or safe removal.",
            "confidence": "low — name only", "next": "Identify its exact role, publisher, dependencies and importance to this device before considering changes.",
        }
    return {
        "group": "not-classified", "reason": "No reliable conclusion from package name and installation category alone.",
        "confidence": "insufficient evidence", "next": "Leave unchanged unless there is a specific problem to investigate.",
    }


def make_audit(device: dict, all_pkgs: set[str], system: set[str], third_party: set[str],
               disabled: set[str], battery: dict, warnings: list[str], demo: bool = False,
               evidence: list[dict] | None = None) -> dict:
    entries = []
    for name in sorted(all_pkgs):
        classification = classify(name, name in system, name in disabled)
        entries.append({
            "package": name, "kind": "System" if name in system else "Third-party" if name in third_party else "Unresolved",
            "enabled": name not in disabled, **classification,
        })
    counts = {key: sum(p["group"] == key for p in entries)
              for key in ("protected", "already-disabled", "review", "not-classified")}
    return {
        "schema_version": "0.2", "mode": "DEMO — SYNTHETIC DATA" if demo else "READ-ONLY AUDIT",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "device": device, "battery": battery,
        "summary": {"total": len(entries), "system": len(all_pkgs & system),
                    "third_party": len(all_pkgs & third_party), "disabled": len(all_pkgs & disabled),
                    "review": counts["review"], "protected": counts["protected"]},
        "packages": entries, "warnings": warnings,
        "backup_status": "Not verified",
        "evidence": evidence or [],
        "limitations": [
            "Names and package states do not establish malicious behavior, dependencies, or safe-to-disable status.",
            "This audit does not inspect network traffic, app code, permissions, or per-user package variations.",
            "A single battery snapshot is not a battery-health or performance benchmark.",
            "Backup status is not verified. An inventory report is not a personal-data backup or recovery guarantee.",
            "No phone configuration was changed. No app was uninstalled or disabled.",
        ],
    }


def collect(adb, serial: str) -> dict:
    props = {
        "manufacturer": "ro.product.manufacturer",
        "model": "ro.product.model",
        "android": "ro.build.version.release",
        "sdk": "ro.build.version.sdk",
        "security_patch": "ro.build.version.security_patch",
    }
    device = {}
    warnings = []
    evidence = []

    def observe(command: tuple[str, ...]) -> str:
        record = {"query": " ".join(command), "status": "unavailable"}
        evidence.append(record)
        result = adb.read(serial, *command)
        record["status"] = "observed" if result.strip() else "empty"
        return result

    def inventory(*flags: str) -> set[str]:
        raw = observe(("shell", "pm", "list", "packages", *flags))
        if any(line.strip() and not PACKAGE_RE.fullmatch(line.strip()) for line in raw.splitlines()):
            raise ValueError("Invalid package listing received. Audit stopped rather than trusting partial data.")
        # Empty filtered categories are valid (especially disabled packages).
        return parse_packages(raw)

    for label, prop in props.items():
        try:
            device[label] = observe(("shell", "getprop", prop)).strip() or "Not reported"
        except AuditError:
            device[label] = "Not available"
            warnings.append(f"Device field '{label}' could not be read.")
    all_pkgs = inventory()
    if not all_pkgs:
        raise ValueError("The phone returned no package list. Audit aborted rather than showing misleading results.")
    sets = {}
    for label, flag in (("system", "-s"), ("third", "-3"), ("disabled", "-d")):
        try:
            sets[label] = inventory(flag)
        except AuditError as exc:
            raise ValueError(f"Could not read the {label} package category. The audit stopped to avoid an incomplete report.") from exc
    if (not (sets["system"] | sets["third"] | sets["disabled"]) <= all_pkgs
            or sets["system"] & sets["third"]):
        raise ValueError("Package categories are inconsistent. Unlock the phone and retry the audit.")
    unresolved = all_pkgs - sets["system"] - sets["third"]
    if unresolved:
        warnings.append(f"{len(unresolved)} packages have an unresolved installation category; leave unchanged.")
    try:
        battery = parse_battery(observe(("shell", "dumpsys", "battery")))
        if battery["level"] is None:
            warnings.append("Battery level was not reported as a valid percentage.")
    except AuditError:
        battery = {"level": None, "status": "Unknown"}
        warnings.append("Battery status was unavailable.")
    warnings.append("ADB package listings may not cover every secondary user or work profile.")
    return make_audit(device, all_pkgs, sets["system"], sets["third"], sets["disabled"], battery, warnings,
                      evidence=evidence)


def demo_audit() -> dict:
    names = {
        "android", "com.android.systemui", "com.android.settings", "com.android.phone",
        "com.android.providers.settings", "com.android.providers.downloads", "com.android.bluetooth",
        "com.google.android.gms", "com.google.android.gsf", "com.google.android.permissioncontroller",
        "com.google.android.apps.maps", "com.google.android.apps.photos", "com.google.android.youtube",
        "com.vendor.promotions", "com.vendor.analytics", "com.vendor.appmarket", "com.vendor.weather",
        "com.vendor.launcher", "com.vendor.camera", "com.vendor.updater", "com.vendor.notes",
        "com.example.reader", "com.example.music", "org.mozilla.firefox", "com.example.calendar",
        "com.example.education", "com.example.fitness", "com.example.podcast", "com.example.messenger",
        "com.vendor.oldwallpapers", "com.vendor.hotapps", "com.example.budget",
    }
    third = {p for p in names if p.startswith("com.example.") or p == "org.mozilla.firefox"}
    return make_audit(
        {"manufacturer": "Example Mobile", "model": "Aurora X (fictional)", "android": "15",
         "sdk": "35", "security_patch": "2026-09-05"}, names, names - third, third,
        {"com.vendor.oldwallpapers"}, {"level": 76, "status": "2"},
        ["Demo data is fictional. Do not use these package names as a debloat list."], demo=True,
    )
