import importlib.util,tempfile,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
spec=importlib.util.spec_from_file_location('prefs',Path(__file__).resolve().parents[1]/'scripts/macos-preferences.py')
class PrefTests(unittest.TestCase):
 def test_dock_metadata_is_ignored_but_order_and_app_changes_are_detected(self):
  a=self.api()
  desired=[{'tile-type':'file-tile','tile-data':{'file-data':{'_CFURLString':'file:///Applications/One.app/','_CFURLStringType':15}}},
           {'tile-type':'file-tile','tile-data':{'file-data':{'_CFURLString':'file:///Applications/Two.app/','_CFURLStringType':15}}}]
  import copy
  current=copy.deepcopy(desired)
  current[0]['GUID']=123
  current[0]['tile-data']['book']=b'private-bookmark'
  current[0]['tile-data']['file-mod-date']=456
  item={'domain':'com.apple.dock','key':'persistent-apps','value':desired}
  backend=a.MemoryBackend({('com.apple.dock','persistent-apps'):current})
  self.assertEqual(a.verify_preferences([item],backend),[])
  with tempfile.TemporaryDirectory() as td:
   journal=a.apply_preferences([item],backend,Path(td).resolve())
   self.assertEqual(backend.get('com.apple.dock','persistent-apps')[1],current)
  backend.set('com.apple.dock','persistent-apps',list(reversed(current)))
  self.assertEqual(len(a.verify_preferences([item],backend)),1)
  backend.set('com.apple.dock','persistent-apps',current[:1])
  self.assertEqual(len(a.verify_preferences([item],backend)),1)
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
  previous=[{'tile-data':{'book':b'synthetic-bookmark','file-label':'Example','file-data':{'_CFURLString':'file:///Applications/Example.app/'}}}]
  try:
   b.set(domain,'persistent-apps',previous)
   with tempfile.TemporaryDirectory() as td:
    j=a.apply_preferences([{'domain':domain,'key':'persistent-apps','value':[]}],b,Path(td).resolve());a.restore_preferences(j,b)
   self.assertEqual(b.get(domain,'persistent-apps'),(True,previous))
  finally:
   import subprocess
   subprocess.run(['defaults','delete',domain],capture_output=True)
