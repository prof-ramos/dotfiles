#!/usr/bin/env python3
"""Validate installed router skills and their invocation dependencies."""
import argparse,json,re,sys
from pathlib import Path
ROUTE=re.compile(r'''Call\s+the\s+Skill\s+tool\s+with\s+["'`]([\w:-]+)["'`]''',re.I)
def inspect_skills(roots):
    skills={}
    for root in roots:
        for path in sorted(Path(root).glob('*/SKILL.md')):
            skills.setdefault(path.parent.name,path)
    routes={name:ROUTE.findall(path.read_text()) for name,path in skills.items()}
    missing=[{'skill':name,'dependency':target} for name,targets in routes.items() for target in targets if target not in skills]
    cycles=[];done=set()
    def visit(name,stack):
        if name in stack:
            cycle=stack[stack.index(name):]+[name]
            if cycle not in cycles:cycles.append(cycle)
            return
        if name in done:return
        for target in routes.get(name,[]):visit(target,stack+[name])
        done.add(name)
    for name in routes:visit(name,[])
    return {'skills':sorted(skills),'routes':routes,'missing':missing,'cycles':cycles}
def default_roots():return [Path.home()/'.agents/skills',Path.home()/'.codex/skills']
def main():
    p=argparse.ArgumentParser();p.add_argument('--roots',nargs='+',type=Path);p.add_argument('--json',action='store_true');a=p.parse_args();result=inspect_skills(a.roots or default_roots())
    if a.json:print(json.dumps(result,indent=2))
    else:
        print(f'Installed skills inspected: {len(result["skills"])}')
        for item in result['missing']:print(f'Missing: {item["skill"]} → {item["dependency"]}')
        for cycle in result['cycles']:print('Cycle: '+' → '.join(cycle))
        if not result['missing'] and not result['cycles']:print('Router dependencies: OK')
    return int(bool(result['missing'] or result['cycles']))
if __name__=='__main__':sys.exit(main())
