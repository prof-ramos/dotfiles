import os, subprocess, tempfile, unittest
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
class BootstrapTests(unittest.TestCase):
 def run_boot(self,*args,fail=False):
  with tempfile.TemporaryDirectory() as td:
   t=Path(td); bin=t/'bin';bin.mkdir(); log=t/'calls'
   for name in ['brew','xcode-select']:
    f=bin/name; f.write_text('#!/bin/sh\necho "$0 $*" >> "$CALLS"\n'+('exit 9\n' if fail and name=='brew' else 'exit 0\n'));f.chmod(0o755)
   env=dict(os.environ,HOME=td,PATH=str(bin)+':'+os.environ['PATH'],CALLS=str(log))
   r=subprocess.run(['/bin/zsh','-f',str(REPO/'bootstrap.sh'),*args],env=env,capture_output=True,text=True)
   return r,log.read_text() if log.exists() else ''
 def test_help_has_no_effect(self):
  r,c=self.run_boot();self.assertEqual(r.returncode,0,r.stderr);self.assertIn('--stage',r.stdout);self.assertEqual(c,'')
 def test_all_does_not_select_optional_modules(self):
  r,c=self.run_boot('--stage','all','--dry-run');self.assertEqual(r.returncode,0,r.stderr);self.assertNotIn('/modules/',r.stdout);self.assertEqual(c,'')
 def test_invalid_module_fails_before_install(self):
  r,c=self.run_boot('--stage','apps','--module','../../etc');self.assertNotEqual(r.returncode,0);self.assertEqual(c,'')
 def test_apps_failure_stops_later_stages(self):
  r,c=self.run_boot('--stage','all',fail=True);self.assertNotEqual(r.returncode,0);self.assertIn('brew',c);self.assertNotIn('Concluído',r.stdout)
