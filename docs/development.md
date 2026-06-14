# 统一开发约束

## 项目定位

本仓库按独立 BA SDK 开发。默认能力必须来自项目自身的配置、代码、调用方传入的 profile/session 和网络请求结果，而不是原游戏客户端。

## 基本原则

- 正常调用先实例化 `HLBA.Client`，再调用实例方法。
- 新能力写入 `core/`、`modules/`、`config/` 或 `docs/`。
- 不新增分散的 CLI 文件、脚本入口、`argparse`、`__main__` 执行块或命令行参数解析。
- 未来需要 CLI 时也应该放到外部项目里；SDK 内部先保持库形态。
- 不新增读取原游戏目录、dump、`shared_prefs`、`LocalConfig`、`Hosts`、DLL、调试桥输出的逻辑。
- 逆向/调试目录只能作为人工对照来源；需要进入 SDK 的稳定表必须整理到 `core/data/`，运行时不能依赖外部调试路径。
- 细节说明写进 `docs/wiki/`；README 只放当前状态和入口说明，不要把它写成小说。

## Game 模块

- 所有游戏内 API 都放在 `modules/game/<domain>/`。
- 不再建立顶层 `game/` 业务目录。
- 当前 Cafe 示例路径为 `modules/game/player/cafe/service.py`。
- 单个目录只放同一领域的 service、request builder、models 或 tests，不混入登录、runtime、GUI、REST API 代码。

## 新增游戏 API

1. 在 `modules/game/<domain>/` 下放 service 或 request builder。
2. 如果需要协议元信息，通过 `core.api_registry` 注册。
3. 复用 `core.client.BAReplayClient` 的构包和发送能力。
4. 给字段构造、协议选择、响应处理补轻量测试。
5. 对外入口最后再接到 REST API 或 GUI，不让入口层承担业务流程。

## 文档位置

- 宏观结构写在 `docs/architecture.md`。
- 开发规则写在 `docs/development.md`。
- 具体协议、登录、游戏 API 写到 `docs/wiki/`。
