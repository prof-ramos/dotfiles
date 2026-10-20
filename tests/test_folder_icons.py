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
 def replace_with_red(self,folder,root):
  p=root/'red.swift';p.write_text('import AppKit\nlet i=NSImage(size:NSSize(width:64,height:64)); i.lockFocus(); NSColor.red.setFill(); NSBezierPath(rect:NSRect(x:0,y:0,width:64,height:64)).fill(); i.unlockFocus(); assert(NSWorkspace.shared.setIcon(i,forFile:CommandLine.arguments[1],options:[]))\n')
  subprocess.run(['swift',str(p),str(folder)],check=True,capture_output=True)
 def test_restore_rejects_later_custom_icon(self):
  r,h,t=self.run_icon();self.assertEqual(r.returncode,0,r.stderr);folder=h/'Developer/infra';self.replace_with_red(folder,t)
  j=next((t/'state').glob('*/icons.json'));before=subprocess.check_output(['xattr','-px','com.apple.ResourceFork',str(folder/'Icon\r')])
  restore=subprocess.run([str(self.bin),'--restore',str(j)],capture_output=True,text=True)
  self.assertNotEqual(restore.returncode,0);self.assertEqual(subprocess.check_output(['xattr','-px','com.apple.ResourceFork',str(folder/'Icon\r')]),before)
 def test_prepared_record_reconciles_successful_seticon(self):
  r,h,t=self.run_icon();self.assertEqual(r.returncode,0,r.stderr);j=next((t/'state').glob('*/icons.json'));data=json.loads(j.read_text());data[0]['applied']=False;j.write_text(json.dumps(data))
  restore=subprocess.run([str(self.bin),'--restore',str(j)],capture_output=True,text=True);self.assertEqual(restore.returncode,0,restore.stderr)
  result=subprocess.run(['xattr','-px','com.apple.FinderInfo',str(h/'Developer/infra')],capture_output=True,text=True);info=''.join(result.stdout.split());flags=int(info[16:20],16) if info else 0;self.assertEqual(flags & 0x400,0)
