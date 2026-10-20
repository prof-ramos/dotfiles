"""Private, recoverable records of filesystem operations."""
import hashlib, json, os, shutil, uuid
from pathlib import Path

def fingerprint(path):
    path=Path(path)
    if path.is_symlink(): return {'kind':'symlink','link':os.readlink(path)}
    if path.is_file(): return {'kind':'file','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.exists(): return {'kind':'directory'}
    return {'kind':'absent'}

def private_dir(path):
    path=Path(path)
    for ancestor in [path,*path.parents]:
        if ancestor.is_symlink(): raise ValueError('Symlink in backup path')
    path.mkdir(parents=True,exist_ok=True,mode=0o700);path.chmod(0o700)
    return path

def write_json(path,data):
    path=Path(path);tmp=path.with_name(path.name+'.tmp')
    fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(data,f,indent=2);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def save_backup(path:Path,state_dir:Path)->dict:
    before=fingerprint(path)
    if before['kind']=='directory':raise ValueError(f'Directory conflict: {path}')
    entry={'target':str(path),'before':before,'backup':None,'status':'prepared'}
    if before['kind']=='file':
        dst=private_dir(state_dir)/uuid.uuid4().hex;shutil.copyfile(path,dst);dst.chmod(0o600);entry['backup']=str(dst)
    return entry

def restore_entry(entry:dict)->None:
    path=Path(entry['target']);before=entry['before']
    current=fingerprint(path)
    if current==before:return
    allowed=[{'kind':'absent'}]
    if entry.get('expected'):allowed.append(entry['expected'])
    if current not in allowed:raise ValueError(f'Changed since application: {path}')
    if path.is_symlink() or path.is_file():path.unlink()
    if before['kind']=='file':shutil.copyfile(entry['backup'],path);path.chmod(entry.get('mode',0o600))
    elif before['kind']=='symlink':path.symlink_to(before['link'])
    entry['status']='restored'
