import os,subprocess,tempfile,unittest,sys,json,pty,shutil
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
   bin=h/'bin';bin.mkdir();fixture=bin/'subl';fixture.write_text('#!/bin/sh\nexit 0\n');fixture.chmod(0o755)
   for flags in ['-lc','-ic']:
    r=subprocess.run(['/bin/zsh',flags,'print -r -- "$EDITOR|$VISUAL"; command -v subl'],env=dict(os.environ,HOME=str(h),ZDOTDIR=str(h),PATH=str(bin)+':'+os.environ['PATH']),capture_output=True,text=True)
    self.assertEqual(r.returncode,0,r.stderr);self.assertIn('subl -w|subl -w',r.stdout);self.assertTrue(r.stdout.strip().endswith('/subl'),r.stdout)

class ShellStartupTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('zsh'), 'zsh is required')
    def test_theme_loads_when_instant_prompt_redirects_stdout(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            repo = Path(__file__).resolve().parents[1]
            shutil.copyfile(repo / '.zshrc', home / '.zshrc')
            (home / '.exports').write_text('export ZSH="$HOME/omz"\n')
            (home / '.aliases').touch()
            (home / '.functions').touch()
            (home / '.p10k.zsh').write_text('typeset -g AUDIT_THEME_CONFIG=loaded\n')
            (home / 'omz').mkdir()
            (home / 'omz/oh-my-zsh.sh').write_text(
                '[[ -z $ZSH_THEME ]] || function p10k() { :; }\n')
            cache = home / '.cache'
            cache.mkdir()
            # Real instant prompt saves the descriptors and redirects stdout
            # before the rest of .zshrc runs. Reproduce that boundary here.
            (cache / f'p10k-instant-prompt-{os.environ["USER"]}.zsh').write_text(
                'exec 1>"$HOME/instant-output"\n')
            master, slave = pty.openpty()
            try:
                env = dict(os.environ, HOME=td, XDG_CACHE_HOME=str(cache),
                           HOMEBREW_PREFIX=td, PATH='/usr/bin:/bin',
                           _DOTFILES_EXPORTS_LOADED='')
                env.pop('ZDOTDIR', None)
                env.pop('GHOSTTY_RESOURCES_DIR', None)
                subprocess.run(['zsh', '-ic',
                    'print -r -- "${+functions[p10k]}:$AUDIT_THEME_CONFIG" > "$HOME/result"'],
                    env=env, stdin=slave, stdout=slave, stderr=slave,
                    timeout=10, check=True)
            finally:
                os.close(slave)
                os.close(master)
            self.assertEqual((home / 'result').read_text().strip(), '1:loaded')
