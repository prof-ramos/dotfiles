#!/usr/bin/env python3
"""Plan, apply and restore only explicitly declared Stow files."""
import argparse, difflib, json, os, subprocess, sys, uuid
from pathlib import Path
from state import fingerprint, private_dir, save_backup, restore_entry, write_json

def safe_relative(value):
    p=Path(value)
    if not value or p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe relative path')
    return p

def no_symlink_parents(path,root):
    if root.is_symlink():raise ValueError(f'Symlink root: {root}')
    for p in path.relative_to(root).parents:
        if (root/p).is_symlink():raise ValueError(f'Symlink parent: {root/p}')

def plan_links(repo:Path,target:Path)->list[dict]:
    repo=Path(repo).absolute();target=Path(target).absolute()
    entries=json.loads((repo/'scripts/managed-files.json').read_text());out=[];seen=set()
    for item in entries:
        package=item['package'];src=safe_relative(item['source']);dst=safe_relative(item['target'])
        if package!='.':safe_relative(package)
        source=repo/package/src;dest=target/dst
        if src!=dst:raise ValueError('Stow source and target must match')
        if str(dst) in seen:raise ValueError('Duplicate target')
        seen.add(str(dst));no_symlink_parents(dest,target)
        no_symlink_parents(source,repo)
        if source.is_symlink() or not source.is_file():raise ValueError(f'Invalid source: {source}')
        if dest.is_symlink() and dest.resolve()==source.resolve():action='unchanged'
        elif dest.exists() or dest.is_symlink():action='conflict'
        else:action='link'
        out.append(dict(item,source_path=str(source),target_path=str(dest),action=action))
    return out

def apply_links(repo,target,state_dir,replace=False):
    repo=Path(repo).absolute();target=Path(target).absolute();plan=plan_links(repo,target)
    conflicts=[p for p in plan if p['action']=='conflict']
    if conflicts and not replace:raise ValueError('Conflicts require explicit --replace after reviewing plan')
    import re
    run=private_dir(Path(state_dir)/uuid.uuid4().hex);journal=run/'journal.json'
    data={'target':str(target),'repo':str(repo),'entries':[]}
    write_json(journal,data)
    changed=[item for item in plan if item['action']!='unchanged']
    for item in changed:
        dest=Path(item['target_path']);entry=save_backup(dest,run)
        entry['mode']=dest.stat().st_mode & 0o777 if dest.is_file() and not dest.is_symlink() else 0o600
        entry['expected']={'kind':'symlink','link':os.path.relpath(item['source_path'],dest.parent)}
        data['entries'].append(entry);write_json(journal,data)
        if dest.is_file() or dest.is_symlink():dest.unlink()
        dest.parent.mkdir(parents=True,exist_ok=True)
    for package in dict.fromkeys(item['package'] for item in changed):
        allowed=set()
        for item in plan:
            if item['package']==package:
                rel=Path(item['source']);allowed.add(str(rel));allowed.update(str(p) for p in rel.parents if str(p)!='.')
        ignore='^/(?!(?:'+'|'.join(re.escape(v)+'$' for v in sorted(allowed))+')).*'
        directory=repo.parent if package=='.' else repo
        name=repo.name if package=='.' else package
        subprocess.run(['stow','--no-folding','--ignore',ignore,'--dir',str(directory),'--target',str(target),name],check=True)
        for entry in data['entries']:
            dest=Path(entry['target'])
            if dest.is_symlink() and fingerprint(dest)==entry['expected']:
                entry['status']='applied';write_json(journal,data)
    for entry in data['entries']:
        if fingerprint(Path(entry['target']))!=entry['expected']:raise RuntimeError('Stow target missing or unexpected')
    print(f'Links journal: {journal}')
    return journal

def restore_run(journal):
    journal=Path(journal);data=json.loads(journal.read_text());root=Path(data['target'])
    for entry in reversed(data['entries']):
        dest=Path(entry['target']);no_symlink_parents(dest,root)
        restore_entry(entry);write_json(journal,data)

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['plan','apply','restore']);p.add_argument('--target',type=Path,default=Path.home());p.add_argument('--replace',action='store_true');p.add_argument('--journal',type=Path);a=p.parse_args()
    repo=Path(__file__).resolve().parents[1]
    if a.action=='restore':
        if not a.journal:p.error('--journal required')
        restore_run(a.journal)
    elif a.action=='plan':
        for item in plan_links(repo,a.target):
            print(item['action'],item['target_path'])
            if item['action']=='conflict' and Path(item['target_path']).is_file():
                old=Path(item['target_path']).read_text(errors='replace').splitlines();new=Path(item['source_path']).read_text().splitlines()
                print('\n'.join(difflib.unified_diff(old,new,fromfile='local',tofile='new')))
    else:apply_links(repo,a.target,a.target/'Library/Application Support/dotfiles/backups',replace=a.replace)
if __name__=='__main__':
    try:main()
    except (ValueError,RuntimeError,OSError,subprocess.CalledProcessError) as e:print(str(e),file=sys.stderr);sys.exit(1)
