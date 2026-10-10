# OlivaDiceFreecellBridge

Freecell Log Studio 桥接插件。将青果骰返回的日志链接接入
[Freecell Log Studio](https://freecellraid.github.io/Freecell-log-studio/)，点击后自动导入日志，随后可在浏览器中编辑。

## 基本信息

- 名称：`OlivaDiceFreecellBridge`（Freecell Log Studio 桥接插件）
- 作者：`Freecell`
- 版本：`1.0.0`
- 兼容版本：插件声明最低 OlivOS 构建号为 `190`（`compatible_svn`）；具体发行版本与实际兼容范围待客户端验证确认。
- 平台：理论适用于 OlivaDiceLogger 支持的聊天平台，尚未完成各平台验证。
- 操作系统：插件无操作系统专属逻辑，理论支持 Windows、Linux，尚未完成跨系统验证。
- 依赖：`OlivaDiceCore`、`OlivaDiceLogger`。
- 许可：MIT，见 [LICENSE](LICENSE)。

## 下载与安装

发布附件为 `OlivaDiceFreecellBridge-1.0.0.zip`，内含 OPK、安装说明、配置示例和许可证。
版本附件见 [GitHub Releases](https://github.com/FreecellRaid/OlivaDiceFreecellBridge/releases)。

1. 确认客户端已安装 OlivaDiceCore 和 OlivaDiceLogger。
2. 解压下载包，将 `OlivaDiceFreecellBridge.opk` 放入机器人数据目录的 `plugin/app/`。
3. 在客户端重载插件，或重启客户端。重载会影响当前插件运行，请在空闲时操作。

也可从源码安装：将仓库中的 `OlivaDiceFreecellBridge/` 文件夹复制到 `plugin/app/`，然后重载。
OPK 与源码目录任选一种安装方式，更新时移走旧副本，避免同时安装两个副本。

## 使用方法

继续使用 Logger 原有日志命令，无需新增命令：

1. 使用 `.log new 日志名` 开始记录。
2. 记录完成后发送 `.log end`，等待上传完成。
3. 点击机器人返回的 Freecell Log Studio 链接，在浏览器中导入并编辑日志。

`.log upload` 和 `.log temp` 返回的日志链接也会使用同一编辑器入口；
命令参数、权限和上传规则沿用当前安装的 OlivaDiceLogger。

插件只替换 Logger 的编辑器链接前缀。日志记录、上传、保存、回复文本及异常处理仍由 Logger 负责。

## 配置、禁用与卸载

默认编辑器为 `https://freecellraid.github.io/Freecell-log-studio/`，通常不需要配置。
如需自托管，将 `config.example.json` 复制到
`plugin/data/OlivaDiceFreecellBridge/config.json`，修改 `editor_url` 后重载插件或重启客户端。

`editor_url` 必须为 HTTPS 页面地址，不带账号、查询参数或 hash，且编辑器部署版本需要支持 `#2-` 自动导入。
`enabled` 必须为 JSON 布尔值 `true` 或 `false`。

配置为全局配置，作用于当前客户端的 Logger 共享链接前缀，暂不提供按机器人或群独立切换。
禁用时设置 `enabled: false`；卸载时移走 `plugin/app/` 下的 OPK 或源码目录。
完成禁用或卸载后建议重启客户端，让 Logger 重新初始化链接前缀。
插件数据目录中的配置可按需保留或删除。

## 限制与排查

- Freecell Log Studio 是浏览器编辑器，不提供后台编辑、托管或编辑结果回写 API。
- 日志下载依赖青果日志服务器，使用时需能正常访问编辑器页面及日志服务器。
- 超过编辑器默认 10 MiB 限制的日志需调整编辑器或拆分导入。
- 配置错误或缺少 Logger 时会记入客户端日志，不阻断其他插件；桥接失败时保留现有链接。
- 若返回的仍是原编辑器链接，先确认插件已加载，再检查客户端日志中的 `[FreecellBridge]` 信息。
- 其他修改 Logger 链接前缀的插件可能覆盖本插件的设置。

## 源码与反馈

- [项目源码](https://github.com/FreecellRaid/OlivaDiceFreecellBridge)
- [问题反馈](https://github.com/FreecellRaid/OlivaDiceFreecellBridge/issues)

反馈时请提供插件版本、OlivOS 版本、Core/Logger 版本、操作系统、使用的命令及相关错误信息。

### 自动发布

GitHub Actions 会在推送 `vX.Y.Z` 标签后检查版本、运行单元测试、构建并验证压缩包，
随后自动创建 GitHub Release，附上 OPK 与版本 ZIP，并生成更新说明。
使用仓库自带的 `GITHUB_TOKEN`，无需额外配置密钥。

发布前更新 `OlivaDiceFreecellBridge/app.json` 中的 `version` 和 `svn`，
同步修改 `main.py` 的 `VERSION`、本文及论坛文案中的版本号和附件名。
标签必须与 `app.json` 的版本一致，否则发布会失败。

```sh
git tag v1.0.0
git push origin v1.0.0
```

将包含工作流的修改提交并推送后，在仓库的 Actions 页面查看发布进度。失败后可修复原因并重新运行；
若对应 Release 已存在，工作流会更新同名附件并保留原发布说明。

### 实现与测试

插件优先级为 `20040`，Logger 为 `20030`。`init_after` 在启动或重载后设置
`OlivaDiceLogger.data.dataLogPainterUrl`，使用 Freecell Log Studio 支持的 `#2-<已编码日志标识>`。

单元验证：`python3 -m unittest discover -s tests -v`。
单元测试不能代替真实客户端与各聊天平台的验证。

客户端测试依赖可通过 `python3 -m pip install -r requirements-test.txt` 安装。
运行 `python3 tools/live_test.py "~/Library/Application Support/OlivaDice" --reload`。
需有本地虚拟终端账号；该测试会发送演示指令、上传演示日志，并生成 `live-test-result.json`。
`--reload` 会重载当前客户端所有插件，应在没有正在处理的指令时使用。
