# headlessBA 模块开发规范

## 分层规则

- `core`：只放协议、加密、packet、gateway client、API registry 这类基础能力。
- `modules/auth`：只放登录、鉴权、TOYSDK、ProofToken、Account/Auth 相关链路。
- `modules/runtime`：只放设备、区域、运行态配置发现和 profile 生成。
- `game/player/<domain>`：玩家业务域，例如 `cafe`、`mail`、`inventory`、`student`。
- `utils`：横向小工具，不能依赖业务模块。
- `database`：持久化连接、仓储、迁移脚本的归口。
- `log`：统一日志配置，不在业务模块里重复配置 root logger。

## 新增游戏 API 的流程

1. 找到业务域，例如 Cafe 放到 `game/player/cafe`。
2. 在该域内添加 request builder 或 service，不要写进 CLI。
3. 如需复用通用发包能力，调用 `core.client.BAReplayClient` 和 `core.api_registry`。
4. 给新增 builder 补测试，测试文件按业务域命名。
5. CLI、REST API、GUI 只做入口和参数转换，不承载业务逻辑。

## 命名建议

- 文件名使用小写下划线。
- request builder 使用 `build_<domain>_<action>_fields`。
- service 类使用 `<Domain>Service`。
- 与协议表相关的字符串集中通过 registry 或常量暴露。
