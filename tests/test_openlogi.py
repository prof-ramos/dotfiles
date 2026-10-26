import importlib.util
import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('openlogi_settings', ROOT / 'scripts/openlogi-settings.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)

CONFIG = '''schema_version = 7
# keep this preference
[app_settings]
appearance = "dark"
[devices."test-keyboard".identity]
kind = "keyboard"
[devices."test-keyboard".identity.model_info]
model_ids = [45943, 0, 0]
[devices."test-mouse".identity]
kind = "mouse"
[devices."test-mouse".identity.model_info]
model_ids = [45105, 0, 0]
[devices."test-mouse".bindings]
Back = { CustomShortcut = "Alt+Left" }
Forward = "Copy"
'''


class OpenLogiTests(unittest.TestCase):
    def recipe(self):
        return json.loads((ROOT / 'macos/openlogi.json').read_text())

    def test_merge_preserves_other_settings_and_is_idempotent(self):
        result = api.prepare(CONFIG, self.recipe())
        data = tomllib.loads(result)
        self.assertFalse(data['devices']['test-keyboard']['fn_lock'])
        self.assertEqual(data['devices']['test-keyboard']['bindings'], {
            'KeySearch': {'CustomShortcut': 'F5'}, 'KeyEmoji': {'CustomShortcut': 'F8'}})
        self.assertEqual(data['devices']['test-mouse']['bindings']['Back'], {'CustomShortcut': 'Ctrl+R'})
        self.assertEqual(data['devices']['test-mouse']['bindings']['Forward'], 'Copy')
        self.assertIn('# keep this preference', result)
        self.assertEqual(data['app_settings']['appearance'], 'dark')
        self.assertEqual(api.prepare(result, self.recipe()), result)

    def test_missing_and_ambiguous_devices_refuse(self):
        for source in [CONFIG.replace('45105', '99999'), CONFIG + '\n[devices.duplicate.identity]\nkind="mouse"\n[devices.duplicate.identity.model_info]\nmodel_ids=[45105]\n']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                api.prepare(source, self.recipe())

    def test_invalid_toml_refuses(self):
        with self.assertRaises(ValueError):
            api.prepare(CONFIG + '\nbroken=[', self.recipe())

    def test_updates_existing_action_tables_and_multiline_values(self):
        source = CONFIG.replace('Back = { CustomShortcut = "Alt+Left" }\n', '').replace('model_ids = [45943, 0, 0]', 'model_ids = [\n45943, # model\n0, 0,\n]')
        source += '\n[devices."test-mouse".bindings.Back]\nCustomShortcut = "Alt+Left"\n'
        source += '\n[devices."test-keyboard".bindings.KeySearch]\nCustomShortcut = "F2"\n'
        result = api.prepare(source, self.recipe())
        self.assertEqual(tomllib.loads(result)['devices']['test-mouse']['bindings']['Back'], {'CustomShortcut': 'Ctrl+R'})
        self.assertEqual(api.prepare(result, self.recipe()), result)
        self.assertNotIn('{ "CustomShortcut"', result)

    def test_apply_backup_idempotence_restore_and_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td).resolve()
            path = home / 'config.toml'
            path.write_text(CONFIG)
            journal = api.apply(path, self.recipe(), home / 'backups')
            self.assertIsNotNone(journal)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertIsNone(api.apply(path, self.recipe(), home / 'backups'))
            api.restore(path, journal)
            self.assertEqual(path.read_text(), CONFIG)
            journal = api.apply(path, self.recipe(), home / 'backups')
            path.write_text(path.read_text() + '\n# later edit\n')
            with self.assertRaises(ValueError):
                api.restore(path, journal)

    def test_refuses_symlink_and_busy_config(self):
        import fcntl
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'config.toml'
            target = Path(td) / 'target'
            target.write_text(CONFIG)
            path.symlink_to(target)
            with self.assertRaises(ValueError):
                api.apply(path, self.recipe(), Path(td) / 'backups')
            path.unlink()
            path.write_text(CONFIG)
            with path.with_name('config.toml.lock').open('a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaises(BlockingIOError):
                    api.apply(path, self.recipe(), Path(td) / 'backups')
