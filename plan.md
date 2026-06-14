# 游戏内 API 接入计划

本计划只记录下一步待接入、待验证或被账号状态挡住的内容。已经完成并在 `docs/protocols.md` 打勾的项目不再放入主表，避免计划表越来越像流水账。

测试会使用外部提供的已登录 session/profile 做 live 验证，但测试输出不得回显 token、MxToken、SessionKey、npToken、账号密码等敏感值。SDK 不保存请求包、响应包、packet 或 dump。

## 完成判定

- 单元测试通过。
- live 测试使用已登录 session/profile 调用成功。
- SDK 返回结构已根据真实返回整理过。
- `docs/protocols.md` 和对应 `docs/protocols/<Module>.md` 已更新完成状态。
- 状态变更协议必须先确认前置状态满足，不能盲调用。

## 当前待办

| 优先级 | 模块 | 协议 | SDK 方法 | 类型 | 当前状态 | 下一步 |
| ---: | --- | --- | --- | --- | --- | --- |
| 2 | Academy | `Academy_AttendSchedule` | `client.academy.attend_schedule(...)` | 状态变更 | 已封装，待 live 成功 | 已修正为使用 `AcademyDB.ZoneVisitCharacterDBs` 的 key 作为 `ZoneId`，并排除 `ZoneScheduleGroupRecords` 已执行 zone；当前小号无可用 zone，大号候选 zone 返回 `ErrorCode=10 AccountCurrencyCannotAffordCost`。等有课程表票/资源的账号后重测，成功后打勾。 |
| 3 | Attendance | `Attendance_Reward` | `client.attendance.reward(...)` | 状态变更 | 待 live | 只在 `client.attendance.status()` 显示有可领取奖励时发包；当前账号没有 claimable 奖励。 |
| 4 | Mail | `Mail_ReceiveSemiPermanent` | `client.mail.receive_semi_permanent(...)` | 状态变更 | 待评估 | 先确认 `Mail_ListSemiPermanent` 是否有稳定列表和 ID 字段，再决定是否封装领取。 |
| 5 | Sweep | `ContentSweep_Request` / `ContentSweep_MultiSweep` | `client.sweep.*` | 状态变更 | 待评估 | 需要先有可靠的通关状态、扫荡次数和资源校验来源；目前只确认 `MultiSweepParameter` 字段结构，不硬接消耗入口。 |

## 暂不接入或等待外部条件

| 模块 | 协议 | 处理 | 原因 |
| --- | --- | --- | --- |
| Attendance | `Attendance_List` / `Attendance_Check` | 不封装稳定 API | live 直接发包返回 `Protocol=-1 / ErrorCode=1`；签到状态来自 `Account_Auth` 缓存。 |
| Academy | `Academy_AttendFavorSchedule` | 暂不接入 | 当前 `core/data` 没有可用 RequestClass/schema，不绕过协议边界补入口。 |
| Sweep | `SkipHistory_List` | 暂不封装稳定 API | live 探针返回 `Protocol=-1 / ErrorCode=500`。 |
| Shop | 普通商品购买/刷新类 | 等明确需求再做 | 涉及资源消耗，必须逐个协议设计显式确认参数和前置校验。 |
| Cafe | 家具布置/移动/移除类 | 暂不做 | 属于布局编辑，不是当前“日常 API 接入”优先目标。 |

## 已完成范围

已完成项以 `docs/protocols.md` 的勾选为准，当前包括登录链路、会话恢复、Account_CurrencySync、Mission、Cafe、Mail 普通领取、Shop AP、Character_List、Campaign_List、WeekDungeon_List、MomoTalk 概览/消息/已读推进、Sweep 预设只读等已验证能力。

## 不做的封装

- 不封装 `client.daily.run()` 或“一键完成每日任务”。
- 不自动串联整套日常流程。
- 不重新添加已从 `core/data` 和 docs 中排除的协议。
- 不接战斗进入、战斗结算、成绩提交、竞技场、小游戏结算、抽卡、支付、风控上报、账号危险操作。

## live 测试输出格式

live 测试只输出摘要，例如：

```text
Mission_List ok: progress_count=12 history_count=4
```

禁止输出完整 session/profile、完整 gateway payload、token、SessionKey、MxToken、账号密码。
