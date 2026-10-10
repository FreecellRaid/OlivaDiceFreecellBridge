"""Use Logger's existing public link prefix; no message interception or uploads."""
import importlib
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

VERSION = '1.0.3'
DEFAULT_EDITOR_URL = 'https://freecellraid.github.io/Freecell-log-studio/'
CONFIG_PATH = Path('plugin/data/OlivaDiceFreecellBridge/config.json')


def editor_prefix(editor_url):
    if not isinstance(editor_url, str):
        raise ValueError('editor_url 必须是字符串')
    parsed = urlsplit(editor_url.strip())
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment):
        raise ValueError('editor_url 必须是无账号、查询参数和片段的 HTTPS 页面地址')
    # Logger already percent-encodes the complete log identifier.
    # Freecell supports #2- for both completed logs and _temp logs.
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path or '/', '', '2-'))


def configure(Proc):
    try:
        config = {'enabled': True, 'editor_url': DEFAULT_EDITOR_URL}
        if CONFIG_PATH.exists():
            value = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
            if not isinstance(value, dict):
                raise ValueError('配置必须为 JSON 对象')
            config.update(value)
        if type(config['enabled']) is not bool:
            raise ValueError('enabled 必须是布尔值')
        if not config['enabled']:
            Proc.log(2, '[FreecellBridge] 已禁用；保留 Logger 默认链接')
            return False
        prefix = editor_prefix(config['editor_url'])
        logger = importlib.import_module('OlivaDiceLogger')
        logger.data.dataLogPainterUrl = prefix
        Proc.log(2, '[FreecellBridge] 日志编辑链接已接入 Freecell Log Studio')
        return True
    except Exception as exc:
        # Optional integration must not interrupt Logger or other plugins.
        Proc.log(3, '[FreecellBridge] 接入失败，保留现有链接：%s' % exc)
        return False


class Event:
    @staticmethod
    def init(plugin_event, Proc):
        pass

    @staticmethod
    def init_after(plugin_event, Proc):
        configure(Proc)
