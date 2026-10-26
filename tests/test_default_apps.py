import importlib.util,tempfile,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
class AppTests(unittest.TestCase):
 def test_per_extension_targets_apply_and_restore(self):
  a=self.api();b=a.MemoryHandlers({'md':'old.markdown','json':'old.json'})
  with tempfile.TemporaryDirectory() as td:
   j=a.apply_handlers({'md':'md.obsidian','json':'com.example.Editor'},b,Path(td).resolve())
   self.assertEqual(b.values,{'md':'md.obsidian','json':'com.example.Editor'})
   a.restore_handlers(j,b)
   self.assertEqual(b.values,{'md':'old.markdown','json':'old.json'})
 def api(self):
  s=importlib.util.spec_from_file_location('apps',Path(__file__).resolve().parents[1]/'scripts/default-apps.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 def test_apply_and_restore_prior_handler(self):
  a=self.api();b=a.MemoryHandlers({'txt':'old.bundle'})
  with tempfile.TemporaryDirectory() as td:
   j=a.apply_handlers(['txt'],b,Path(td).resolve());self.assertEqual(b.get('txt'),'com.sublimetext.4');a.restore_handlers(j,b);self.assertEqual(b.get('txt'),'old.bundle')
 def test_unknown_handler_aborts_before_changes(self):
  a=self.api();b=a.MemoryHandlers({'txt':'old.bundle'})
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(ValueError):a.apply_handlers(['txt','unknown'],b,Path(td).resolve())
  self.assertEqual(b.get('txt'),'old.bundle')
 def test_duti_reports_unapplied_change(self):
  from unittest.mock import patch
  import subprocess
  a=self.api()
  def run(args,**kwargs):return subprocess.CompletedProcess(args,0,stdout='Old App\n/Applications/Old.app\nold.bundle\n')
  with patch.object(a.subprocess,'run',side_effect=run),patch('time.sleep'):
   with self.assertRaises(RuntimeError):a.DutiHandlers().set('txt','com.sublimetext.4')
