#!/usr/bin/env python3
"""Read-only environment and drift report; never installs or reloads apps."""
import argparse,json,shutil,subprocess,sys
from pathlib import Path
from preview import ROOT,build_plan,format_plan,load

def diagnose(repo,home,skill_roots=None):
 tools={name:shutil.which(name) for name in ['git','zsh','stow','swift','swiftc','gitleaks','duti','brew','codex','subl']}
 skills=load('skill-doctor');skill_report=skills.inspect_skills(skill_roots if skill_roots is not None else skills.default_roots())
 branch=subprocess.run(['git','-C',str(repo),'branch','--show-current'],capture_output=True,text=True)
 report={'repo':str(repo),'branch':branch.stdout.strip(),'tools':tools,'skills':skill_report,'plan':build_plan(repo,home,['shell','macos','visual'],[])}
 report['healthy']=all(tools.values()) and not skill_report['missing'] and not skill_report['cycles'] and all(i['action']=='unchanged' for i in report['plan']['links']) and not any(i['change'] for i in report['plan']['preferences']+report['plan']['handlers']) and all(i['asset_exists'] and not i['create_folder'] for i in report['plan']['icons'])
 return report

def main():
 p=argparse.ArgumentParser();p.add_argument('--target',type=Path,default=Path.home());p.add_argument('--json',action='store_true');p.add_argument('--skill-roots',type=Path,nargs='+');a=p.parse_args();r=diagnose(ROOT,a.target,a.skill_roots)
 if a.json:print(json.dumps(r,indent=2))
 else:
  print(f'Repository: {r["repo"]} ({r["branch"]})')
  print('Tools missing: '+(', '.join(k for k,v in r['tools'].items() if not v) or 'none'))
  print('Skill routes: '+('OK' if not r['skills']['missing'] and not r['skills']['cycles'] else 'check scripts/skill-doctor.py'))
  print(format_plan(r['plan']))
  print('Status: '+('OK' if r['healthy'] else 'differences or prerequisites require review'))
 return 0 if r['healthy'] else 1
if __name__=='__main__':
 try:sys.exit(main())
 except (OSError,ValueError) as error:print(error,file=sys.stderr);sys.exit(1)
