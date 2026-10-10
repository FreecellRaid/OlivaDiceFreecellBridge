"""Test the installed plugin in the running macOS client's virtual terminal."""
import argparse
import asyncio
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import unquote, urlsplit, urlencode
import uuid

import requests
import websockets


async def verify(root, reload_plugins=False):
    listener = json.loads((root / 'data/webui/listen.json').read_text())
    base = 'http://127.0.0.1:%s' % listener['port']
    client = requests.Session()
    client.headers['X-Auth-Token'] = (root / 'conf/webui_token.txt').read_text().strip()
    if reload_plugins:
        response = client.post(base + '/api/plugins/reload', timeout=5)
        response.raise_for_status()
        await asyncio.sleep(4)
    for _ in range(40):
        plugins = client.get(base + '/api/plugins', timeout=5).json()
        if 'OlivaDiceFreecellBridge' in plugins.get('shallow_plugin_data_dict', {}):
            break
        await asyncio.sleep(0.5)
    else:
        raise AssertionError('客户端没有加载 FreecellBridge')
    print('PASS 当前客户端加载桥接插件', flush=True)
    login = client.post(base + '/api/login', timeout=5).json()
    terminals = client.get(base + '/api/terminals', timeout=5).json()['items']
    terminal = next(item for item in terminals if item['model'] == 'virtual_terminal')
    path = '/ws/terminal/%s/%s' % (terminal['model'], terminal['hash'])
    name = 'Freecell桥接测试_' + uuid.uuid4().hex[:8]
    group = str(900000000 + int(uuid.uuid4().hex[:6], 16))
    protocols = ['olivos', 'token.' + login['browser_token']]
    async with websockets.connect(base.replace('http:', 'ws:') + path,
                                  subprotocols=protocols) as socket:
        await socket.recv()

        async def send(command, expected=None, duration=15):
            await socket.send(json.dumps({'data': command, 'user_conf': {
                'user_name': 'Freecell测试调查员', 'user_id': '900001',
                'flag_group': True, 'target_id': group, 'group_role': 'owner'}}))
            replies = []
            deadline = time.monotonic() + duration
            while time.monotonic() < deadline:
                try:
                    packet = json.loads(await asyncio.wait_for(socket.recv(),
                                           min(5, deadline - time.monotonic())))
                except asyncio.TimeoutError:
                    if expected is None:
                        return ''
                    continue
                replies.extend(item for item in packet.get('items', []) if item.get('name') == 'BOT')
                text = '\n'.join(str(item.get('data', item)) for item in replies)
                if expected and expected in text:
                    print('PASS %s: %s' % (command, text[:1000]), flush=True)
                    return text
            raise AssertionError('未收到预期回复 %s: %s' % (command, replies))

        await send('.log new ' + name, '记录')
        await send('推开房门，开始调查。Freecell自动导入测试。', duration=2)
        await send('.r1d1', '=1')
        text = await send('.log end', 'https://freecellraid.github.io/Freecell-log-studio/#2-', 90)
        match = re.search(r'https://freecellraid\.github\.io/Freecell-log-studio/#2-[^\s\]\"\\]+', text)
        assert match, text
        link = match.group(0)
        identifier = unquote(urlsplit(link).fragment[2:])
        assert name in identifier, identifier
        reader = 'https://api.dice.center/dicelogger/logReader.php'
        def read_https(url):
            # macOS curl uses the system trust store; no TLS verification bypass.
            return subprocess.run(['curl', '--fail', '--silent', '--show-error',
                                   '--location', '--max-time', '30', url],
                                  capture_output=True, check=True).stdout.decode('utf-8')
        meta = json.loads(read_https(reader + '?' + urlencode({'m': 'metaData', 'id': identifier})))
        assert meta.get('code') == 0, meta
        redirect = meta.get('redirectDownloadUrl')
        if redirect:
            raw = read_https(redirect)
        else:
            raw = read_https(reader + '?' + urlencode({'m': 'rawData', 'id': identifier}))
        assert '推开房门' in raw, raw[:500]
        print('PASS 编辑器来源 API 可读取刚上传的正文', flush=True)
        # Re-upload uses the same Logger prefix without creating a second log.
        log_uuid = identifier.split('_', 2)[1]
        await send('.log upload ' + log_uuid, link, 90)
    report = {'tested_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
              'client': base, 'virtual_group': group, 'editor_link': link,
              'log_identifier': identifier, 'metadata_code': meta['code'],
              'checks': ['plugin_loaded', 'log_new', 'real_dice_reply',
                         'log_end_editor_link', 'remote_metadata',
                         'remote_body_contains_message', 'log_upload_editor_link']}
    report_path = Path(__file__).resolve().parents[1] / 'live-test-result.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('RESULT ' + link, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--reload', action='store_true')
    args = parser.parse_args()
    asyncio.run(verify(args.root.expanduser().resolve(), args.reload))
