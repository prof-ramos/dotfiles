#!/usr/bin/env python3
"""Apply a portable OpenLogi recipe to local device identities, with recovery."""
import argparse
import copy
import datetime
import fcntl
import hashlib
import json
import os
import re
import tempfile
import tomllib
import uuid
from contextlib import contextmanager
from pathlib import Path

from state import fingerprint, private_dir, save_backup, write_json

ROOT = Path(__file__).resolve().parents[1]


def key_literal(value):
    return value if re.fullmatch(r'[A-Za-z0-9_-]+', value) else literal(value)


def literal(value):
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, list):
        return '[' + ', '.join(map(literal, value)) + ']'
    if isinstance(value, dict):
        return '{ ' + ', '.join(literal(k) + ' = ' + literal(v) for k, v in value.items()) + ' }'
    raise ValueError('Unsupported TOML value')


def statements(text):
    """Find complete TOML assignments, including multiline values, and tables."""
    lines = text.splitlines(keepends=True)
    section = ()
    index = 0
    while index < len(lines):
        start = index
        line = lines[index]
        index += 1
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if line.lstrip().startswith('['):
            # Let TOML itself decode quoted keys and dotted table paths.
            node = tomllib.loads(line + '\n__dotfiles_marker__ = true\n')
            path = []
            while '__dotfiles_marker__' not in node:
                if len(node) != 1 or not isinstance(next(iter(node.values())), dict):
                    raise ValueError('Unsupported table form; configuration left unchanged')
                key, node = next(iter(node.items()))
                path.append(key)
            section = tuple(path)
            yield ('table', section, None, start, index)
            continue
        chunk = line
        while True:
            try:
                parsed = tomllib.loads(chunk)
                break
            except tomllib.TOMLDecodeError:
                if index == len(lines):
                    raise ValueError('Unsupported assignment; configuration left unchanged')
                chunk += lines[index]
                index += 1
        if len(parsed) != 1:
            raise ValueError('Unsupported assignment; configuration left unchanged')
        yield ('value', section, next(iter(parsed)), start, index)


def set_value(text, section, key, value):
    lines = text.splitlines(keepends=True)
    records = list(statements(text))
    replacement = f'{key_literal(key)} = {literal(value)}\n'
    for kind, path, name, start, end in records:
        if kind == 'value' and path == section and name == key:
            lines[start:end] = [replacement]
            return ''.join(lines)
    for i, (kind, path, _, start, end) in enumerate(records):
        if kind == 'table' and path == section:
            boundary = next((r[3] for r in records[i + 1:] if r[0] == 'table'), len(lines))
            lines[boundary:boundary] = ['\n' + replacement]
            return ''.join(lines)
    header = '.'.join(map(key_literal, section))
    # Put a newly explicit parent before its children, as OpenLogi's writer does.
    boundary = next((r[3] for r in records if r[0] == 'table' and r[1][:len(section)] == section), len(lines))
    lines[boundary:boundary] = [f'\n[{header}]\n' + replacement + '\n']
    return ''.join(lines)


def set_binding(text, section, button, action):
    # Use ordinary action tables: 0.8.14's writer can damage decorations when
    # converting hand-authored inline actions to tables on a later GUI/CLI save.
    lines = text.splitlines(keepends=True)
    path = section + (button,)
    for kind, table, name, start, end in reversed(list(statements(text))):
        if (table == section and kind == 'value' and name == button) or table[:len(path)] == path:
            del lines[start:end]
    result = ''.join(lines)
    for name, value in action.items():
        result = set_value(result, path, name, value)
    return result


def prepare(text, recipe):
    original = tomllib.loads(text)
    expected = copy.deepcopy(original)
    updates = []
    for rule in recipe['devices']:
        matches = [key for key, device in original.get('devices', {}).items()
                   if device.get('identity', {}).get('kind') == rule['kind']
                   and rule['model_id'] in device.get('identity', {}).get('model_info', {}).get('model_ids', [])]
        if len(matches) != 1:
            raise ValueError(f"Model {rule['model_id']}: expected one known device, found {len(matches)}. Open OpenLogi with both devices connected first.")
        key = matches[0]
        device = expected['devices'][key]
        if 'fn_lock' in rule:
            device['fn_lock'] = rule['fn_lock']
            updates.append((('devices', key), 'fn_lock', rule['fn_lock']))
        for button, action in rule['bindings'].items():
            device.setdefault('bindings', {})[button] = action
            updates.append((('devices', key, 'bindings'), button, action))
    # No-op means no formatting changes, backup or write.
    if expected == original:
        return text
    result = text
    for section, key, value in updates:
        result = set_binding(result, section, key, value) if section[-1] == 'bindings' else set_value(result, section, key, value)
    if tomllib.loads(result) != expected:
        raise ValueError('Unexpected TOML layout; configuration left unchanged')
    return result


@contextmanager
def locked(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('Configuration must be an existing regular file')
    lock_path = path.with_name(path.name + '.lock')
    if lock_path.is_symlink():
        raise ValueError('Lock must not be a symlink')
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def atomic_write(path, data):
    fd, name = tempfile.mkstemp(prefix='.openlogi-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def apply(path, recipe, state_dir):
    with locked(path):
        before = path.read_bytes()
        result = prepare(before.decode(), recipe).encode()
        if result == before:
            return None
        run = private_dir(state_dir / uuid.uuid4().hex)
        entry = save_backup(path, run)
        entry['expected'] = {'kind': 'file', 'sha256': hashlib.sha256(result).hexdigest()}
        journal = run / 'journal.json'
        write_json(journal, entry)
        if path.read_bytes() != before:
            raise ValueError('Configuration changed concurrently; retry after closing OpenLogi')
        atomic_write(path, result)
        entry['status'] = 'applied'
        write_json(journal, entry)
        return journal


def restore(path, journal):
    entry = json.loads(journal.read_text())
    if Path(entry['target']) != path:
        raise ValueError('Journal belongs to another configuration')
    with locked(path):
        current = fingerprint(path)
        if current == entry['before']:
            return
        if current != entry['expected']:
            raise ValueError('Configuration changed since application; refusing to overwrite it')
        before = Path(entry['backup']).read_bytes()
        if hashlib.sha256(before).hexdigest() != entry['before']['sha256']:
            raise ValueError('Backup integrity check failed')
        atomic_write(path, before)
        entry['status'] = 'restored'
        write_json(journal, entry)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'apply', 'restore'])
    config_home = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config')))
    parser.add_argument('--config', type=Path, default=config_home / 'openlogi/config.toml')
    parser.add_argument('--journal', type=Path)
    args = parser.parse_args()
    path = args.config.absolute()
    if args.action == 'restore':
        if not args.journal:
            parser.error('restore requires --journal')
        restore(path, args.journal)
        print('Configuration restored. Reopen OpenLogi to load it.')
        return
    recipe = json.loads((ROOT / 'macos/openlogi.json').read_text())
    if args.action == 'plan':
        before = path.read_text()
        after = prepare(before, recipe)
        print('Changes required: K380s F5/F8 without Fn, other F keys with Fn; LIFT Back = Control+R.' if before != after else 'Already configured.')
    else:
        journal = apply(path, recipe, Path.home() / 'Library/Application Support/dotfiles/backups/openlogi')
        print(f'Backup journal: {journal}' if journal else 'Already configured; no changes.')
        print('Reopen OpenLogi to load saved settings. No hardware write or reload was performed by this script.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(str(error))
