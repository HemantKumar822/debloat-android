"""Experimental single-app changes. Audit adapter remains read-only.

Approval digests bind a reviewed document, not a security sandbox or signature.
Local files and an unrestricted agent must still be trusted.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from android_care.adb import AuditError, SERIAL_PATTERN
from android_care.analyzer import classify
from android_care.installation import checked_path

PACKAGE = re.compile(r'[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+')
ROLES = ('HOME', 'DIALER', 'SMS', 'ASSISTANT', 'BROWSER', 'EMERGENCY', 'CALL_SCREENING', 'CALL_REDIRECTION')
QUERIES = frozenset({
    ('shell', 'am', 'get-current-user'), ('shell', 'pm', 'list', 'users'),
    ('shell', 'getprop', 'ro.build.fingerprint'),
    ('shell', 'dumpsys', 'device_policy'),
    ('shell', 'settings', 'get', 'secure', 'default_input_method'),
    *(('shell', 'cmd', 'role', 'get-role-holders', '--user', '0', 'android.app.role.' + role) for role in ROLES),
})


def valid_package(package):
    if not isinstance(package, str) or not PACKAGE.fullmatch(package):
        raise AuditError('Invalid package identifier; components and shell syntax are forbidden.')


class ChangeADB:
    """Narrow separate process boundary; no arbitrary shell command API."""
    def __init__(self, executable=None, runner=None):
        self.executable = executable or shutil.which('adb')
        self.runner = runner or subprocess.run
        if not self.executable: raise AuditError('Install Android Platform Tools; adb is missing.')

    def _call(self, serial, args):
        if not isinstance(serial, str) or not SERIAL_PATTERN.fullmatch(serial):
            raise AuditError('Invalid device identifier.')
        package_query = len(args) == 4 and args[:3] == ('shell', 'dumpsys', 'package') and PACKAGE.fullmatch(args[3])
        mutation = (len(args) == 6 and args[:2] == ('shell', 'pm')
                    and args[2] in ('disable-user', 'enable', 'default-state')
                    and args[3:5] == ('--user', '0') and PACKAGE.fullmatch(args[5]))
        if args not in QUERIES and not package_query and not mutation:
            raise AuditError('Blocked: command is outside the change executor allowlist.')
        try:
            result = self.runner([self.executable, '-s', serial, *args], capture_output=True,
                text=True, encoding='utf-8', errors='replace', timeout=30, check=False, shell=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise AuditError('ADB interrupted. A submitted change may have happened; inspect the recovery receipt.') from exc
        if result.returncode != 0 or re.search(r'(?im)^\s*(error|failure|exception|unknown command|securityexception)', result.stdout):
            raise AuditError('ADB could not confirm the operation. Stop and inspect state; do not retry blindly.')
        return result.stdout

    def query(self, serial, *args):
        if args not in QUERIES and not (len(args) == 4 and args[:3] == ('shell', 'dumpsys', 'package')):
            raise AuditError('Blocked read query.')
        return self._call(serial, tuple(args))

    def change(self, serial, package, operation):
        valid_package(package)
        if operation not in ('disable-user', 'enable', 'default-state'):
            raise AuditError('Only disable and exact-state restoration are supported.')
        return self._call(serial, ('shell', 'pm', operation, '--user', '0', package))


def digest(document):
    return hashlib.sha256(json.dumps(document, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()


def save_document(path, document):
    path = checked_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    checked_path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        json.dump(document, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())


def owner(adb, serial):
    if adb.query(serial, 'shell', 'am', 'get-current-user').strip() != '0':
        raise AuditError('Only the active owner user 0 is supported.')
    users = adb.query(serial, 'shell', 'pm', 'list', 'users')
    if not users.strip().startswith('Users:') or re.findall(r'UserInfo\{(\d+):', users) != ['0']:
        raise AuditError('Multiple users/work profiles or unknown user output: changes blocked.')


def snapshot(adb, serial, package, *, guards=True):
    valid_package(package)
    owner(adb, serial)
    fingerprint = adb.query(serial, 'shell', 'getprop', 'ro.build.fingerprint').strip()
    if not fingerprint or '\n' in fingerprint: raise AuditError('Build identity is unavailable.')
    raw = adb.query(serial, 'shell', 'dumpsys', 'package', package)
    # Parse only the exact active package block, not disabled-system history or resolver tables.
    blocks = re.findall(r'(?ms)^\s*Package \[' + re.escape(package) + r'\][^\n]*\n(.*?)(?=^\s*Package \[|\Z)', raw)
    if len(blocks) != 1: raise AuditError('Ambiguous or missing package details.')
    block = blocks[0]
    versions = re.findall(r'\bversionCode=(\d+)', block)
    states = re.findall(r'(?m)^\s*User 0:\s*(.*)$', block)
    if len(versions) != 1 or len(states) != 1: raise AuditError('Incomplete package state.')
    state = states[0]
    enabled = re.search(r'\benabled=([0-4])\b', state)
    if not enabled or not all(value in state.split() for value in ('installed=true', 'hidden=false', 'suspended=false')):
        raise AuditError('Unsupported package/user state.')
    if guards:
        flags = re.findall(r'(?m)^[ \t]*(?:pkgFlags|flags)=\[([^\]\r\n]*)\][ \t]*$', block)
        if len(flags) != 1 or any(re.search(r'\b(SYSTEM|UPDATED_SYSTEM_APP|PERSISTENT)\b', flag) for flag in flags):
            raise AuditError('System, persistent or unclassified packages are not supported in this experimental release.')
        if classify(package, False, False)['group'] == 'protected' or re.search(r'sharedUser|sharedUserId|sharedUserSetting|android.permission.BIND_|DEVICE_ADMIN', raw, re.I):
            raise AuditError('Protected infrastructure, shared UID or sensitive bound service: leave unchanged.')
        policy = adb.query(serial, 'shell', 'dumpsys', 'device_policy')
        # AOSP's legacy and modern empty sections terminate at mPasswordOwner.
        # Requiring only whitespace between them catches flattened admin components
        # and refuses truncated or vendor-specific unknown formats.
        empty_admin = re.findall(r'(?m)^[ \t]*Enabled Device Admins \(User 0(?:, provisioningState: 0)?\):[ \t]*\r?\n\s*mPasswordOwner=-1[ \t]*$', policy)
        if (len(empty_admin) != 1 or len(re.findall('Enabled Device Admins', policy)) != 1
            or re.search(r'ComponentInfo|Device Owner:|Profile Owner', policy, re.I)):
            raise AuditError('Managed/admin state is present or cannot be established.')
        for role in ROLES:
            holders = adb.query(serial, 'shell', 'cmd', 'role', 'get-role-holders', '--user', '0', 'android.app.role.' + role).strip().splitlines()
            if any(not PACKAGE.fullmatch(value.strip()) for value in holders):
                raise AuditError('Role query is unsupported or malformed.')
            if package in [value.strip() for value in holders]: raise AuditError('The app holds an active Android role.')
        ime = adb.query(serial, 'shell', 'settings', 'get', 'secure', 'default_input_method').strip()
        if '/' not in ime or ime.split('/')[0] == package:
            raise AuditError('Keyboard protection could not be established or this is the active keyboard.')
    return {'device': digest({'serial': serial, 'build': fingerprint}), 'version': versions[0], 'enabled': int(enabled.group(1))}


def create_plan(adb, serial, package, reason, evidence, *, now=None):
    if not isinstance(reason, str) or not isinstance(evidence, str) or not reason.strip() or not 20 <= len(evidence.strip()) <= 2000 or len(reason) > 500:
        raise AuditError('Provide a concrete reason and reviewed evidence beyond the package name.')
    before = snapshot(adb, serial, package)
    if before['enabled'] not in (0, 1): raise AuditError('Only currently default/enabled apps may be disabled.')
    plan = {'schema': 1, 'operation': 'disable-user', 'user': 0, 'package': package,
            'created': time.time() if now is None else now, 'before': before,
            'reason': reason, 'evidence': evidence,
            'risk': 'The app and its notifications/background work will stop. Data is retained, but restoration is not a backup or recovery guarantee.'}
    validate_plan(plan)
    return plan


def validate_plan(plan):
    if len(json.dumps(plan, ensure_ascii=True)) > 20000:
        raise AuditError('Plan is too large; keep evidence concise so recovery remains portable.')
    if not isinstance(plan, dict) or set(plan) != {'schema', 'operation', 'user', 'package', 'created', 'before', 'reason', 'evidence', 'risk'}:
        raise AuditError('Invalid change plan schema.')
    if plan['schema'] != 1 or plan['operation'] != 'disable-user' or plan['user'] != 0:
        raise AuditError('Unsupported plan operation.')
    valid_package(plan['package'])
    before = plan['before']
    if (not isinstance(before, dict) or set(before) != {'device', 'version', 'enabled'}
        or type(before['enabled']) is not int or before['enabled'] not in (0, 1)
        or not isinstance(before['device'], str) or not re.fullmatch('[a-f0-9]{64}', before['device'])
        or not isinstance(before['version'], str) or not before['version'].isdigit()
        or type(plan['created']) not in (int, float)):
        raise AuditError('Invalid saved preconditions.')
    if any(not isinstance(plan[key], str) or not plan[key].strip() for key in ('reason', 'evidence', 'risk')):
        raise AuditError('Missing reviewed evidence.')


def approve(document, approval):
    if approval != digest(document): raise AuditError('Approval must match the full SHA-256 of the reviewed document.')


def apply_plan(adb, serial, plan, approval, receipt, *, now=None):
    validate_plan(plan); approve(plan, approval)
    age = (time.time() if now is None else now) - plan['created']
    if not 0 <= age <= 900: raise AuditError('Plan expired or future-dated. Create and review a new plan.')
    if snapshot(adb, serial, plan['package']) != plan['before']:
        raise AuditError('Device, app version or enabled state changed. Create a new plan.')
    recovery = {'schema': 1, 'status': 'prepared', 'plan': plan, 'plan_digest': digest(plan)}
    save_document(receipt, recovery)  # Durable before the first potentially mutating command.
    adb.change(serial, plan['package'], 'disable-user')
    expected = {**plan['before'], 'enabled': 3}
    if snapshot(adb, serial, plan['package'], guards=False) != expected:
        raise AuditError('Disable outcome not confirmed. Keep the receipt and inspect before restoring.')
    return {'status': 'verified-disabled', 'package': plan['package'], 'recovery': str(receipt)}


def restore(adb, serial, recovery, approval, receipt):
    approve(recovery, approval)
    if not isinstance(recovery, dict) or set(recovery) != {'schema', 'status', 'plan', 'plan_digest'} or recovery['schema'] != 1 or recovery['status'] != 'prepared':
        raise AuditError('Invalid recovery receipt.')
    plan = recovery['plan']; validate_plan(plan)
    if recovery['plan_digest'] != digest(plan): raise AuditError('Recovery plan checksum mismatch.')
    current = snapshot(adb, serial, plan['package'], guards=False)
    before = plan['before']
    if current == before: return {'status': 'already-restored', 'package': plan['package']}
    if current != {**before, 'enabled': 3}:
        raise AuditError('Device/build/version or package state differs; automatic restoration blocked.')
    save_document(receipt, {'schema': 1, 'status': 'restore-prepared', 'recovery_digest': digest(recovery)})
    adb.change(serial, plan['package'], 'default-state' if before['enabled'] == 0 else 'enable')
    if snapshot(adb, serial, plan['package'], guards=False) != before:
        raise AuditError('Restore not confirmed; reconnect and inspect. Do not assume recovery succeeded.')
    return {'status': 'verified-restored', 'package': plan['package']}
