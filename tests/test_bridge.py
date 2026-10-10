import importlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import quote, unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from OlivaDiceFreecellBridge import main


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.logger = SimpleNamespace(data=SimpleNamespace(dataLogPainterUrl='original'))
        self.proc = SimpleNamespace(log=lambda *args: None)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'config.json'
        self.modules = patch.dict(sys.modules, {'OlivaDiceLogger': self.logger})
        self.modules.start()
        self.addCleanup(self.modules.stop)
        self.config = patch.object(main, 'CONFIG_PATH', self.path)
        self.config.start()
        self.addCleanup(self.config.stop)

    def test_end_upload_and_temp_identifiers_round_trip(self):
        main.Event.init_after(None, self.proc)
        for name in ['log_123_调查记录_第1幕', 'log_123_空格 & # + %', 'log_123_记录_temp']:
            link = self.logger.data.dataLogPainterUrl + quote(name)
            self.assertEqual(urlsplit(link).hostname, 'freecellraid.github.io')
            self.assertEqual(unquote(urlsplit(link).fragment[2:]), name)

    def test_init_after_reapplies_after_module_reload(self):
        main.Event.init_after(None, self.proc)
        self.logger.data.dataLogPainterUrl = 'reset by logger reload'
        reloaded = importlib.reload(main)
        with patch.object(reloaded, 'CONFIG_PATH', self.path):
            reloaded.Event.init_after(None, self.proc)
        self.assertEqual(self.logger.data.dataLogPainterUrl,
                         main.DEFAULT_EDITOR_URL + '#2-')

    def test_invalid_disabled_and_missing_logger_do_not_interrupt(self):
        for value in [{'enabled': False}, {'editor_url': 'http://example.com/'},
                      {'enabled': 'false'}, [], {'editor_url': 'https://example.com/#foo'}]:
            self.path.write_text(json.dumps(value))
            self.assertFalse(main.configure(self.proc))
            self.assertEqual(self.logger.data.dataLogPainterUrl, 'original')
        self.path.write_text('{broken')
        self.assertFalse(main.configure(self.proc))
        self.path.unlink()
        with patch.dict(sys.modules, {'OlivaDiceLogger': None}):
            self.assertFalse(main.configure(self.proc))


if __name__ == '__main__':
    unittest.main()
