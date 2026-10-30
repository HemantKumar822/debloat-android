import os
import stat
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from android_care.installation import bundle_files, checked_path, install, installation_target, package


ROOT = Path(__file__).resolve().parents[1]


class InstallationTests(unittest.TestCase):
    def test_user_hosts_install_under_expected_personal_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            for host, folder in [('codex', '.agents/skills'), ('cursor', '.cursor/skills'),
                                 ('claude', '.claude/skills'), ('antigravity', '.gemini/config/skills')]:
                home = Path(temp) / host
                target = installation_target(host, user=True, home=home)
                install(ROOT, target)
                self.assertTrue((home / folder / 'android-device-care/SKILL.md').is_file())

    def test_curated_manifest_excludes_private_and_nested_files(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'source'
            wanted = ['SKILL.md', 'LICENSE', 'scripts/android_care.py', 'scripts/install_skill.py',
                      'android_care/__init__.py', 'android_care/adb.py', 'android_care/cli.py',
                      'android_care/analyzer.py', 'android_care/report.py', 'android_care/installation.py',
                      'references/onboarding.md', 'references/roadmap.md', 'references/safety-and-evidence.md']
            unwanted = ['reports/private.md', '.git/config', 'website/index.html',
                        'tools/adb.exe', 'android_care/__pycache__/cached.py',
                        'references/private/secret.md', 'scripts/unrelated.py',
                        'references/android-audit-report.md', 'android_care/private_export.py']
            for relative in wanted + unwanted:
                path = source / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(relative, encoding='utf-8')
            self.assertEqual(set(bundle_files(source)), set(wanted))

    def test_reparse_point_rejected_without_pathlib_junction_api(self):
        # Python 3.10/3.11 lack Path.is_junction; lstat exposes this flag there.
        with patch.object(Path, 'is_symlink', return_value=False), \
             patch.object(Path, 'is_junction', return_value=False, create=True), \
             patch.object(Path, 'lstat', return_value=SimpleNamespace(
                 st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)):
            with self.assertRaisesRegex(ValueError, 'reparse|junction'):
                checked_path(ROOT / 'linked-project')

    def make_link(self, link, target):
        try:
            link.symlink_to(target, target_is_directory=target.is_dir())
        except OSError as exc:
            self.skipTest(f'Symlink creation unavailable on this host: {exc}')

    def test_symlink_destination_ancestor_refused_without_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            outside = Path(temp) / 'outside'
            outside.mkdir()
            link = Path(temp) / 'project'
            self.make_link(link, outside)
            with self.assertRaisesRegex(ValueError, 'Symlink|junction'):
                install(ROOT, link / '.agents/skills/android-device-care')
            with self.assertRaisesRegex(ValueError, 'Symlink|junction'):
                package(ROOT, link / 'bundle.zip')
            self.assertEqual(list(outside.iterdir()), [])

    def test_symlink_source_ancestor_and_file_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'source'
            install(ROOT, source)
            link = Path(temp) / 'alias'
            self.make_link(link, source)
            with self.assertRaisesRegex(ValueError, 'Symlink|junction'):
                bundle_files(link)
            (source / 'LICENSE').unlink()
            self.make_link(source / 'LICENSE', ROOT / 'LICENSE')
            with self.assertRaisesRegex(ValueError, 'Symlink|junction'):
                bundle_files(source)

    def run_script(self, name, *args, cwd=None):
        return subprocess.run([sys.executable, str(ROOT / 'scripts' / name), *map(str, args)],
                              cwd=cwd, capture_output=True, text=True, encoding='utf-8',
                              env={**os.environ, 'PYTHONUTF8': '1'})

    def test_project_hosts_install_curated_files_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            for host, folder in [('codex', '.agents'), ('cursor', '.cursor'),
                                 ('claude', '.claude'), ('antigravity', '.agents')]:
                project = Path(temp) / (host + ' project नमस्ते')
                result = self.run_script('install_skill.py', '--agent', host, '--project', project)
                self.assertEqual(result.returncode, 0, result.stderr)
                target = project / folder / 'skills/android-device-care'
                self.assertTrue((target / 'SKILL.md').is_file())
                self.assertTrue((target / 'LICENSE').is_file())
                self.assertTrue((target / 'scripts/android_care.py').is_file())
                self.assertTrue((target / 'references/onboarding.md').is_file())
                self.assertFalse((target / 'website').exists())
                self.assertFalse((target / 'tests').exists())
                self.assertTrue((target / 'scripts/install_skill.py').exists())
                (target / 'SKILL.md').write_text('keep me', encoding='utf-8')
                result = self.run_script('install_skill.py', '--agent', host, '--project', project)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((target / 'SKILL.md').read_text(), 'keep me')

    def test_dry_run_missing_project_does_not_write(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / 'missing'
            result = self.run_script('install_skill.py', '--agent', 'cursor', '--project', project, '--dry-run')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('.cursor', result.stdout)
            self.assertFalse(project.exists())

    def test_unicode_target_works_with_legacy_console_encoding(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / 'नमस्ते'
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/install_skill.py'),
                                     '--agent', 'codex', '--project', str(project)],
                                    capture_output=True, text=True,
                                    env={**os.environ, 'PYTHONIOENCODING': 'ascii'})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project / '.agents/skills/android-device-care/SKILL.md').is_file())

    def test_installed_demo_runs_from_different_directory_without_adb(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / 'project'
            result = self.run_script('install_skill.py', '--agent', 'codex', '--project', project)
            self.assertEqual(result.returncode, 0, result.stderr)
            entry = project / '.agents/skills/android-device-care/scripts/android_care.py'
            result = subprocess.run([sys.executable, str(entry), 'demo', '--output', 'sample.md'],
                                    cwd=temp, capture_output=True, text=True,
                                    env={**os.environ, 'PATH': '', 'PYTHONUTF8': '1'})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('#', (Path(temp) / 'sample.md').read_text(encoding='utf-8'))

    def test_zip_matches_installed_files_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / 'project'
            result = self.run_script('install_skill.py', '--agent', 'claude', '--project', project)
            self.assertEqual(result.returncode, 0, result.stderr)
            archive = Path(temp) / 'debloat android.zip'
            result = self.run_script('package_skill.py', '--output', archive)
            self.assertEqual(result.returncode, 0, result.stderr)
            target = project / '.claude/skills/android-device-care'
            files = {p.relative_to(target).as_posix(): p.read_bytes() for p in target.rglob('*') if p.is_file()}
            with zipfile.ZipFile(archive) as bundle:
                self.assertEqual({n.removeprefix('android-device-care/'): bundle.read(n) for n in bundle.namelist()}, files)
                self.assertFalse(any('..' in n.split('/') for n in bundle.namelist()))
            before = archive.read_bytes()
            result = self.run_script('package_skill.py', '--output', archive)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(archive.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()

