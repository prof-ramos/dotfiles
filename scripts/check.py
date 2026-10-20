#!/usr/bin/env python3
"""One fail-closed entry point for local hooks and CI."""
import argparse,os,shutil,subprocess,sys,tempfile,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run_steps(steps,cwd,log_dir):
    log_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
    for index,(name,command) in enumerate(steps):
        log=log_dir/f'{index:02d}-{name}.log'
        with log.open('w') as output:
            result=subprocess.run(command,cwd=cwd,stdout=output,stderr=subprocess.STDOUT)
        log.chmod(0o600)
        print(f'{name}: {"OK" if result.returncode==0 else "FAIL"}',flush=True)
        if result.returncode:
            print('\n'.join(log.read_text(errors='replace').splitlines()[-45:]),file=sys.stderr)
            print(f'Log: {log}',file=sys.stderr)
            return result.returncode
    print(f'Checks passed. Logs: {log_dir}')
    return 0

def check_staged(repo):
    with tempfile.TemporaryDirectory(prefix='dotfiles-index-') as td:
        snapshot=Path(td).resolve()
        subprocess.run(['git','-C',str(repo),'checkout-index','--all','--prefix',str(snapshot)+os.sep],check=True)
        checker=snapshot/'scripts/check.py'
        if not checker.is_file():raise ValueError('Stage scripts/check.py before enabling the commit hook')
        return subprocess.run([sys.executable,str(checker)],cwd=snapshot).returncode

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--staged',action='store_true');parser.add_argument('--history',action='store_true');args=parser.parse_args()
    if args.staged:return check_staged(ROOT)
    missing=[name for name in ['git','zsh','stow','swift','swiftc','gitleaks'] if not shutil.which(name)]
    if missing:print('Missing check tools: '+', '.join(missing),file=sys.stderr);return 1
    steps=[('public-files',[sys.executable,'scripts/validate.py']),('secrets-tree',['gitleaks','dir','--redact','--no-banner','.'])]
    if args.history:steps.append(('secrets-history',['gitleaks','git','--redact','--no-banner','.']))
    shells=['bootstrap.sh','.zshrc','.zprofile','.zshenv','.aliases','.functions','.exports','.p10k.zsh']+[str(p.relative_to(ROOT)) for p in sorted((ROOT/'scripts').glob('*.sh'))]
    steps.extend((f'zsh-{i}',['zsh','-n',file]) for i,file in enumerate(shells))
    steps+=[('python-syntax',[sys.executable,'-m','compileall','-q','scripts','tests']),('tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'])]
    logs=Path.home()/'.local/state/dotfiles/checks'/uuid.uuid4().hex
    return run_steps(steps,ROOT,logs)
if __name__=='__main__':
    try:sys.exit(main())
    except (OSError,ValueError,subprocess.CalledProcessError) as error:print(error,file=sys.stderr);sys.exit(1)
