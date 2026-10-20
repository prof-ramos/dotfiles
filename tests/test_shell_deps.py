import tempfile,subprocess,unittest,os,shutil
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
class DependencyTests(unittest.TestCase):
 def test_foreign_dependency_symlink_never_written(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td).resolve();h=root/'home';outside=root/'outside';h.mkdir();outside.mkdir();(outside/'oh-my-zsh.sh').write_text('# marker')
   (h/'.oh-my-zsh').symlink_to(outside);bin=root/'bin';bin.mkdir()
   sha='4d4cfc287e9d887b81242c0e431b5f49f9cec5c1'
   g=bin/'git';g.write_text('#!/bin/sh\necho '+sha+'\n');g.chmod(0o755)
   r=subprocess.run(['/bin/zsh','-f',str(REPO/'scripts/install-shell-deps.sh'),'--install'],env=dict(os.environ,HOME=str(h),PATH=str(bin)+':'+os.environ['PATH']),capture_output=True,text=True)
   self.assertNotEqual(r.returncode,0);self.assertEqual([p.name for p in outside.iterdir()],['oh-my-zsh.sh'])
