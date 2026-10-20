#!/usr/bin/env python3
"""Read-only plan shared by bootstrap and doctor."""
import argparse,importlib.util,json,shutil,sys
from pathlib import Path
from links import plan_links
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def safe_value(value):
 if isinstance(value,(bytes,bytearray)):return f'<binary: {len(value)} bytes>'
 if isinstance(value,list):return f'<array: {len(value)} items>'
 if isinstance(value,dict):return f'<dictionary: {len(value)} keys>'
 return value

def build_plan(repo,home,stages,modules,prefs=None,handlers=None):
 repo=Path(repo).resolve();home=Path(home).absolute()
 plan={'repo':str(repo),'home':str(home),'stages':stages,'modules':modules,'apps':[],'links':[],'preferences':[],'icons':[],'handlers':[],'notes':[]}
 if 'apps' in stages:
  plan['apps']=[str(repo/'Brewfile')]+[str(repo/'modules'/name/'Brewfile') for name in modules]
 if 'shell' in stages:
  plan['links']=[{k:i[k] for k in ['package','source','target','action']} for i in plan_links(repo,home)]
 if 'macos' in stages:
  prefs=prefs or load('macos-preferences').DefaultsBackend()
  if not shutil.which('defaults') and not hasattr(prefs,'values'):plan['notes'].append('defaults unavailable: current preferences unknown')
  else:
   for item in json.loads((repo/'macos/preferences/defaults.json').read_text()):
    exists,current=prefs.get(item['domain'],item['key'])
    plan['preferences'].append({'domain':item['domain'],'key':item['key'],'exists':exists,'current':safe_value(current),'desired':safe_value(item['value']),'change':not exists or current!=item['value'] or type(current) is not type(item['value'])})
 if 'visual' in stages:
  for item in json.loads((repo/'macos/folder-icons.json').read_text()):
   target=home/item['folder'];asset=repo/'macos'/item['icon']
   plan['icons'].append({'folder':str(target),'icon':str(asset),'create_folder':not target.exists(),'asset_exists':asset.is_file()})
  handlers=handlers or (load('default-apps').DutiHandlers() if shutil.which('duti') else None)
  for ext in json.loads((repo/'macos/default-apps.json').read_text()):
   current=handlers.get(ext) if handlers else None
   plan['handlers'].append({'extension':ext,'current':current,'desired':'com.sublimetext.4','change':current!='com.sublimetext.4'})
 return plan

def format_plan(plan):
 lines=[f'Repository: {plan["repo"]}',f'Target: {plan["home"]}','Stages: '+', '.join(plan['stages'])]
 for file in plan['apps']:lines.append('Brewfile: '+file)
 for item in plan['links']:lines.append(f"{item['action']}: {item['target']}")
 for item in plan['preferences']:
  before=repr(item['current']) if item['exists'] else '<unset>'
  lines.append(f"{'change' if item['change'] else 'unchanged'}: {item['domain']}.{item['key']}: {before} -> {item['desired']!r}")
 for item in plan['icons']:lines.append(f"icon: {item['folder']} <- {item['icon']} (create folder: {item['create_folder']}, asset exists: {item['asset_exists']})")
 for item in plan['handlers']:lines.append(f"{'change' if item['change'] else 'unchanged'}: .{item['extension']}: {item['current'] or '<unknown>'} -> {item['desired']}")
 return '\n'.join(lines+plan['notes'])

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['apps','shell','macos','visual','all'],default='all');p.add_argument('--module',action='append',choices=['personal','development','security','cloud','media'],default=[]);p.add_argument('--target',type=Path,default=Path.home());p.add_argument('--json',action='store_true');a=p.parse_args()
 stages=['apps','shell','macos','visual'] if a.stage=='all' else [a.stage]
 plan=build_plan(ROOT,a.target,stages,a.module);print(json.dumps(plan,indent=2) if a.json else format_plan(plan))
if __name__=='__main__':
 try:main()
 except (OSError,ValueError) as error:print(error,file=sys.stderr);sys.exit(1)
