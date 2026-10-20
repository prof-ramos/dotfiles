import os,subprocess,tempfile,unittest,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from links import apply_links
REPO=Path(__file__).resolve().parents[1]
class SetupTests(unittest.TestCase):
 def test_full_plan_is_read_only(self):
  with tempfile.TemporaryDirectory() as td:
   t=Path(td).resolve();env=dict(os.environ,HOME=str(t))
   r=subprocess.run(['/bin/zsh','-f',str(REPO/'bootstrap.sh'),'--stage','all','--dry-run'],env=env,capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(list(t.iterdir()),[])
 def test_twice_applied_temp_home_has_stable_links(self):
  with tempfile.TemporaryDirectory() as td:
   h=Path(td).resolve();apply_links(REPO,h,h/'backups')
   before={p.relative_to(h).as_posix():os.readlink(p) for p in h.rglob('*') if p.is_symlink()}
   apply_links(REPO,h,h/'backups');after={p.relative_to(h).as_posix():os.readlink(p) for p in h.rglob('*') if p.is_symlink()}
   self.assertEqual(before,after);self.assertIn('.zshrc',after);self.assertFalse((h/'docs').exists())
 def test_editor_available_in_login_and_interactive_shell(self):
  with tempfile.TemporaryDirectory() as td:
   h=Path(td).resolve();apply_links(REPO,h,h/'backups')
   for flags in ['-lc','-ic']:
    r=subprocess.run(['/bin/zsh',flags,'print -r -- "$EDITOR|$VISUAL"; command -v subl'],env=dict(os.environ,HOME=str(h),ZDOTDIR=str(h)),capture_output=True,text=True)
    self.assertEqual(r.returncode,0,r.stderr);self.assertIn('subl -w|subl -w',r.stdout);self.assertIn('Sublime Text.app',r.stdout)
