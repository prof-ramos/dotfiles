import importlib.util,tempfile,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
class AppTests(unittest.TestCase):
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
