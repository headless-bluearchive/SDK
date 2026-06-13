# 统一开发约束

## 项目定位

本仓库按独立ba客户端开发。默认能力必须来自项目自身的配置、代码、持久化 profile 和网络请求结果，而不是原游戏客户端。

## 基本原则

- 正常调用先实例化 `HLBA.Client`，再调用实例方法。
- 新能力写入 `core/`、`modules/`、`config/` 或 `docs/`。
- 不新增分散的 CLI 文件、脚本入口、`argparse`、`__main__` 执行块或命令行参数解析。
- 未来需要 CLI 时，只能集中到顶层 `cli.py`。
- 不新增读取原游戏目录、dump、`shared_prefs`、`LocalConfig`、`Hosts`、DLL、调试桥输出的逻辑。
- 变更说明只更新 `docs/`，不要修改 `README.md`。

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
- 具体协议、登录、游戏 API 写到 `docs/api/`。
