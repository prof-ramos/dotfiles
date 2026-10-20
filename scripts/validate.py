#!/usr/bin/env python3
"""Reject unreviewed files and credential material without echoing contents."""
import argparse,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def validate_public(repo:Path)->list[str]:
    allow=set(json.loads((ROOT/'scripts/public-files.json').read_text()))
    errors=[]
    for path in repo.rglob('*'):
        rel=path.relative_to(repo).as_posix()
        if any(p in ('.git','.superpowers','__pycache__') for p in path.relative_to(repo).parts):continue
        if path.is_symlink():errors.append('Symlink source forbidden: '+rel);continue
        if not path.is_file():continue
        if rel not in allow:errors.append('Unreviewed file: '+rel)
        if path.suffix=='.icns':continue
        raw=path.read_text(errors='replace')
        if re.search(r'-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{20,}|\bgh[pousr]_[A-Za-z0-9]{20,}',raw):
            errors.append('Credential-like content: '+rel)
    return errors

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=ROOT);a=p.parse_args()
    errors=validate_public(a.repo)
    if errors:print('\n'.join(errors),file=sys.stderr);return 1
    from links import plan_links
    import tempfile
    with tempfile.TemporaryDirectory() as td:plan_links(a.repo,Path(td).resolve())
    print('Public files and link manifest validated');return 0
if __name__=='__main__':sys.exit(main())
