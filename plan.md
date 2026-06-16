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

## 暂不接入或等待外部条件

| 模块 | 协议 | 处理 | 原因 |
| --- | --- | --- | --- |
| Attendance | `Attendance_List` / `Attendance_Check` | 不封装稳定 API | live 直接发包返回 `Protocol=-1 / ErrorCode=1`；签到状态来自 `Account_Auth` 缓存。 |
| Academy | `Academy_AttendFavorSchedule` | 暂不接入 | 当前 `core/data` 没有可用 RequestClass/schema，不绕过协议边界补入口。 |
| Mail | `Mail_ReceiveSemiPermanent` | 已封装，等待可领取账号验证 | `Mail_ListSemiPermanent` 已 live 验证，小号/大号当前列表为空；SDK 会在无可领取邮件时本地拦截，不盲发领取。 |
| Mission / NGS | `Mission_Reward` / `Mission_MultipleReward` | 等外部 NGS 结论 | 小号仍返回 `1032 NexonNgsmValidateFail`；当前先不作为主线阻塞项。 |
| Sweep | `ContentSweep_Request` / `ContentSweep_MultiSweep` | 已封装，等待调用方显式确认场景 | SDK 要求 `confirm=True`，不会自动挑关卡、不会自动算资源、不会绕过通关记录；live 不主动执行消耗。 |
| Sweep | `SkipHistory_List` | 暂不封装稳定 API | live 探针返回 `Protocol=-1 / ErrorCode=500`。 |
| Shop | 普通商品购买/刷新类 | 等明确需求再做 | 涉及资源消耗，必须逐个协议设计显式确认参数和前置校验。 |
| Cafe | 家具布置/移动/移除类 | 暂不做 | 属于布局编辑，不是当前“日常 API 接入”优先目标。 |

## 已完成范围

已完成项以 `docs/protocols.md` 的勾选为准，当前包括登录链路、会话恢复、Account_CurrencySync、Attendance Reward、Mission、Cafe、Mail 普通领取、Mail 半永久列表、Shop AP、Character_List、Campaign_List、WeekDungeon_List、MomoTalk 概览/消息/已读推进、Sweep 预设只读和显式确认扫荡入口等能力。

本批次已完成 70 个低风险只读/查询接口接入，覆盖 Account_GetTutorial、Attachment、BattlePass 只读、Cafe_TrophyHistory、CharacterGear、Clan 查询、Conquest 查询、Craft_List、Echelon_List、EliminateRaid 查询、Equipment、Event/EventContent 只读、Friend 查询、Item_List、Management、MemoryLobby、MiniGame 只读、PermanentRaid_Lobby、Raid 查询、Scenario_List、SchoolDungeon_List、Shop 招募状态只读、System_Version、Toast_List、WorldRaid 查询。使用说明见 `docs/wiki/player/readonly-extended.md`。

2026-06-16 已对这 70 个新增只读接口做 live 验证：54 个接口在小号或大号至少一个账号上成功；16 个接口因当前活动、小游戏赛季、WorldRaid 参数或自选招募不存在而返回开放条件/数据不存在类错误，已记录到 `docs/wiki/player/readonly-extended.md` 的 Live 验证表。

另外已按显式确认状态变更接口接入 9 个协议：Friend_SendFriendRequest、Friend_AcceptFriendRequest、Friend_DeclineFriendRequest、Friend_CancelFriendRequest、Craft_CompleteProcessAll、Craft_ShiftingCompleteProcessAll、Campaign_ConfirmMainStage、Scenario_ConfirmMainStage、Scenario_SkipMainStage。调用必须传 `confirm=True`，默认会先查询当前状态做前置校验。使用说明见 `docs/wiki/player/state-changing.md`。

live 验证结果：好友申请发送/取消/拒绝/接受已用小号和大号互测成功；制造完成两个账号当前无普通/转化制造候选，未盲发；主线/剧情关卡确认或跳过需要活跃关卡 SaveData，上述账号直接用历史列表 ID 不满足前置条件，其中 `Campaign_ConfirmMainStage` 返回 `ErrorCode=6003 CampaignStageInvalidSaveData`，SDK 默认改为本地拦截。

## 不做的封装

- 不自动串联整套日常流程。
- 不重新添加已从 `core/data` 和 docs 中排除的协议。
- 不接战斗进入、战斗结算、成绩提交、竞技场、小游戏结算、抽卡、支付、风控上报、账号危险操作。

## live 测试输出格式

live 测试只输出摘要，例如：

```text
Mission_List ok: progress_count=12 history_count=4
```

禁止输出完整 session/profile、完整 gateway payload、token、SessionKey、MxToken、账号密码。
