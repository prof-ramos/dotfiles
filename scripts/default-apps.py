#!/usr/bin/env python3
"""Set declared per-extension applications; preserve previous handlers."""
import argparse,json,subprocess,sys,time,uuid
from pathlib import Path
from state import private_dir,write_json
ROOT=Path(__file__).resolve().parents[1]
BUNDLE='com.sublimetext.4'
def handler_targets(extensions):
 return extensions if isinstance(extensions,dict) else dict.fromkeys(extensions,BUNDLE)
class MemoryHandlers:
 def __init__(self,values):self.values=values.copy()
 def get(self,ext):return self.values.get(ext)
 def set(self,ext,bundle):self.values[ext]=bundle
 def available(self,bundle):return True
class DutiHandlers:
 def available(self,bundle):
  # Resolve through Launch Services without launching the destination app.
  script='ObjC.import("AppKit"); function run(argv) { return Boolean(ObjC.unwrap($.NSWorkspace.sharedWorkspace.URLForApplicationWithBundleIdentifier(argv[0]))); }'
  r=subprocess.run(['osascript','-l','JavaScript','-e',script,bundle],capture_output=True,text=True,check=True,timeout=10)
  return r.stdout.strip()=='true'
 def get(self,ext):
  r=subprocess.run(['duti','-x',ext],capture_output=True,text=True)
  lines=r.stdout.strip().splitlines()
  return lines[-1] if r.returncode==0 and len(lines)>=3 else None
 def set(self,ext,bundle):
  subprocess.run(['duti','-s',bundle,'.'+ext,'all'],check=True)
  # Launch Services publishes the new mapping asynchronously.
  for attempt in range(30):
   if self.get(ext)==bundle:return
   time.sleep(0.1)
  raise RuntimeError('Launch Services did not confirm handler for .'+ext)

def apply_handlers(extensions,backend,state_dir,dry=False):
 records=[]
 for ext,bundle in handler_targets(extensions).items():
  if not ext.isalnum():raise ValueError('Invalid extension')
  if not isinstance(bundle,str) or not bundle.strip():raise ValueError('Invalid application bundle')
  if not backend.available(bundle):raise ValueError('Destination application not installed: '+bundle+'. Install it before applying the visual stage.')
  old=backend.get(ext)
  if not old:raise ValueError('No recoverable current handler for .'+ext)
  if old!=bundle:records.append({'extension':ext,'before':old,'after':bundle,'status':'prepared'})
 if dry:print('Default-app changes:',len(records));return None
 run=private_dir(Path(state_dir)/('apps-'+uuid.uuid4().hex));journal=run/'apps.json';write_json(journal,records)
 for item in records:
  backend.set(item['extension'],item['after']);item['status']='applied';write_json(journal,records)
 print('Default apps journal:',journal);return journal

def restore_handlers(journal,backend):
 journal=Path(journal);records=json.loads(journal.read_text())
 for item in reversed(records):
  now=backend.get(item['extension'])
  if now==item['before']:continue
  if now!=item['after']:raise ValueError('Handler changed after application')
  backend.set(item['extension'],item['before']);item['status']='restored';write_json(journal,records)

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['diff','apply','restore']);p.add_argument('--journal',type=Path);a=p.parse_args();b=DutiHandlers()
 if a.action=='restore':
  if not a.journal:p.error('--journal required')
  restore_handlers(a.journal,b)
 else:apply_handlers(json.loads((ROOT/'macos/default-apps.json').read_text()),b,Path.home()/'Library/Application Support/dotfiles/backups',dry=a.action=='diff')
if __name__=='__main__':
 try:main()
 except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError) as e:print(e,file=sys.stderr);sys.exit(1)
