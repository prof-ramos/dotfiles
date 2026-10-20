#!/usr/bin/env python3
import argparse,base64,json,plistlib,subprocess,sys,time,uuid
from pathlib import Path
from state import private_dir,write_json
ROOT=Path(__file__).resolve().parents[1]
class MemoryBackend:
 def __init__(self,values):self.values=values.copy()
 def get(self,domain,key):return (key in [k for d,k in self.values if d==domain],self.values.get((domain,key)))
 def set(self,domain,key,value):self.values[domain,key]=value
 def delete(self,domain,key):self.values.pop((domain,key),None)
class DefaultsBackend:
 def get(self,domain,key):
  r=subprocess.run(['defaults','export',domain,'-'],capture_output=True)
  if r.returncode:return False,None
  data=plistlib.loads(r.stdout);return key in data,data.get(key)
 def set(self,domain,key,value):
  if isinstance(value,bool):args=['-bool','true' if value else 'false']
  elif isinstance(value,int):args=['-int',str(value)]
  elif isinstance(value,float):args=['-float',str(value)]
  elif isinstance(value,str):args=['-string',value]
  elif isinstance(value,(list,dict)):args=[plistlib.dumps(value,fmt=plistlib.FMT_XML).decode()]
  else:raise ValueError('Unsupported defaults value')
  subprocess.run(['defaults','write',domain,key,*args],check=True)
 def delete(self,domain,key):
  if self.get(domain,key)[0]:subprocess.run(['defaults','delete',domain,key],check=True)

def verify_preferences(items,backend):
 differences=[]
 for item in items:
  exists,current=backend.get(item['domain'],item['key'])
  if not exists or current!=item['value'] or type(current) is not type(item['value']):
   differences.append({'domain':item['domain'],'key':item['key'],'current':current,'desired':item['value'],'exists':exists})
 return differences

def reload_components(items):
 if any(i['domain']=='com.apple.dock' for i in items):
  subprocess.run(['killall','Dock'],capture_output=True,check=False)

def describe_value(value):
 if isinstance(value,bytes):return f'<{len(value)} bytes>'
 if isinstance(value,(list,dict)):return f'<{type(value).__name__}: {len(value)} items>'
 return repr(value)

def print_differences(items):
 print('Preference changes:',len(items))
 for item in items:
  before=describe_value(item['current']) if item['exists'] else '<unset>'
  print(f"{item['domain']}.{item['key']}: {before} -> {describe_value(item['desired'])}")

def apply_preferences(items,backend,state_dir,dry=False):
 changes=[]
 for item in items:
  exists,value=backend.get(item['domain'],item['key'])
  if not exists or value!=item['value'] or type(value) is not type(item['value']):changes.append(dict(item,existed=exists,previous_plist=base64.b64encode(plistlib.dumps(value)).decode() if exists else None,status='prepared'))
 if dry:
  print_differences(verify_preferences(items,backend));return None
 run=private_dir(Path(state_dir)/('preferences-'+uuid.uuid4().hex));journal=run/'preferences.json';write_json(journal,changes)
 for item in changes:
  backend.set(item['domain'],item['key'],item['value']);item['status']='applied';write_json(journal,changes)
 if isinstance(backend,DefaultsBackend) and changes:reload_components(changes)
 # Read after mutation/reload: defaults accepting a write is not completion.
 for attempt in range(20):
  remaining=verify_preferences(items,backend)
  if not remaining:break
  if not isinstance(backend,DefaultsBackend):break
  time.sleep(0.1)
 if remaining:
  print_differences(remaining)
  raise RuntimeError(f'Preferences did not persist; backup: {journal}')
 print('Preferences journal:',journal);return journal

def restore_preferences(journal,backend):
 journal=Path(journal);items=json.loads(journal.read_text())
 for item in reversed(items):
  now=backend.get(item['domain'],item['key'])
  previous=plistlib.loads(base64.b64decode(item['previous_plist'])) if item['existed'] else None
  if now[0]==item['existed'] and (not now[0] or (type(now[1]) is type(previous) and now[1]==previous)):continue
  if not now[0] or type(now[1]) is not type(item['value']) or now[1]!=item['value']:raise ValueError('Preference changed after application')
  if item['existed']:backend.set(item['domain'],item['key'],previous)
  else:backend.delete(item['domain'],item['key'])
  item['status']='restored';write_json(journal,items)

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['diff','apply','restore','verify']);p.add_argument('--journal',type=Path);p.add_argument('--reload',action='store_true',help='Reload Dock before verification');a=p.parse_args();b=DefaultsBackend()
 if a.action=='verify':
  items=json.loads((ROOT/'macos/preferences/defaults.json').read_text())
  if a.reload:reload_components(items)
  differences=verify_preferences(items,b);print_differences(differences)
  if differences:raise RuntimeError('Preference drift detected')
 elif a.action=='restore':
  if not a.journal:p.error('--journal required')
  restore_preferences(a.journal,b)
 else:apply_preferences(json.loads((ROOT/'macos/preferences/defaults.json').read_text()),b,Path.home()/'Library/Application Support/dotfiles/backups',dry=a.action=='diff')
if __name__=='__main__':
 try:main()
 except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError) as e:print(e,file=sys.stderr);sys.exit(1)
