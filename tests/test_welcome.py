import subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WelcomeTests(unittest.TestCase):
 def test_install_explains_activation_and_read_only_boundary(self):
  with tempfile.TemporaryDirectory() as folder:
   result=subprocess.run([sys.executable,str(ROOT/'scripts/install_skill.py'),'--agent','codex','--project',folder],capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr)
   self.assertIn('NEXT STEPS',result.stdout)
   self.assertIn('No phone was accessed',result.stdout)
   self.assertIn('Use android-device-care',result.stdout)
