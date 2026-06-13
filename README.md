# headlessBA

`headlessBA` 是一个面向生产环境的 Blue Archive 自动化/服务端基础项目。它从原先偏调试用途的 `ba_replay` 迁移而来，目标是把登录链、主网关发包、运行态 profile、后续游戏内 API 自动化统一到一个高内聚、低耦合、可测试、可扩展的工程结构里。

当前版本优先保留并模块化已有能力：

- Android/mobile Nexon ID 直登 TOYSDK 链路
- Web token / Playwright 登录入口
- 主游戏网关构包、加密、解包、ProofToken、Account_CheckNexon、Account_Auth、Account_LoginSync
- Android runtime/profile 生成与持久化
- NGS-X/NgsmToken Android bridge 辅助脚本
- 登录链 artifact 对比与轻量测试

## 目录结构

```text
headlessBA/
  headlessba/
    core/              # 协议、schema、packet、crypto、gateway client、API registry
    modules/
      auth/            # 登录、TOYSDK、ProofToken、Nexon web token、登录链编排
      runtime/         # Android profile、区域配置、runtime 发现、profile generator
    game/
      player/
        cafe/          # 后续 Cafe API 模块扩展点
    utils/             # 横向工具，例如代理配置
    config/            # 项目路径和设置
    log/               # 标准 logger 配置
    database/          # 后续任务/账号/执行历史持久化入口
  tools/               # 可独立运行的采集/验证工具
  tests/               # 无 pytest 依赖也可直接 python 执行的轻量测试
  docs/architecture/   # 架构约束和开发规范
```

## 快速开始

```powershell
cd D:\gaimo\headlessBA
python -m pip install -r requirements.txt
python main.py --help
```

Android Nexon ID 直登示例：

```powershell
python main.py --mobile-nx-login --nx-id "<email>" --nx-password "<password>" --region tw --turnstile-no-browser --post --timeout 120 --output-dir analysis_reports\nexon_webview_login\android_mobile_nx
```

成功后 CLI 会输出玩家摘要：

```text
[*] Player info: AccountId=... Nickname=... Level=... Exp=... FriendCode=... PublisherAccountId=...
```

## 开发约束

- 新增游戏内 API 必须放入明确业务模块，例如 `game/player/cafe`、`game/player/mail`、`modules/battle`。
- 通用构包、加密、协议表、网关客户端只能放在 `core`。
- 代理、JSON、时间、文件等横向工具放在 `utils`，不要反向依赖业务模块。
- RESTful API、GUI、任务队列以后应作为独立入口调用 `modules` 服务，不直接复制发包逻辑。
- token、密码、session key、设备唯一 ID、运行日志和 `analysis_reports` 不进入 git。

## 测试

当前测试保持“无 pytest 也能运行”的形式：

```powershell
python -m py_compile main.py headlessba\cli.py
python tests\test_ba_replay.py
python tests\test_login_equivalence.py
python tests\test_android_runtime_profile.py
```

## Git 代理

如果需要通过本地代理推送：

```powershell
git config http.proxy http://127.0.0.1:60808
git config https.proxy http://127.0.0.1:60808
```
