import subprocess
import tempfile
import unittest
from pathlib import Path

from android_care.adb import ADB, AuditError, READ_ONLY_COMMANDS, parse_devices
from android_care.analyzer import parse_packages, parse_battery, classify, collect, demo_audit
from android_care.cli import main, save_report
from android_care.report import render


class FakeADB:
    def __init__(self):
        self.commands = []

    def read(self, serial, *args):
        self.commands.append(args)
        mock = {
            ("shell", "getprop", "ro.product.manufacturer"): "ExampleCo\n",
            ("shell", "getprop", "ro.product.model"): "Test One\n",
            ("shell", "getprop", "ro.build.version.release"): "15\n",
            ("shell", "getprop", "ro.build.version.sdk"): "35\n",
            ("shell", "getprop", "ro.build.version.security_patch"): "2026-09-01\n",
            ("shell", "pm", "list", "packages"): "package:android\npackage:com.vendor.analytics\npackage:com.example.app\n",
            ("shell", "pm", "list", "packages", "-s"): "package:android\npackage:com.vendor.analytics\n",
            ("shell", "pm", "list", "packages", "-3"): "package:com.example.app\n",
            ("shell", "pm", "list", "packages", "-d"): "",
            ("shell", "dumpsys", "battery"): "level: 83\nstatus: 2\n",
        }
        return mock[args]


class TestAdapter(unittest.TestCase):
    def test_device_listing(self):
        devices = parse_devices("List of devices attached\nabc123 device product:foo\nxyz unauthorized\n")
        self.assertEqual([d.state for d in devices], ["device", "unauthorized"])

    def test_rejects_mutations_even_if_requested(self):
        def runner(*a, **kw):
            raise AssertionError("runner must never receive forbidden command")
        adb = ADB(executable="adb", runner=runner)
        with self.assertRaises(AuditError):
            adb.read("abc", "shell", "pm", "disable-user", "--user", "0", "com.foo.bar")
        with self.assertRaises(AuditError):
            adb.read("abc", "shell", "pm", "list", "packages", "-s", ";rm")
        with self.assertRaises(AuditError):
            adb.read("evil;echo foo", "shell", "pm", "list", "packages")

    def test_multiple_devices_requires_target(self):
        def runner(args, **kwargs):
            return subprocess.CompletedProcess(args, 0, "List of devices attached\na device\nb device\n", "")
        adb = ADB(executable="adb", runner=runner)
        with self.assertRaisesRegex(AuditError, "More than one"):
            adb.pick()
        self.assertEqual(adb.pick("b").serial, "b")

    def test_read_only_allowlist(self):
        self.assertTrue(READ_ONLY_COMMANDS)
        joined = " ".join(" ".join(command) for command in READ_ONLY_COMMANDS)
        self.assertNotIn("uninstall", joined)
        self.assertNotIn("disable-user", joined)
        self.assertNotIn("settings put", joined)


class TestAnalysis(unittest.TestCase):
    def test_parse_package_output(self):
        parsed = parse_packages("package:android\npackage:com.foo.bar\npackage:evil;rm\n")
        self.assertEqual(parsed, {"android", "com.foo.bar"})

    def test_battery_level(self):
        self.assertEqual(parse_battery("level: 85\n")["level"], 85)
        self.assertIsNone(parse_battery("level: 200\n")["level"])

    def test_review_is_low_confidence(self):
        result = classify("com.vendor.analytics", True, False)
        self.assertEqual(result["group"], "review")
        self.assertIn("not proof", result["reason"])

    def test_collect_uses_only_allowlisted(self):
        adb = FakeADB()
        audit = collect(adb, "device1")
        self.assertEqual(audit["summary"]["total"], 3)
        self.assertEqual(audit["summary"]["review"], 1)
        self.assertTrue(all(command in READ_ONLY_COMMANDS for command in adb.commands))

    def test_empty_inventory_fails_closed(self):
        class Empty(FakeADB):
            def read(self, serial, *args):
                if args == ("shell", "pm", "list", "packages"):
                    return ""
                return super().read(serial, *args)
        with self.assertRaisesRegex(ValueError, "no package list"):
            collect(Empty(), "device1")

    def test_markdown_safely_escapes_device_metadata(self):
        audit = demo_audit()
        audit["device"]["model"] = '<img src=x onerror="alert(1)">'
        html = render(audit)
        self.assertIn("&lt;img", html)
        self.assertNotIn('<img src=x onerror="alert(1)">', html)
        self.assertIn("DEMO", html)

    def test_report_does_not_overwrite_existing_files(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "report.md"
            file.write_text("my important file", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                save_report(demo_audit(), str(file), False)
            self.assertEqual(file.read_text(encoding="utf-8"), "my important file")

    def test_report_contains_explanations(self):
        report = render(demo_audit())
        self.assertIn("Reason", report)
        self.assertIn("not proof of tracking", report)

    def test_demo_report_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "sample.md"
            self.assertEqual(main(["demo", "--output", str(file)]), 0)
            report = file.read_text(encoding="utf-8")
            self.assertIn("DEMO", report)
            self.assertIn("No changes performed", report)
            self.assertIn("Full inventory", report)
            self.assertFalse(file.with_suffix(".json").exists())


if __name__ == "__main__":
    unittest.main()

