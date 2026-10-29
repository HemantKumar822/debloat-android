import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from android_care.adb import ADB, AuditError, Device
from android_care.analyzer import classify, collect, make_audit
from android_care.cli import main, save_report
from android_care.report import render
from test_audit import FakeADB


class BoundaryTests(unittest.TestCase):
    def test_low_level_boundary_blocks_mutations(self):
        def runner(*args, **kwargs):
            self.fail('Forbidden command reached the process runner')
        adb = ADB(executable='adb', runner=runner)
        for args in [('shell', 'pm', 'clear', 'com.example.app'),
                     ('reboot',), ('install', 'app.apk'),
                     ('-s', 'phone', 'shell', 'settings', 'put', 'x', 'y')]:
            with self.subTest(args=args), self.assertRaises(AuditError):
                adb._call(args)

    def test_option_shaped_serial_is_rejected(self):
        adb = ADB(executable='adb', runner=lambda *a, **k: self.fail('runner called'))
        with self.assertRaises(AuditError):
            adb.read('-s', 'shell', 'pm', 'list', 'packages')

    def test_offline_selection_has_specific_guidance(self):
        adb = ADB(executable='adb', runner=lambda args, **kw:
                  subprocess.CompletedProcess(args, 0, 'phone offline\n', ''))
        with self.assertRaisesRegex(AuditError, 'offline'):
            adb.pick('phone')

    def test_timeout_has_actionable_error(self):
        def runner(*args, **kwargs):
            raise subprocess.TimeoutExpired('adb', 20)
        with self.assertRaisesRegex(AuditError, 'cable'):
            ADB(executable='adb', runner=runner).devices()


class OnboardingTests(unittest.TestCase):
    def test_consented_audit_saves_markdown_and_json_without_identifier(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/'audit.md'
            fake = FakeADB()
            fake.pick = lambda serial: Device('PRIVATE_SERIAL_987', 'device', '')
            with patch('android_care.cli.ADB', return_value=fake), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(['audit', '--consent', '--output', str(target), '--save-json']), 0)
            for file in [target, target.with_suffix('.json')]:
                self.assertTrue(file.exists())
                self.assertNotIn('PRIVATE_SERIAL_987', file.read_text(encoding='utf-8'))

    def test_audit_requires_consent_before_adb_initialization(self):
        with patch('android_care.cli.ADB') as adapter, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(['audit']), 2)
            adapter.assert_not_called()

    def test_doctor_guides_connection_states_without_inventory(self):
        for listing, expected, code in [('', 'No phone', 2),
                ('one unauthorized\n', 'Unlock', 2),
                ('one offline\n', 'Reconnect', 2),
                ('one device\ntwo device\n', '--serial', 2),
                ('one device\n', '--consent', 0)]:
            calls = []
            def runner(args, **kwargs):
                calls.append(args[1:])
                return subprocess.CompletedProcess(args, 0, listing, '')
            output = io.StringIO()
            with self.subTest(listing=listing), patch('android_care.cli.ADB',
                    return_value=ADB(executable='adb', runner=runner)), contextlib.redirect_stdout(output):
                self.assertEqual(main(['doctor']), code)
                self.assertIn(expected, output.getvalue())
                self.assertEqual(calls, [['devices', '-l']])

    def test_legacy_windows_console_can_generate_demo(self):
        with tempfile.TemporaryDirectory() as folder:
            stream = io.TextIOWrapper(io.BytesIO(), encoding='cp1252', errors='strict')
            with contextlib.redirect_stdout(stream):
                self.assertEqual(main(['demo', '--output', str(Path(folder)/'测试.md')]), 0)
            self.assertTrue((Path(folder)/'测试.md').exists())

    def test_doctor_missing_adb_is_friendly(self):
        output = io.StringIO()
        with patch('android_care.cli.ADB', side_effect=AuditError('ADB was not found')), contextlib.redirect_stderr(output):
            self.assertEqual(main(['doctor']), 2)
        self.assertIn('ADB was not found', output.getvalue())


class EvidenceTests(unittest.TestCase):
    def test_malformed_package_query_fails_closed(self):
        for flag in [None, '-s', '-3', '-d']:
            class Malformed(FakeADB):
                def read(self, serial, *args):
                    target = ('shell', 'pm', 'list', 'packages') + ((flag,) if flag else ())
                    if args == target:
                        return 'package:android\nError: permission denied\n'
                    return super().read(serial, *args)
            with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, 'package'):
                collect(Malformed(), 'phone')

    def test_inconsistent_categories_fail_closed(self):
        for response in ['package:com.not.in.inventory\n', 'package:com.example.app\n']:
            class Inconsistent(FakeADB):
                def read(self, serial, *args):
                    if args == ('shell', 'pm', 'list', 'packages', '-s'):
                        return response
                    return super().read(serial, *args)
            with self.subTest(response=response), self.assertRaisesRegex(ValueError, 'inconsistent'):
                collect(Inconsistent(), 'phone')

    def test_disabled_query_cannot_silently_claim_enabled(self):
        class InvalidDisabled(FakeADB):
            def read(self, serial, *args):
                if args == ('shell', 'pm', 'list', 'packages', '-d'):
                    return 'Failure [not allowed]'
                return super().read(serial, *args)
        with self.assertRaises(ValueError):
            collect(InvalidDisabled(), 'phone')

    def test_inventory_records_provenance_without_serial(self):
        audit = collect(FakeADB(), 'PRIVATE_SERIAL_987')
        self.assertIn('evidence', audit)
        self.assertEqual(len(audit['evidence']), 10)
        self.assertEqual(audit['evidence'][8]['status'], 'empty')
        self.assertTrue(all(e['status'] in ('observed', 'empty') for e in audit['evidence']))
        self.assertNotIn('PRIVATE_SERIAL_987', str(audit))
        self.assertEqual(audit['backup_status'], 'Not verified')

    def test_optional_failure_is_visible_in_evidence(self):
        class NoBattery(FakeADB):
            def read(self, serial, *args):
                if args == ('shell', 'dumpsys', 'battery'):
                    raise AuditError('unavailable')
                return super().read(serial, *args)
        audit = collect(NoBattery(), 'phone')
        self.assertEqual(audit['evidence'][-1]['status'], 'unavailable')
        self.assertIsNone(audit['battery']['level'])

    def test_core_name_matching_respects_package_boundaries(self):
        self.assertEqual(classify('com.google.android.gmsclone', False, False)['group'], 'not-classified')
        self.assertEqual(classify('androidish.app', False, False)['group'], 'not-classified')
        self.assertEqual(classify('com.google.android.gms', True, False)['group'], 'protected')

    def test_report_shows_observed_state_and_evidence_limits(self):
        audit = collect(FakeADB(), 'phone')
        html = render(audit)
        for phrase in ['Backup status', 'Not verified', 'Evidence coverage',
                       'Enabled', 'Not a backup', 'USB debugging']:
            self.assertIn(phrase, html)

    def test_only_markdown_report_paths_are_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'report.json'
            with self.assertRaisesRegex(ValueError, 'md'):
                save_report(collect(FakeADB(), 'phone'), str(path), True)
            self.assertFalse(path.exists())

    def test_existing_json_companion_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/'report.md'
            companion = target.with_suffix('.json')
            companion.write_text('keep this', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                save_report(collect(FakeADB(), 'phone'), str(target), True)
            self.assertEqual(companion.read_text(encoding='utf-8'), 'keep this')
            self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()

