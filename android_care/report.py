"""Render a standalone UTF-8 Markdown audit, with untrusted fields as text."""
from __future__ import annotations

from html import escape
import re


def text(value: object) -> str:
    """Keep metadata inside its paragraph/table cell, never executable markup."""
    value = " ".join(str(value).split())
    value = "".join(c for c in value if c.isprintable())
    value = escape(value, quote=False)
    return re.sub(r"([\\`*_{}\[\]#!|])", r"\\\1", value)


def table(headers, rows) -> list[str]:
    return ["| " + " | ".join(text(v) for v in headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |",
            *("| " + " | ".join(text(v) for v in row) + " |" for row in rows), ""]


def render(report: dict) -> str:
    stats = report["summary"]
    phone = report["device"]
    packages = report["packages"]
    demo = report["mode"].startswith("DEMO")
    lines = ["# Debloat Android — Android audit", "", "v0.3 read-only preview", "",
             f"Generated: {text(report['generated_at'])}", "",
             f"Mode: {text(report['mode'])}", "",
             "No changes performed. This report is an inventory, not a security verdict.", "",
             "## Summary", ""]
    lines += table(["Measure", "Packages"], [
        ("Installed", stats["total"]), ("System", stats["system"]),
        ("Third-party", stats.get("third_party", "Unknown")),
        ("Research candidates", stats["review"]), ("Protected-pattern matches", stats["protected"]),
        ("Already disabled", stats["disabled"])])
    lines += ["## Device snapshot", "", "Basic properties reported by Android. No serial number is saved.", ""]
    lines += table(["Property", "Value"], [
        (label, phone.get(key, "Unknown")) for label, key in [
            ("Manufacturer", "manufacturer"), ("Model", "model"), ("Android", "android"),
            ("SDK", "sdk"), ("Security patch", "security_patch")]])
    battery = report["battery"].get("level")
    lines += [f"Battery: {text(str(battery) + '%' if battery is not None else 'Not available')} at inspection; not a battery-health measurement.", "",
              "## Package research", "",
              "Name signals are weak clues, not proof of tracking or safe removal. Protected-pattern matches are advisory and incomplete; other packages may also be essential.", ""]
    candidates = [p for p in packages if p["group"] == "review"]
    if candidates:
        lines += table(["Candidate", "Confidence", "Reason", "Next step"], [
            (p["package"], p["confidence"], p["reason"], p["next"]) for p in candidates])
    else:
        lines += ["No name-based research candidates found. This does not establish safety.", ""]
    lines += ["## Full inventory", "", "State reflects the package listing at inspection time.", ""]
    lines += table(["Package", "Type", "State", "Finding", "Confidence", "Reason", "Next step"], [
        (p["package"], p["kind"], "Enabled" if p["enabled"] else "Disabled",
         {"review": "Research first", "protected": "Protected", "already-disabled": "Already disabled"}.get(p["group"], "Unclassified"),
         p["confidence"], p["reason"], p["next"]) for p in packages])
    lines += ["## Evidence coverage", "",
              "Synthetic example: no device queries were performed." if demo else
              "Observed means a query returned data; it does not verify an app's behavior. Empty filtered lists can be valid. Unavailable fields remain unknown.", ""]
    evidence = report.get("evidence", [])
    if evidence:
        lines += table(["Read-only query", "Result"], [(e["query"], e["status"]) for e in evidence])
    else:
        lines += ["No query evidence recorded.", ""]
    lines += ["## Backup status", "", "Unknown — Not verified. Not a backup.", "",
              "This inventory cannot confirm that photos, messages, accounts or app data can be restored. It provides no recovery guarantee or permission for changes.", "",
              "## Limitations", ""]
    lines += [f"- {text(item)}" for item in report["limitations"]]
    lines += ["", "## Notes", ""]
    lines += [f"- {text(item)}" for item in report.get("warnings", [])] or ["No additional warnings recorded."]
    lines += ["", "## Next steps", "",
              "1. Identify each candidate's publisher, exact role, OEM purpose and device-specific dependencies using reliable documentation.",
              "2. Discuss possible benefits, risks and alternatives. Leave packages unchanged while evidence is incomplete.",
              "3. Verify a separate backup and recovery plan before considering any future, separately approved changes. This version cannot perform those changes.",
              "4. Turn off USB debugging or revoke this computer's debugging access when finished.", "",
              "Keep this offline Markdown report private. Installed-app lists can reveal personal interests; cloud agents may process details they read.", ""]
    return "\n".join(lines)
