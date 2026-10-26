import importlib.util,sys,tempfile,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class DiagnosticTests(unittest.TestCase):
 def test_plan_describes_conflicts_and_typed_changes_without_writing(self):
  p=load('preview');prefs=load('macos-preferences').MemoryBackend({('com.apple.dock','tilesize'):52})
  handlers=load('default-apps').MemoryHandlers({'txt':'com.apple.TextEdit'})
  with tempfile.TemporaryDirectory() as td:
   base=Path(td).resolve();home=base/'home';home.mkdir();(home/'.zshrc').write_text('private content')
   repo=base/'repo';(repo/'scripts').mkdir(parents=True);(repo/'macos/preferences').mkdir(parents=True);(repo/'.zshrc').write_text('new shell')
   (repo/'scripts/managed-files.json').write_text('[{"package":".","source":".zshrc","target":".zshrc"}]')
   (repo/'macos/preferences/defaults.json').write_text('[{"domain":"com.apple.dock","key":"tilesize","value":68}]')
   (repo/'macos/default-apps.json').write_text('{"txt":"com.apple.TextEdit"}');(repo/'macos/folder-icons.json').write_text('[]')
   before=list(home.iterdir());plan=p.build_plan(repo,home,['shell','macos','visual'],[],prefs,handlers)
   self.assertEqual(list(home.iterdir()),before);self.assertEqual((home/'.zshrc').read_text(),'private content')
   self.assertEqual(next(i for i in plan['links'] if i['target']=='.zshrc')['action'],'conflict')
   change=next(i for i in plan['preferences'] if i['key']=='tilesize');self.assertEqual(change['current'],52);self.assertEqual(change['desired'],68)
   text=p.format_plan(plan);self.assertIn('tilesize',text);self.assertIn('52',text);self.assertNotIn('private content',text)
   self.assertEqual(plan['handlers'],[{'extension':'txt','current':'com.apple.TextEdit','desired':'com.apple.TextEdit','change':False}])
 def test_preference_apply_detects_backend_that_did_not_persist(self):
  a=load('macos-preferences')
  class Broken(a.MemoryBackend):
   def set(self,*args):pass
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(RuntimeError):a.apply_preferences([{'domain':'test','key':'k','value':1}],Broken({}),Path(td).resolve())
 def test_preference_verify_reports_names_and_values(self):
  a=load('macos-preferences');r=a.verify_preferences([{'domain':'test','key':'k','value':2}],a.MemoryBackend({('test','k'):1}))
  self.assertEqual(r,[{'domain':'test','key':'k','current':1,'desired':2,'exists':True}])
 def test_preference_apply_preserves_declared_scalar_type(self):
  a=load('macos-preferences');backend=a.MemoryBackend({('test','k'):True})
  with tempfile.TemporaryDirectory() as td:a.apply_preferences([{'domain':'test','key':'k','value':1}],backend,Path(td).resolve())
  self.assertIs(type(backend.get('test','k')[1]),int)

 def test_scalar_type_changes_restore_original_type(self):
  a=load('macos-preferences')
  for before,after in [(True,1),(1,1.0),(1.0,True)]:
   with self.subTest(before=type(before),after=type(after)),tempfile.TemporaryDirectory() as td:
    backend=a.MemoryBackend({('test','k'):before});journal=a.apply_preferences([{'domain':'test','key':'k','value':after}],backend,Path(td).resolve())
    a.restore_preferences(journal,backend)
    self.assertIs(type(backend.get('test','k')[1]),type(before))
