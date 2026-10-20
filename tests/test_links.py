import importlib, sys, tempfile, unittest, json, os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
class LinksTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  t=Path(self.tmp.name).resolve();self.repo=t/'clone with spaces';self.home=t/'home with spaces';self.home.mkdir();self.repo.mkdir();(self.repo/'scripts').mkdir()
  (self.repo/'.zshrc').write_text('new shell');(self.repo/'.aliases').write_text('aliases')
  (self.repo/'docs').mkdir();(self.repo/'docs/private').write_text('never link')
  (self.repo/'.stow-local-ignore').write_text(r'^/(?!\.zshrc$|\.aliases$).*'+'\n')
  (self.repo/'scripts/managed-files.json').write_text(json.dumps([{'package':'.','source':n,'target':n} for n in ['.zshrc','.aliases']]))
 def api(self):return importlib.import_module('links')
 def apply(self,**kw):return self.api().apply_links(self.repo,self.home,self.home/'backups',**kw)
 def test_clone_and_home_with_spaces(self):
  self.apply();self.assertEqual((self.home/'.zshrc').resolve(),self.repo/'.zshrc')
 def test_root_package_links_only_allowlist(self):
  self.apply();self.assertFalse((self.home/'docs').exists());self.assertFalse((self.home/'scripts').exists())
 def test_divergent_file_is_preserved_without_decision(self):
  (self.home/'.zshrc').write_text('mine')
  with self.assertRaises(ValueError):self.apply()
  self.assertEqual((self.home/'.zshrc').read_text(),'mine');self.assertFalse((self.home/'.aliases').exists())
 def test_foreign_symlink_not_followed(self):
  ext=self.home.parent/'external';ext.write_text('private');(self.home/'.zshrc').symlink_to(ext)
  with self.assertRaises(ValueError):self.apply()
  self.assertEqual(ext.read_text(),'private')
 def test_second_apply_is_unchanged(self):
  self.apply();before=os.readlink(self.home/'.zshrc');self.apply();self.assertEqual(os.readlink(self.home/'.zshrc'),before)
 def test_restore_after_partial_failure(self):
  (self.home/'.zshrc').write_text('mine')
  # A failed Stow operation is an external failure, not a test-only production hook.
  from unittest.mock import patch
  with patch('links.subprocess.run',side_effect=RuntimeError('stow interrupted')):
   with self.assertRaises(RuntimeError):self.apply(replace=True)
  journal=next((self.home/'backups').glob('*/journal.json'))
  self.api().restore_run(journal);self.assertEqual((self.home/'.zshrc').read_text(),'mine')
 def test_traversal_rejected(self):
  (self.repo/'scripts/managed-files.json').write_text('[{"package":".","source":".zshrc","target":"../outside"}]')
  with self.assertRaises(ValueError):self.apply()
 def test_restore_refuses_later_changes(self):
  journal=self.apply();(self.home/'.zshrc').unlink();(self.home/'.zshrc').write_text('later')
  with self.assertRaises(ValueError):self.api().restore_run(journal)
  self.assertEqual((self.home/'.zshrc').read_text(),'later')
