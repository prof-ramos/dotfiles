import importlib.util,tempfile,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
spec=importlib.util.spec_from_file_location('prefs',Path(__file__).resolve().parents[1]/'scripts/macos-preferences.py')
class PrefTests(unittest.TestCase):
 def api(self):
  m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 def test_missing_key_restored_by_delete(self):
  a=self.api();b=a.MemoryBackend({})
  with tempfile.TemporaryDirectory() as td:
   j=a.apply_preferences([{'domain':'test','key':'k','value':True}],b,Path(td).resolve());self.assertEqual(b.get('test','k'),(True,True));a.restore_preferences(j,b);self.assertEqual(b.get('test','k'),(False,None))
 def test_apply_uses_selected_keys_only(self):
  a=self.api();b=a.MemoryBackend({('test','other'):'untouched'})
  with tempfile.TemporaryDirectory() as td:a.apply_preferences([{'domain':'test','key':'k','value':3}],b,Path(td).resolve())
  self.assertEqual(b.get('test','other'),(True,'untouched'))
 def test_dry_run_has_no_mutations(self):
  a=self.api();b=a.MemoryBackend({})
  with tempfile.TemporaryDirectory() as td:
   a.apply_preferences([{'domain':'test','key':'k','value':3}],b,Path(td).resolve(),dry=True);self.assertEqual(b.values,{});self.assertEqual(list(Path(td).iterdir()),[])
 def test_production_backend_restores_nonempty_dock_array(self):
  import uuid
  a=self.api();b=a.DefaultsBackend();domain='org.dotfiles.test.'+uuid.uuid4().hex
  previous=[{'tile-data':{'file-label':'Example','file-data':{'_CFURLString':'file:///Applications/Example.app/'}}}]
  try:
   b.set(domain,'persistent-apps',previous)
   with tempfile.TemporaryDirectory() as td:
    j=a.apply_preferences([{'domain':domain,'key':'persistent-apps','value':[]}],b,Path(td).resolve());a.restore_preferences(j,b)
   self.assertEqual(b.get(domain,'persistent-apps'),(True,previous))
  finally:
   import subprocess
   subprocess.run(['defaults','delete',domain],capture_output=True)
