import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import contextlib
import io
from unittest.mock import patch

from android_care import changes
from android_care.adb import AuditError


class Phone:
    def __init__(self):
        self.state = 0
        self.version = '12'
        self.system = False
        self.role = ''
        self.writes = []
        self.fail_write = False

    def query(self, serial, *args):
        if args == ('shell', 'am', 'get-current-user'): return '0'
        if args == ('shell', 'pm', 'list', 'users'): return 'Users:\n UserInfo{0:Owner:13} running\n'
        if args[:3] == ('shell', 'getprop', 'ro.build.fingerprint'): return 'vendor/model/build'
        if args[:3] == ('shell', 'dumpsys', 'device_policy'): return 'Device Policy Manager state:\n Enabled Device Admins (User 0, provisioningState: 0):\n mPasswordOwner=-1\n'
        if args[:3] == ('shell', 'cmd', 'role'): return self.role
        if args[:3] == ('shell', 'settings', 'get'): return 'com.keyboard/.IME'
        if args[:3] == ('shell', 'dumpsys', 'package'):
            return f'Packages:\n Package [com.example.game] (abc):\n versionCode={self.version} minSdk=23\n pkgFlags=[ {"SYSTEM" if self.system else "HAS_CODE"} ]\n User 0: installed=true hidden=false suspended=false enabled={self.state}\n'
        raise AssertionError(args)

    def change(self, serial, package, operation):
        self.writes.append(operation)
        self.state = {'disable-user': 3, 'default-state': 0, 'enable': 1}[operation]
        if self.fail_write: raise AuditError('connection lost')


class ChangesTests(unittest.TestCase):
    def plan(self, phone=None):
        return changes.create_plan(phone or Phone(), 'phone', 'com.example.game',
            'I do not use this game', 'Publisher documentation reviewed; user confirms it is optional', now=100)

    def test_plan_does_not_write(self):
        phone = Phone()
        self.assertEqual(self.plan(phone)['before']['enabled'], 0)
        self.assertEqual(phone.writes, [])

    def test_apply_and_restore_exact_default(self):
        phone = Phone(); plan = self.plan(phone)
        with tempfile.TemporaryDirectory() as folder:
            receipt = Path(folder)/'receipt.json'
            changes.apply_plan(phone, 'phone', plan, changes.digest(plan), receipt, now=101)
            self.assertEqual(phone.state, 3)
            recovery = json.loads(receipt.read_text())
            changes.restore(phone, 'phone', recovery, changes.digest(recovery), Path(folder)/'restore.json')
            self.assertEqual(phone.writes, ['disable-user', 'default-state'])

    def test_reject_wrong_approval_stale_identity_and_drift(self):
        for fault in ('approval', 'stale', 'serial', 'drift', 'edited'):
            phone = Phone(); plan = self.plan(phone); approval = changes.digest(plan)
            if fault == 'drift': phone.version = '13'
            if fault == 'edited': plan['reason'] = 'edited after review'
            with tempfile.TemporaryDirectory() as folder, self.subTest(fault=fault), self.assertRaises(AuditError):
                changes.apply_plan(phone, 'other' if fault == 'serial' else 'phone', plan,
                    'wrong' if fault == 'approval' else approval, Path(folder)/'r.json',
                    now=1100 if fault == 'stale' else 101)
            self.assertEqual(phone.writes, [])

    def test_block_system_and_active_role(self):
        for fault in ('system', 'role'):
            phone = Phone()
            if fault == 'system': phone.system = True
            else: phone.role = 'com.example.game'
            with self.assertRaises(AuditError): self.plan(phone)

    def test_admin_policy_rejects_flattened_component_and_truncated_output(self):
        for policy in ('Enabled Device Admins (User 0):\n com.admin/.Receiver:\n mPasswordOwner=-1',
                       'Enabled Device Admins (User 0):\n',
                       'Enabled Device Admins (User 0, provisioningState: 3):\n mPasswordOwner=-1'):
            phone = Phone(); query = phone.query
            phone.query = lambda serial, *args: policy if args == ('shell', 'dumpsys', 'device_policy') else query(serial, *args)
            with self.subTest(policy=policy), self.assertRaises(AuditError): self.plan(phone)

    def test_large_evidence_is_rejected_before_device_query(self):
        with self.assertRaises(AuditError):
            changes.create_plan(Phone(), 'phone', 'com.example.game', 'optional', 'e'*90000, now=100)

    def test_permission_flags_cannot_substitute_for_package_classification(self):
        phone = Phone(); query = phone.query
        def override(serial, *args):
            value = query(serial, *args)
            if args[:3] == ('shell', 'dumpsys', 'package'):
                return value.replace('pkgFlags=[ HAS_CODE ]', 'runtime permissions:\n android.permission.POST_NOTIFICATIONS: granted=true, flags=[ USER_SET ]')
            return value
        phone.query = override
        with self.assertRaises(AuditError): self.plan(phone)

    def test_durable_receipt_survives_uncertain_write_and_can_restore(self):
        phone = Phone(); plan = self.plan(phone); phone.fail_write = True
        with tempfile.TemporaryDirectory() as folder:
            receipt = Path(folder)/'r.json'
            with self.assertRaises(AuditError):
                changes.apply_plan(phone, 'phone', plan, changes.digest(plan), receipt, now=101)
            self.assertEqual(json.loads(receipt.read_text())['status'], 'prepared')
            phone.fail_write = False
            recovery = json.loads(receipt.read_text())
            changes.restore(phone, 'phone', recovery, changes.digest(recovery), Path(folder)/'restored.json')
            self.assertEqual(phone.state, 0)

    def test_existing_receipt_prevents_mutation(self):
        phone = Phone(); plan = self.plan(phone)
        with tempfile.TemporaryDirectory() as folder:
            receipt = Path(folder)/'r.json'; receipt.write_text('keep')
            with self.assertRaises(FileExistsError):
                changes.apply_plan(phone, 'phone', plan, changes.digest(plan), receipt, now=101)
            self.assertEqual(phone.writes, [])

    def test_executor_blocks_injection_and_unrelated_commands(self):
        adapter = changes.ChangeADB(executable='adb', runner=lambda *a, **k: self.fail('runner called'))
        for package in ('com.foo;reboot', '-x', 'com.foo/.Activity'):
            with self.assertRaises(AuditError): adapter.change('phone', package, 'disable-user')
        with self.assertRaises(AuditError): adapter.change('phone', 'com.example.app', 'uninstall')
        with self.assertRaises(AuditError): adapter.query('phone', 'shell', 'reboot')

    def test_restore_explicit_enabled_and_idempotence(self):
        phone = Phone(); phone.state = 1; plan = self.plan(phone)
        with tempfile.TemporaryDirectory() as folder:
            receipt = Path(folder)/'r.json'
            changes.apply_plan(phone, 'phone', plan, changes.digest(plan), receipt, now=101)
            recovery = json.loads(receipt.read_text())
            changes.restore(phone, 'phone', recovery, changes.digest(recovery), Path(folder)/'restore.json')
            result = changes.restore(phone, 'phone', recovery, changes.digest(recovery), Path(folder)/'unused.json')
            self.assertEqual(result['status'], 'already-restored')
            self.assertEqual(phone.writes, ['disable-user', 'enable'])
            self.assertFalse((Path(folder)/'unused.json').exists())

    def test_unsupported_profiles_roles_and_sensitive_services_block(self):
        for kind in ('profile', 'role-error', 'service', 'shared', 'keyboard', 'missing-version'):
            phone = Phone(); query = phone.query
            def override(serial, *args):
                value = query(serial, *args)
                if kind == 'profile' and args == ('shell', 'pm', 'list', 'users'): return value+'UserInfo{10:Work:30}'
                if kind == 'role-error' and args[:3] == ('shell', 'cmd', 'role'): return 'Unknown command'
                if kind == 'keyboard' and args[:3] == ('shell', 'settings', 'get'): return 'com.example.game/.IME'
                if args[:3] == ('shell', 'dumpsys', 'package'):
                    if kind == 'service': return value+'android.permission.BIND_ACCESSIBILITY_SERVICE'
                    if kind == 'shared': return value+'sharedUserId=1000'
                    if kind == 'missing-version': return value.replace('versionCode=', 'missing=')
                return value
            phone.query = override
            with self.subTest(kind=kind), self.assertRaises(AuditError): self.plan(phone)
            self.assertEqual(phone.writes, [])

    def test_restore_rejects_foreign_device_version_and_modified_receipt(self):
        for kind in ('serial', 'version', 'tampered', 'state'):
            phone = Phone(); plan = self.plan(phone)
            with tempfile.TemporaryDirectory() as folder:
                receipt = Path(folder)/'r.json'
                changes.apply_plan(phone, 'phone', plan, changes.digest(plan), receipt, now=101)
                recovery = json.loads(receipt.read_text())
                if kind == 'version': phone.version = '13'
                if kind == 'tampered': recovery['plan']['package'] = 'com.other.app'
                if kind == 'state': phone.state = 2
                with self.subTest(kind=kind), self.assertRaises(AuditError):
                    changes.restore(phone, 'other' if kind == 'serial' else 'phone', recovery, changes.digest(recovery), Path(folder)/'restore.json')
                self.assertEqual(phone.writes, ['disable-user'])

    def test_cli_gates_before_adapter_initialization(self):
        from android_care.cli import main
        for flags in ([], ['--experimental']):
            with patch('android_care.changes.ChangeADB') as adapter, contextlib.redirect_stderr(io.StringIO()):
                result = main(['apply', '--serial', 'phone', '--plan', 'missing.json', '--approve', 'bad', '--receipt', 'unused.json', *flags])
                self.assertEqual(result, 2)
                adapter.assert_not_called()

    def test_cli_plan_apply_restore_end_to_end_without_hardware(self):
        from android_care.cli import main
        phone = Phone()
        with tempfile.TemporaryDirectory() as folder, patch('android_care.changes.ChangeADB', return_value=phone), contextlib.redirect_stdout(io.StringIO()):
            plan = Path(folder)/'plan.json'; receipt = Path(folder)/'recovery.json'
            common = ['--experimental', '--serial', 'phone']
            self.assertEqual(main(['plan', *common, '--consent', '--package', 'com.example.game', '--reason', 'Optional game', '--evidence', 'Publisher role reviewed; user confirms no dependency', '--output', str(plan)]), 0)
            self.assertIn('Review one app change', plan.with_suffix('.md').read_text())
            approval = changes.digest(json.loads(plan.read_text()))
            self.assertEqual(main(['apply', *common, '--backup-acknowledged', '--plan', str(plan), '--approve', approval, '--receipt', str(receipt)]), 0)
            approval = changes.digest(json.loads(receipt.read_text()))
            self.assertEqual(main(['restore', *common, '--backup-acknowledged', '--recovery', str(receipt), '--approve', approval, '--receipt', str(Path(folder)/'restored.json')]), 0)
            self.assertEqual(phone.state, 0)

    def test_process_boundary_exact_command_and_no_shell(self):
        calls = []
        def runner(command, **kwargs):
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(command, 0, 'Package com.example.game new state: disabled-user', '')
        adapter = changes.ChangeADB(executable='adb', runner=runner)
        adapter.change('phone', 'com.example.game', 'disable-user')
        self.assertEqual(calls[0][0], ['adb', '-s', 'phone', 'shell', 'pm', 'disable-user', '--user', '0', 'com.example.game'])
        self.assertFalse(calls[0][1]['shell'])


if __name__ == '__main__': unittest.main()
