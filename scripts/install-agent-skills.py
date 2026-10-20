#!/usr/bin/env python3
"""Install Matt Pocock skills with their router dependency closure."""
import argparse,re,subprocess,sys
from preview import load

def ensure_skills(names,roots,runner=subprocess.run):
 if not names or any(not re.fullmatch(r'[a-z0-9][a-z0-9-]*',name) for name in names):raise ValueError('Invalid skill name')
 checker=load('skill-doctor');pending=list(names);seen=set();requested=set(names)
 while pending:
  name=pending.pop(0)
  if name in seen:continue
  if not re.fullmatch(r'[a-z0-9][a-z0-9-]*',name):raise ValueError('Unsupported dependency name')
  if len(seen)>=128:raise ValueError('Dependency limit exceeded')
  report=checker.inspect_skills(roots)
  if name in requested or name not in report['skills']:
   runner(['npx','skills','add','mattpocock/skills','--skill',name,'-g','-y'],check=True)
   report=checker.inspect_skills(roots)
  if name not in report['skills']:raise ValueError('Installation missing '+name)
  seen.add(name);pending.extend(report['routes'].get(name,[]))
 report=checker.inspect_skills(roots)
 if any(i['skill'] in seen for i in report['missing']) or any(set(c)&seen for c in report['cycles']):raise ValueError('Missing or cyclic router dependency')
 return sorted(seen)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('skills',nargs='+');args=parser.parse_args();checker=load('skill-doctor');print('Ready: '+', '.join(ensure_skills(args.skills,checker.default_roots())))
if __name__=='__main__':
 try:main()
 except (OSError,ValueError,subprocess.CalledProcessError) as error:print(error,file=sys.stderr);sys.exit(1)
