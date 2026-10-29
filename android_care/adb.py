"""Constrained, read-only ADB adapter. No arbitrary command execution.

This package has no device modification API. The process boundary validates
commands as well as the public read method. This is not a Python sandbox.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Callable


class AuditError(RuntimeError):
    pass


# All shell invocations must be exact members of this fixed allowlist.
READ_ONLY_COMMANDS = frozenset({
    ("shell", "getprop", "ro.product.manufacturer"),
    ("shell", "getprop", "ro.product.model"),
    ("shell", "getprop", "ro.build.version.release"),
    ("shell", "getprop", "ro.build.version.sdk"),
    ("shell", "getprop", "ro.build.version.security_patch"),
    ("shell", "pm", "list", "packages"),
    ("shell", "pm", "list", "packages", "-s"),
    ("shell", "pm", "list", "packages", "-3"),
    ("shell", "pm", "list", "packages", "-d"),
    ("shell", "dumpsys", "battery"),
})

SERIAL_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.:_-]{0,127}$")


@dataclass(frozen=True)
class Device:
    serial: str
    state: str
    label: str


def parse_devices(output: str) -> list[Device]:
    results = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("list of devices") or line.startswith("*"):
            continue
        chunks = line.split()
        if len(chunks) >= 2 and SERIAL_PATTERN.fullmatch(chunks[0]):
            results.append(Device(chunks[0], chunks[1], " ".join(chunks[2:])))
    return results


class ADB:
    def __init__(self, executable: str | None = None, runner: Callable | None = None):
        self.executable = executable or shutil.which("adb")
        if self.executable is None:
            raise AuditError("ADB was not found. Install Android SDK Platform Tools and add adb to PATH.")
        self.runner = runner or subprocess.run

    def _call(self, args: tuple[str, ...], timeout: int = 20) -> str:
        targeted_read = (
            len(args) >= 3 and args[0] == "-s"
            and SERIAL_PATTERN.fullmatch(args[1])
            and args[2:] in READ_ONLY_COMMANDS
        )
        if args != ("devices", "-l") and not targeted_read:
            raise AuditError("Blocked command: only discovery and predefined read-only ADB queries are permitted.")
        try:
            result = self.runner(
                [self.executable, *args], capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=timeout,
                check=False, shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise AuditError("ADB did not respond in time. Check the phone and cable.") from exc
        except OSError as exc:
            raise AuditError(f"Could not run ADB: {exc}") from exc
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "unknown error").strip()
            raise AuditError(f"ADB read failed: {detail[:200]}")
        return result.stdout

    def devices(self) -> list[Device]:
        return parse_devices(self._call(("devices", "-l")))

    def pick(self, requested: str | None = None) -> Device:
        found = self.devices()
        if requested:
            if not SERIAL_PATTERN.fullmatch(requested):
                raise AuditError("Invalid device identifier.")
            matches = [device for device in found if device.serial == requested]
            if not matches:
                raise AuditError("The selected phone is not connected. Run `devices` to check.")
            if matches[0].state != "device":
                if matches[0].state == "offline":
                    raise AuditError("This phone is offline. Reconnect the cable and unlock the screen.")
                raise AuditError("This phone is not authorized. Unlock it and accept USB debugging.")
            return matches[0]
        ready = [device for device in found if device.state == "device"]
        if len(ready) > 1:
            raise AuditError("More than one device is ready. Choose one with --serial <id>.")
        if len(ready) == 1:
            return ready[0]
        if any(d.state == "unauthorized" for d in found):
            raise AuditError("Your phone is connected but not authorized. Unlock it and approve the USB debugging prompt.")
        if any(d.state == "offline" for d in found):
            raise AuditError("Your phone shows as offline. Reconnect the cable and unlock the screen.")
        raise AuditError("No phone detected. Connect a phone, enable USB debugging, then try again.")

    def read(self, serial: str, *parts: str) -> str:
        command = tuple(parts)
        if command not in READ_ONLY_COMMANDS:
            raise AuditError("Blocked command: the audit tool permits only predefined read-only ADB queries.")
        if not SERIAL_PATTERN.fullmatch(serial):
            raise AuditError("Invalid device identifier.")
        return self._call(("-s", serial, *command), timeout=30)
