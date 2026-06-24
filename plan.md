# 游戏内 API 接入计划

记录接入边界、完成判定和下一步。**已接入能力清单不在这里维护**——逐协议状态见 `docs/protocols.md`，调用方式见 `README.md` 与 `docs/wiki/`。

live 验证使用已登录的 `session/profile`，输出只保留结果摘要，不回显 token / MxToken / SessionKey / npToken / 账号密码 / 完整 payload / dump。

## 接入边界（硬约束）

SDK 仅供调用，不影响游戏公平性。**不接入**：战斗进入/结算/成绩提交、竞技场(Arena)、小游戏对局/结算、抽卡购买·保存·选择招募结果、支付(Billing 交易流程)、风控上报(XignCode/ngsx)、账号危险操作(创建/改名/重置/解绑/失效 token/生日身份写入)。状态变更与资源消耗接口必须 `confirm=True`。

## 完成判定

- 单元测试通过（pytest，全量绿）；`py_compile` 覆盖 `HLBA.py` + `core` + `modules`。
- live 用已登录账号验证：读接口实读；写接口验证 `confirm` 守卫与协议路由。
- `docs/protocols.md` 与对应文档同步完成状态。

## 当前进度

**边界内协议接入已完成**：397 个协议中 299 个 ✓（只读查询 / 领取 / 设置·偏好 / 养成·消耗 / 破坏性·社团，写接口全部 `confirm=True`）。剩余空白项均为边界外的战斗/小游戏对局/支付/抽卡/账号危险，按约束不接；少数无 `RequestClass`/schema 的协议不硬补。

打磨已完成：登录链路全链路代理（含 SOCKS，三处 urllib→requests）、高价值只读补 `format_*` 统一返回风格、`common` 工具跨模块去重、参数/命名规范、死代码清理、全模块测试补齐（`tests/` 全绿）。

## 下一步计划

边界内协议接入、只读返回风格统一（高价值只读已补 `format_*`）、`common` 工具去重均已完成。剩余仅按需打磨：

- 为更多写操作补"可领/可用"前置校验——受限于是否有可查询的状态源；无现成查询的领奖类维持 `confirm=True` 守卫。
- 随真实账号出现可领/可购场景时补 live 实测样本（无业务数据的握手类只读维持原始负载）。

## 不接入的封装

- 不自动串联整套日常流程。
- 不重新添加已从 `core/data` 与 docs 排除的协议。
- 不接战斗进入/结算/成绩提交、竞技场、小游戏对局/结算、抽卡、支付、风控上报、账号危险操作。
- `core/data` 无 `RequestClass`/schema 的协议不硬补。

## live 测试输出格式

只输出摘要，例如 `Mission_List ok: progress_count=12`。禁止输出完整 session/profile、gateway payload、token、SessionKey、MxToken、账号密码。
