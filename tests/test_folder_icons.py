import subprocess,tempfile,unittest,json,os,shutil
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
class IconTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.build=tempfile.TemporaryDirectory();cls.bin=Path(cls.build.name)/'icons'
  result=subprocess.run(['swiftc',str(REPO/'scripts/apply-folder-icons.swift'),'-o',str(cls.bin)],capture_output=True,text=True)
  if result.returncode:raise AssertionError(result.stderr)
 @classmethod
 def tearDownClass(cls):cls.build.cleanup()
 def run_icon(self,folder='Developer/infra',valid=True,dry=False):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);root=Path(self.t.name).resolve();home=root/'home';home.mkdir()
  shutil.copy2(REPO/'macos/icons/infra.icns',root/'infra.icns')
  (root/'map.json').write_text(json.dumps([{'folder':folder,'icon':'infra.icns' if valid else 'missing.icns'}]))
  cmd=[str(self.bin),'--map',str(root/'map.json'),'--home',str(home),'--state',str(root/'state')]
  if dry:cmd+=['--dry-run']
  return subprocess.run(cmd,capture_output=True,text=True),home,root
 def test_missing_folder_created(self):
  r,h,t=self.run_icon();self.assertEqual(r.returncode,0,r.stderr);self.assertTrue((h/'Developer/infra').is_dir())
  self.assertEqual(subprocess.run(['xattr','-p','com.apple.FinderInfo',str(h/'Developer/infra')],capture_output=True).returncode,0)
 def test_invalid_icon_reports_failure(self):
  r,h,t=self.run_icon(valid=False);self.assertNotEqual(r.returncode,0);self.assertFalse((h/'Developer').exists())
 def test_dry_run_creates_nothing(self):
  r,h,t=self.run_icon(dry=True);self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(list(h.iterdir()),[]);self.assertFalse((t/'state').exists())
 def test_paths_cannot_escape_home(self):
  r,h,t=self.run_icon(folder='../outside');self.assertNotEqual(r.returncode,0);self.assertFalse((t/'outside').exists())
