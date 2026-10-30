import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from android_care.analyzer import demo_audit
from android_care.cli import main, save_report
from android_care.report import render


class MarkdownTests(unittest.TestCase):
    def test_complete_standalone_markdown_inventory(self):
        audit = demo_audit()
        document = render(audit)
        self.assertTrue(document.startswith('# Debloat Android'))
        for heading in ['Summary', 'Device snapshot', 'Package research', 'Full inventory',
                        'Evidence coverage', 'Backup status', 'Limitations', 'Next steps']:
            self.assertIn('## ' + heading, document)
        for package in audit['packages']:
            self.assertIn(package['package'], document)
            self.assertIn(package['reason'], document)
        self.assertNotIn('<', document)
        self.assertIn('Synthetic example: no device queries were performed.', document)

    def test_metadata_cannot_inject_markdown_html_or_table_rows(self):
        audit = demo_audit()
        payload = '<script>alert(1)</script>\n# forged | ![image](https://evil.test) `code` &lt;b&gt;'
        audit['device']['model'] = payload
        audit['warnings'] = [payload]
        document = render(audit)
        self.assertNotIn('<script>', document)
        self.assertNotIn('\n# forged', document)
        self.assertNotIn('![image]', document)
        self.assertNotIn('`code`', document)
        self.assertIn('&lt;script&gt;', document)
        self.assertIn('\\|', document)
        self.assertIn('&amp;lt;b&amp;gt;', document)

    def test_demo_default_is_markdown_without_adb(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = os.getcwd()
            try:
                os.chdir(directory)
                with patch('android_care.cli.ADB') as adb, contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(['demo']), 0)
                adb.assert_not_called()
                self.assertTrue(Path('demo-android-audit.md').is_file())
            finally:
                os.chdir(previous)

    def test_markdown_extensions_and_utf8_json(self):
        with tempfile.TemporaryDirectory() as directory:
            for index, suffix in enumerate(['.md', '.markdown', '.MD']):
                target = Path(directory) / ('测试' + str(index) + suffix)
                audit = demo_audit()
                audit['device']['model'] = '测试手机'
                save_report(audit, str(target), False)
                self.assertIn('测试手机', target.read_text(encoding='utf-8'))
            for suffix in ['.html', '.htm', '.json', '.txt']:
                with self.assertRaisesRegex(ValueError, 'md'):
                    save_report(demo_audit(), str(Path(directory) / ('reject' + suffix)), False)
