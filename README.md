# OlivaDiceFreecellBridge

青果骰插件，把 OlivaDiceLogger 返回的日志链接替换为 [Freecell-Log-Studio](https://freecellraid.github.io/Freecell-log-studio/)
在 `.log end` 上传完成后，群内返回替换后的编辑器链接，并可进一步编辑。
`.log upload` 和 `.log temp` 等同样使用编辑器链接。

## 安装

依赖 OlivaDiceCore 和 OlivaDiceLogger。
将 `OlivaDiceFreecellBridge/` 文件夹复制到机器人数据目录的 `plugin/app/`，然后在客户端重载插件即可装载。  
也可运行 `python3 tools/build.py`，将生成的 OPK 安装到 `plugin/app/`。

默认编辑器为 `https://freecellraid.github.io/Freecell-log-studio/`。
通常不需要配置。如需自托管，把 `config.example.json` 复制到
`plugin/data/OlivaDiceFreecellBridge/config.json`，设置 `editor_url` 后重载插件。
URL 应为支持机器人日志导入的 HTTPS 编辑器页面地址，不带查询参数或 hash。
禁用可设置 `enabled: false` 后重载插件；卸载可移走插件目录再重载。

## 实现与限制

插件优先级为 20040，Logger 为 20030。`init_after` 在每次启动和插件重载后设置
`OlivaDiceLogger.data.dataLogPainterUrl`，使用 Freecell-log-studio 支持的 `#2-<已编码日志标识>`。
Logger 原有的消息文本、上传、保存和异常处理继续负责日志流程，链接按钮也会使用同一地址。
配置错误或缺少 Logger 会记入客户端日志，不阻断其他插件。

Freecell-log-studio 是浏览器编辑器，不提供后台编辑、托管或编辑结果回写 API。
编辑在点击链接后进行；机器人不会远程启动用户浏览器。
日志下载依赖青果日志服务器，编辑器需部署支持 `#2-` 自动导入的版本。
超过默认 10 MiB 限制的日志需调整编辑器或拆分导入。

## 验证

`python3 -m unittest discover -s tests -v`

客户端测试依赖可通过 `python3 -m pip install -r requirements-test.txt` 安装；插件本身无额外依赖。
运行 `python3 tools/live_test.py "~/Library/Application Support/OlivaDice" --reload`。
需有本地虚拟终端账号；`--reload` 会重载当前客户端所有插件，应在没有正在处理的指令时使用。
