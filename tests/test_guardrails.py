import importlib.util, json, os, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT/"scripts"))
def module(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class GuardrailsTests(unittest.TestCase):
 def test_check_stops_at_first_failure(self):
  import sys
  with tempfile.TemporaryDirectory() as td:
   root=Path(td).resolve();marker=root/'should-not-exist'
   code=module('check').run_steps([('bad',[sys.executable,'-c','raise SystemExit(7)']),('later',[sys.executable,'-c',f'open({str(marker)!r},"w").close()'])],root,root/'logs')
   self.assertEqual(code,7);self.assertFalse(marker.exists())
 def test_staged_check_uses_index_not_worktree(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td).resolve();subprocess.run(['git','init',str(root)],capture_output=True,check=True);(root/'scripts').mkdir()
   (root/'scripts/check.py').write_text('from pathlib import Path\nraise SystemExit(9 if Path("value").read_text()=="bad" else 0)\n');v=root/'value';v.write_text('bad')
   subprocess.run(['git','-C',str(root),'add','.'],check=True);v.write_text('good')
   self.assertEqual(module('check').check_staged(root),9)
 def test_missing_router_dependency_reported(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=root/'grill-me';p.mkdir();(p/'SKILL.md').write_text('Call the Skill tool with "grilling".')
   self.assertEqual(module('skill-doctor').inspect_skills([root])['missing'],[{'skill':'grill-me','dependency':'grilling'}])
 def test_present_router_dependency_succeeds(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   for name,text in [('grill-me','Call the Skill tool with "grilling".'),('grilling','Interview the user.')]:
    p=root/name;p.mkdir();(p/'SKILL.md').write_text(text)
   self.assertEqual(module('skill-doctor').inspect_skills([root])['missing'],[])
 def test_router_cycle_reported(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   for name,target in [('one','two'),('two','one')]:
    p=root/name;p.mkdir();(p/'SKILL.md').write_text(f'Call the Skill tool with "{target}".')
   self.assertTrue(module('skill-doctor').inspect_skills([root])['cycles'])
 def test_skill_install_resolves_router_in_one_operation(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);calls=[]
   def install(args,check):
    name=args[args.index('--skill')+1];calls.append(name);p=root/name;p.mkdir();(p/'SKILL.md').write_text('Call the Skill tool with "grilling".' if name=='grill-me' else 'Interview.')
   ready=module('install-agent-skills').ensure_skills(['grill-me'],[root],install)
   self.assertEqual(calls,['grill-me','grilling']);self.assertEqual(ready,['grill-me','grilling'])
 def test_skill_installer_rejects_option_injection_before_running(self):
  calls=[]
  with self.assertRaises(ValueError):module('install-agent-skills').ensure_skills(['--all'],[],lambda *a,**k:calls.append(a))
  self.assertEqual(calls,[])
 def test_hooks_installer_preserves_existing_hooks(self):
  import shutil
  with tempfile.TemporaryDirectory() as td:
   root=Path(td).resolve();subprocess.run(['git','init',str(root)],capture_output=True,check=True);(root/'scripts').mkdir();shutil.copy2(ROOT/'scripts/install-hooks.sh',root/'scripts/install-hooks.sh')
   subprocess.run(['git','-C',str(root),'config','core.hooksPath','existing-hooks'],check=True)
   r=subprocess.run(['/bin/zsh','-f',str(root/'scripts/install-hooks.sh')],capture_output=True)
   self.assertNotEqual(r.returncode,0);self.assertEqual(subprocess.check_output(['git','-C',str(root),'config','core.hooksPath'],text=True).strip(),'existing-hooks')
