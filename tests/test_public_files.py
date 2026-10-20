import importlib, tempfile, unittest, sys, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
class PublicFilesTests(unittest.TestCase):
 def validate(self,rel,content='sample'):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
   return importlib.import_module('validate').validate_public(root)
 def test_private_key_and_token_files_rejected(self):
  for rel in ['ssh/id_ed25519','token.json','.env','auth.json']:
   with self.subTest(rel=rel):self.assertTrue(self.validate(rel))
 def test_sublime_sessions_and_license_rejected(self):
  for rel in ['sublime/Local/Session.sublime_session','sublime/Packages/User/License.sublime_license']:
   with self.subTest(rel=rel):self.assertTrue(self.validate(rel))
 def test_app_packages_have_exact_destinations(self):
  api=importlib.import_module('links');repo=Path(__file__).resolve().parents[1]
  with tempfile.TemporaryDirectory() as td:
   plan=api.plan_links(repo,Path(td).resolve())
   targets=[v['target'] for v in plan]
   self.assertIn('Library/Application Support/com.mitchellh.ghostty/config.ghostty',targets)
   self.assertIn('Library/Application Support/Sublime Text/Packages/User/Preferences.sublime-settings',targets)
 def test_secret_content_rejected_without_echo(self):
  errors=self.validate('.aliases','-----BEGIN '+'OPENSSH PRIVATE KEY-----\nSYNTHETIC\n')
  self.assertTrue(errors);self.assertNotIn('SYNTHETIC',str(errors))
 def test_force_tracked_ignored_secret_is_rejected(self):
  import subprocess
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);subprocess.run(['git','init',str(root)],capture_output=True,check=True)
   p=root/'.superpowers/auth.json';p.parent.mkdir();p.write_text('private fixture')
   subprocess.run(['git','-C',str(root),'add','-f','.superpowers/auth.json'],check=True)
   self.assertTrue(importlib.import_module('validate').validate_public(root))
