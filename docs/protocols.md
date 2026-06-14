# 协议总表

本表由 `core/data/protocols.json` 整理，按协议名前缀归类。详细模块表见 `docs/protocols/`，模块文档中已补充 Request/Response 字段结构、字段说明与验证状态。

## 接入边界

已删除会影响游戏公平性的协议文档部分，包括战斗进入、战斗结算、成绩提交、竞技场、小游戏结算、翻牌开奖、奖励重掷、招募购买、抽取招募、保存招募结果、选择招募结果、活动翻卡开奖等内容。

SDK 文档只保留登录、查询、同步、常规资源、扫荡，以及招募只读状态类协议。后续新增协议时也按这个边界维护。

## 每日任务影响

| 每日任务类型 | 当前文档状态 | 影响 |
| --- | --- | --- |
| 每天登入 | 保留登录与大厅同步流程 | 可支持 |
| 咖啡厅获得学生羁绊点数 | 保留 `Cafe_Interact` | 可支持 |
| 执行课程表 | 保留 `Academy_AttendSchedule`；`Academy_AttendFavorSchedule` 当前无 RequestClass | 可支持 |
| 领取已完成每日任务奖励 | 保留 `Mission_List` / `Mission_Reward` / `Mission_MultipleReward` | 可支持 |
| 完成学园交流会 | 仅保留 `SchoolDungeon_List` 查询；完成/战斗结果类协议未保留 | 影响自动完成 |
| 参加战术大赛 | `Arena` 模块已删除 | 影响自动完成 |

说明：SDK 可以读取每日任务进度并领取已经完成的任务奖励，但不会提供战斗、竞技场、成绩提交等会影响公平性的完成链路。

## 实现难度标签

| 标签 | 含义 |
| --- | --- |
| 低 | 查询、列表、状态读取或单纯同步，通常只需要登录后的 session 与少量固定字段。 |
| 中 | 需要前置查询结果、资源/次数校验、状态变更或领奖，适合按模块封装。 |
| 高 | 涉及登录会话、ProofToken、支付、跨模块状态机或复杂活动流程，需要先做端到端验证。 |

完成列说明：`✓` 表示 SDK 当前已作为稳定登录链路的一部分完成；`-` 表示不建议或不需要作为 SDK API 实现；空白表示仅有字段文档，或只是登录后启动同步时被顺带调用，尚未封装为独立稳定 API。

| 模块 | 协议名 | 协议号 | 作用 | 实现难度 | 完成 | 详细 |
| --- | --- | ---: | --- | --- |:--:| --- |
| 课程表/日程 | `Academy_GetInfo` | `24000` | 课程表/日程：获取模块信息 | 低 | ✓  | [Academy](protocols/Academy.md) |
| 课程表/日程 | `Academy_AttendSchedule` | `24001` | 课程表/日程：执行日程课程 | 中 |    | [Academy](protocols/Academy.md) |
| 课程表/日程 | `Academy_AttendFavorSchedule` | `24002` | 课程表/日程：执行可提升羁绊的日程 | 中 | -  | [Academy](protocols/Academy.md) |
| 账号与登录 | `Account_Create` | `1000` | 账号与登录：创建账号数据 | 中 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_Nickname` | `1001` | 账号与登录：设置昵称 | 中 |    | [Account](protocols/Account.md) |
| 账号与登录 | `Account_Auth` | `1002` | 账号与登录：账号认证并进入主网关会话 | 高 | ✓  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_CurrencySync` | `1003` | 账号与登录：同步货币数据 | 低 | ✓  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_SetRepresentCharacterAndComment` | `1004` | 账号与登录：设置代表学生和个人简介 | 中 |    | [Account](protocols/Account.md) |
| 账号与登录 | `Account_GetTutorial` | `1005` | 账号与登录：获取教程进度 | 低 |    | [Account](protocols/Account.md) |
| 账号与登录 | `Account_SetTutorial` | `1006` | 账号与登录：更新教程进度 | 中 |    | [Account](protocols/Account.md) |
| 账号与登录 | `Account_PassCheck` | `1007` | 账号与登录：通行/状态检查 | 中 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_VerifyForYostar` | `1008` | 账号与登录：Yostar 登录验证 | 高 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_CheckYostar` | `1009` | 账号与登录：校验 Yostar 登录态 | 高 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_CallName` | `1010` | 账号与登录：设置老师称呼 | 中 |    | [Account](protocols/Account.md) |
| 账号与登录 | `Account_BirthDay` | `1011` | 账号与登录：设置或提交生日信息 | 中 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_Auth2` | `1012` | 账号与登录：账号认证备用流程 | 高 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_LinkReward` | `1013` | 账号与登录：领取账号绑定奖励 | 中 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_CheckNexon` | `1014` | 账号与登录：校验 Nexon 登录态并下发 1014 会话密钥 | 高 | ✓  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_DetachNexon` | `1015` | 账号与登录：解除 Nexon 绑定 | 高 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_ReportXignCodeCheater` | `1016` | 账号与登录：上报 XignCode 风控结果 | 高 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_DismissRepurchasablePopup` | `1017` | 账号与登录：关闭可重复购买弹窗 | 中 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_InvalidateToken` | `1018` | 账号与登录：使当前登录 token 失效 | 高 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_LoginSync` | `1019` | 账号与登录：登录后同步大厅与各模块基础数据 | 低 | ✓  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_VerifyCheckAdultAgree` | `1020` | 账号与登录：验证成人确认状态 | 中 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_SetCheckAdultAgree` | `1021` | 账号与登录：设置成人确认同意状态 | 中 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_Reset` | `1022` | 账号与登录：重置账号相关状态 | 高 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_RequestBirthdayMail` | `1023` | 账号与登录：请求生日邮件 | 低 | -  | [Account](protocols/Account.md) |
| 账号与登录 | `Account_CheckAccountLevelReward` | `1024` | 账号与登录：检查账号等级奖励状态 | 中 |    | [Account](protocols/Account.md) |
| 账号与登录 | `Account_ReceiveAccountLevelReward` | `1025` | 账号与登录：领取AccountLevel奖励 | 中 |    | [Account](protocols/Account.md) |
| 附件与头像框 | `Attachment_Get` | `46000` | 附件与头像框：获取数据 | 低 |    | [Attachment](protocols/Attachment.md) |
| 附件与头像框 | `Attachment_EmblemList` | `46001` | 附件与头像框：Emblem列表 | 低 |    | [Attachment](protocols/Attachment.md) |
| 附件与头像框 | `Attachment_EmblemAcquire` | `46002` | 附件与头像框：执行 EmblemAcquire 流程 | 中 |    | [Attachment](protocols/Attachment.md) |
| 附件与头像框 | `Attachment_EmblemAttach` | `46003` | 附件与头像框：执行 EmblemAttach 流程 | 中 |    | [Attachment](protocols/Attachment.md) |
| 签到 | `Attendance_List` | `9000` | 签到：获取列表数据 | 中 | -  | [Attendance](protocols/Attendance.md) |
| 签到 | `Attendance_Check` | `9001` | 签到：检查状态 | 中 | -  | [Attendance](protocols/Attendance.md) |
| 签到 | `Attendance_Reward` | `9002` | 签到：奖励 | 中 |    | [Attendance](protocols/Attendance.md) |
| 战斗通行证 | `BattlePass_GetInfo` | `51000` | 战斗通行证：获取模块信息 | 低 |    | [BattlePass](protocols/BattlePass.md) |
| 战斗通行证 | `BattlePass_BuyLevel` | `51001` | 战斗通行证：购买Level | 中 |    | [BattlePass](protocols/BattlePass.md) |
| 战斗通行证 | `BattlePass_ReceiveReward` | `51002` | 战斗通行证：领取奖励 | 中 |    | [BattlePass](protocols/BattlePass.md) |
| 战斗通行证 | `BattlePass_MissionList` | `51003` | 战斗通行证：任务列表 | 低 |    | [BattlePass](protocols/BattlePass.md) |
| 战斗通行证 | `BattlePass_MissionSingleReward` | `51004` | 战斗通行证：任务Single奖励 | 中 |    | [BattlePass](protocols/BattlePass.md) |
| 战斗通行证 | `BattlePass_MissionMultipleReward` | `51005` | 战斗通行证：任务Multiple奖励 | 中 |    | [BattlePass](protocols/BattlePass.md) |
| 战斗通行证 | `BattlePass_Check` | `51006` | 战斗通行证：检查状态 | 中 |    | [BattlePass](protocols/BattlePass.md) |
| 充值与购买记录 | `Billing_TransactionStartByYostar` | `29000` | 充值与购买记录：执行 TransactionStartByYostar 流程 | 高 | -  | [Billing](protocols/Billing.md) |
| 充值与购买记录 | `Billing_TransactionEndByYostar` | `29001` | 充值与购买记录：执行 TransactionEndByYostar 流程 | 高 | -  | [Billing](protocols/Billing.md) |
| 充值与购买记录 | `Billing_PurchaseListByYostar` | `29002` | 充值与购买记录：Purchase列表ByYostar | 高 | -  | [Billing](protocols/Billing.md) |
| 充值与购买记录 | `Billing_PurchaseCashShopVerifyByNexon` | `29003` | 充值与购买记录：PurchaseCash商店VerifyByNexon | 高 | -  | [Billing](protocols/Billing.md) |
| 充值与购买记录 | `Billing_CheckConditionCashShopGoods` | `29004` | 充值与购买记录：检查ConditionCash商店Goods | 高 | -  | [Billing](protocols/Billing.md) |
| 充值与购买记录 | `Billing_PurchaseListByNexon` | `29005` | 充值与购买记录：Purchase列表ByNexon | 高 | -  | [Billing](protocols/Billing.md) |
| 充值与购买记录 | `Billing_ValidateByNexon` | `29006` | 充值与购买记录：执行 ValidateByNexon 流程 | 高 | -  | [Billing](protocols/Billing.md) |
| 充值与购买记录 | `Billing_FinishByNexon` | `29007` | 充值与购买记录：执行 FinishByNexon 流程 | 高 | -  | [Billing](protocols/Billing.md) |
| 充值与购买记录 | `Billing_PurchaseFreeProduct` | `29008` | 充值与购买记录：执行 PurchaseFreeProduct 流程 | 高 | -  | [Billing](protocols/Billing.md) |
| 咖啡厅 | `Cafe_Get` | `20000` | 咖啡厅：获取数据 | 低 | ✓  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_Ack` | `20001` | 咖啡厅：确认咖啡厅状态变更 | 中 | -  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_Deploy` | `20002` | 咖啡厅：布置咖啡厅家具 | 中 | -  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_Relocate` | `20003` | 咖啡厅：移动咖啡厅家具 | 中 | -  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_Remove` | `20004` | 咖啡厅：移除咖啡厅家具 | 中 | -  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_RemoveAll` | `20005` | 咖啡厅：移除全部咖啡厅家具 | 中 | -  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_Interact` | `20006` | 咖啡厅：与咖啡厅内角色互动/摸头 | 中 | ✓  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_ListPreset` | `20007` | 咖啡厅：获取预设列表 | 高 | -  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_RenamePreset` | `20008` | 咖啡厅：重命名咖啡厅预设 | 高 | -  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_ClearPreset` | `20009` | 咖啡厅：清空咖啡厅预设 | 高 | -  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_UpdatePresetFurniture` | `20010` | 咖啡厅：更新预设家具布局 | 高 | -  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_ApplyPreset` | `20011` | 咖啡厅：应用咖啡厅家具预设 | 高 | -  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_RankUp` | `20012` | 咖啡厅：提升等级 | 中 |    | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_ReceiveCurrency` | `20013` | 咖啡厅：领取咖啡厅产出货币 | 中 | ✓  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_GiveGift` | `20014` | 咖啡厅：赠送礼物 | 中 |    | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_SummonCharacter` | `20015` | 咖啡厅：邀请角色到咖啡厅 | 中 |    | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_TrophyHistory` | `20016` | 咖啡厅：获取咖啡厅奖杯历史 | 低 |    | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_ApplyTemplate` | `20017` | 咖啡厅：应用咖啡厅模板 | 中 | -  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_Open` | `20018` | 咖啡厅：打开或解锁对应内容 | 中 |    | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_Travel` | `20019` | 咖啡厅：切换或访问咖啡厅区域 | 中 |    | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_SummonCharacterTicketUse` | `20020` | 咖啡厅：使用咖啡厅邀请券 | 中 |    | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_PresetDetail` | `20021` | 咖啡厅：获取咖啡厅预设详情 | 高 | -  | [Cafe](protocols/Cafe.md) |
| 咖啡厅 | `Cafe_UpdateCopyPresetFurniture` | `20022` | 咖啡厅：更新复制预设中的家具布局 | 高 | -  | [Cafe](protocols/Cafe.md) |
| 主线关卡 | `Campaign_List` | `6000` | 主线关卡：获取列表数据 | 低 | ✓  | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_EnterMainStage` | `6001` | 主线关卡：进入Main关卡 | 高 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_ConfirmMainStage` | `6002` | 主线关卡：ConfirmMain关卡 | 低 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_DeployEchelon` | `6003` | 主线关卡：布置Echelon | 高 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_WithdrawEchelon` | `6004` | 主线关卡：执行 WithdrawEchelon 流程 | 高 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_MapMove` | `6005` | 主线关卡：执行 MapMove 流程 | 高 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_EndTurn` | `6006` | 主线关卡：执行 EndTurn 流程 | 高 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_ChapterClearReward` | `6010` | 主线关卡：Chapter清空奖励 | 中 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_Heal` | `6011` | 主线关卡：执行 Heal 流程 | 中 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_EnterSubStage` | `6012` | 主线关卡：进入Sub关卡 | 高 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_Portal` | `6014` | 主线关卡：执行 Portal 流程 | 高 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_ConfirmTutorialStage` | `6015` | 主线关卡：ConfirmTutorial关卡 | 低 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_PurchasePlayCountHardStage` | `6016` | 主线关卡：PurchasePlayCountHard关卡 | 中 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_EnterTutorialStage` | `6017` | 主线关卡：进入Tutorial关卡 | 低 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_RestartMainStage` | `6019` | 主线关卡：RestartMain关卡 | 高 |    | [Campaign](protocols/Campaign.md) |
| 主线关卡 | `Campaign_EnterMainStageStrategySkip` | `6020` | 主线关卡：进入Main关卡StrategySkip | 高 |    | [Campaign](protocols/Campaign.md) |
| 学生角色 | `Character_List` | `2000` | 学生角色：获取列表数据 | 低 | ✓  | [Character](protocols/Character.md) |
| 学生角色 | `Character_Transcendence` | `2001` | 学生角色：突破/升星 | 低 |    | [Character](protocols/Character.md) |
| 学生角色 | `Character_ExpGrowth` | `2002` | 学生角色：执行 ExpGrowth 流程 | 中 |    | [Character](protocols/Character.md) |
| 学生角色 | `Character_FavorGrowth` | `2003` | 学生角色：执行 FavorGrowth 流程 | 中 |    | [Character](protocols/Character.md) |
| 学生角色 | `Character_UpdateSkillLevel` | `2004` | 学生角色：更新SkillLevel | 中 |    | [Character](protocols/Character.md) |
| 学生角色 | `Character_UnlockWeapon` | `2005` | 学生角色：执行 UnlockWeapon 流程 | 中 |    | [Character](protocols/Character.md) |
| 学生角色 | `Character_WeaponExpGrowth` | `2006` | 学生角色：执行 WeaponExpGrowth 流程 | 中 |    | [Character](protocols/Character.md) |
| 学生角色 | `Character_WeaponTranscendence` | `2007` | 学生角色：执行 WeaponTranscendence 流程 | 中 |    | [Character](protocols/Character.md) |
| 学生角色 | `Character_SetFavorites` | `2008` | 学生角色：设置Favorites | 中 |    | [Character](protocols/Character.md) |
| 学生角色 | `Character_SetCostume` | `2009` | 学生角色：设置Costume | 中 |    | [Character](protocols/Character.md) |
| 学生角色 | `Character_BatchSkillLevelUpdate` | `2010` | 学生角色：BatchSkillLevel更新 | 中 |    | [Character](protocols/Character.md) |
| 学生角色 | `Character_PotentialGrowth` | `2011` | 学生角色：执行 PotentialGrowth 流程 | 中 |    | [Character](protocols/Character.md) |
| 爱用品/角色装备 | `CharacterGear_List` | `44000` | 爱用品/角色装备：获取列表数据 | 低 |    | [CharacterGear](protocols/CharacterGear.md) |
| 爱用品/角色装备 | `CharacterGear_Unlock` | `44001` | 爱用品/角色装备：执行 Unlock 流程 | 中 |    | [CharacterGear](protocols/CharacterGear.md) |
| 爱用品/角色装备 | `CharacterGear_TierUp` | `44002` | 爱用品/角色装备：Tier提升 | 中 |    | [CharacterGear](protocols/CharacterGear.md) |
| 社团 | `Clan_Lobby` | `28000` | 社团：获取或进入模块大厅 | 低 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Login` | `28001` | 社团：进入模块并同步基础数据 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Search` | `28002` | 社团：搜索 | 低 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Create` | `28003` | 社团：创建账号数据 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Member` | `28004` | 社团：成员 | 低 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Applicant` | `28005` | 社团：执行 Applicant 流程 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Join` | `28006` | 社团：加入 | 低 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Quit` | `28007` | 社团：执行 Quit 流程 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Permit` | `28008` | 社团：执行 Permit 流程 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Kick` | `28009` | 社团：执行 Kick 流程 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Setting` | `28010` | 社团：执行 Setting 流程 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Confer` | `28011` | 社团：执行 Confer 流程 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Dismiss` | `28012` | 社团：解散或关闭 | 低 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_AutoJoin` | `28013` | 社团：执行 AutoJoin 流程 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_MemberList` | `28014` | 社团：获取成员列表 | 低 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_CancelApply` | `28015` | 社团：取消申请 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_MyAssistList` | `28016` | 社团：My助战列表 | 低 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_SetAssist` | `28017` | 社团：设置助战 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_ChatLog` | `28018` | 社团：执行 ChatLog 流程 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_Check` | `28019` | 社团：检查状态 | 中 |    | [Clan](protocols/Clan.md) |
| 社团 | `Clan_AllAssistList` | `28020` | 社团：全部助战列表 | 低 |    | [Clan](protocols/Clan.md) |
| 通关编队记录 | `ClearDeck_List` | `34000` | 通关编队记录：获取列表数据 | 中 |    | [ClearDeck](protocols/ClearDeck.md) |
| 通关编队记录 | `ClearDeck_GroupedList` | `34001` | 通关编队记录：Grouped列表 | 中 |    | [ClearDeck](protocols/ClearDeck.md) |
| 占领战 | `Conquest_GetInfo` | `42000` | 占领战：获取模块信息 | 低 |    | [Conquest](protocols/Conquest.md) |
| 占领战 | `Conquest_Conquer` | `42001` | 占领战：执行 Conquer 流程 | 中 |    | [Conquest](protocols/Conquest.md) |
| 占领战 | `Conquest_DeployEchelon` | `42004` | 占领战：布置Echelon | 高 |    | [Conquest](protocols/Conquest.md) |
| 占领战 | `Conquest_ManageBase` | `42005` | 占领战：执行 ManageBase 流程 | 中 |    | [Conquest](protocols/Conquest.md) |
| 占领战 | `Conquest_UpgradeBase` | `42006` | 占领战：执行 UpgradeBase 流程 | 中 |    | [Conquest](protocols/Conquest.md) |
| 占领战 | `Conquest_TakeEventObject` | `42007` | 占领战：Take活动Object | 低 |    | [Conquest](protocols/Conquest.md) |
| 占领战 | `Conquest_ReceiveCalculateRewards` | `42010` | 占领战：领取CalculateRewards | 中 |    | [Conquest](protocols/Conquest.md) |
| 占领战 | `Conquest_NormalizeEchelon` | `42011` | 占领战：执行 NormalizeEchelon 流程 | 中 |    | [Conquest](protocols/Conquest.md) |
| 占领战 | `Conquest_Check` | `42012` | 占领战：检查状态 | 中 |    | [Conquest](protocols/Conquest.md) |
| 占领战 | `Conquest_MainStoryGetInfo` | `42015` | 占领战：MainStory获取信息 | 低 |    | [Conquest](protocols/Conquest.md) |
| 占领战 | `Conquest_MainStoryConquer` | `42016` | 占领战：执行 MainStoryConquer 流程 | 中 |    | [Conquest](protocols/Conquest.md) |
| 占领战 | `Conquest_MainStoryCheck` | `42019` | 占领战：MainStory检查 | 中 |    | [Conquest](protocols/Conquest.md) |
| 内容日志 | `ContentLog_UIOpenStatistics` | `32000` | 内容日志：UI打开Statistics | 中 | -  | [ContentLog](protocols/ContentLog.md) |
| 内容存档 | `ContentSave_Get` | `26000` | 内容存档：获取数据 | 中 |    | [ContentSave](protocols/ContentSave.md) |
| 内容存档 | `ContentSave_Discard` | `26001` | 内容存档：执行 Discard 流程 | 中 |    | [ContentSave](protocols/ContentSave.md) |
| 扫荡预设 | `ContentSweep_Request` | `27000` | 扫荡预设：请求 | 中 |    | [ContentSweep](protocols/ContentSweep.md) |
| 扫荡预设 | `ContentSweep_MultiSweep` | `27001` | 扫荡预设：执行 MultiSweep 流程 | 中 |    | [ContentSweep](protocols/ContentSweep.md) |
| 扫荡预设 | `ContentSweep_MultiSweepPresetList` | `27002` | 扫荡预设：MultiSweep预设列表 | 高 | ✓  | [ContentSweep](protocols/ContentSweep.md) |
| 扫荡预设 | `ContentSweep_SetMultiSweepPreset` | `27003` | 扫荡预设：设置MultiSweep预设 | 高 | -  | [ContentSweep](protocols/ContentSweep.md) |
| 扫荡预设 | `ContentSweep_SetMultiSweepPresetName` | `27004` | 扫荡预设：设置MultiSweep预设Name | 高 | -  | [ContentSweep](protocols/ContentSweep.md) |
| 制造 | `Craft_List` | `21000` | 制造：获取列表数据 | 低 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_SelectNode` | `21001` | 制造：执行 SelectNode 流程 | 中 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_UpdateNodeLevel` | `21002` | 制造：更新NodeLevel | 中 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_BeginProcess` | `21003` | 制造：执行 BeginProcess 流程 | 中 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_CompleteProcess` | `21004` | 制造：执行 CompleteProcess 流程 | 中 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_Reward` | `21005` | 制造：奖励 | 中 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_HistoryList` | `21006` | 制造：历史记录列表 | 低 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_ShiftingBeginProcess` | `21007` | 制造：执行 ShiftingBeginProcess 流程 | 中 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_ShiftingCompleteProcess` | `21008` | 制造：执行 ShiftingCompleteProcess 流程 | 中 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_ShiftingReward` | `21009` | 制造：Shifting奖励 | 中 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_AutoBeginProcess` | `21010` | 制造：执行 AutoBeginProcess 流程 | 中 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_CompleteProcessAll` | `21011` | 制造：CompleteProcess全部 | 低 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_RewardAll` | `21012` | 制造：奖励全部 | 中 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_ShiftingCompleteProcessAll` | `21013` | 制造：ShiftingCompleteProcess全部 | 低 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_ShiftingRewardAll` | `21014` | 制造：Shifting奖励全部 | 中 |    | [Craft](protocols/Craft.md) |
| 制造 | `Craft_SavePreset` | `21015` | 制造：保存预设 | 高 | -  | [Craft](protocols/Craft.md) |
| 制造 | `Craft_SavePresetName` | `21016` | 制造：保存预设Name | 高 | -  | [Craft](protocols/Craft.md) |
| 累计在线奖励 | `CumulativeTimeReward_List` | `13000` | 累计在线奖励：获取列表数据 | 中 |    | [CumulativeTimeReward](protocols/CumulativeTimeReward.md) |
| 累计在线奖励 | `CumulativeTimeReward_Reward` | `13001` | 累计在线奖励：奖励 | 中 |    | [CumulativeTimeReward](protocols/CumulativeTimeReward.md) |
| 每日记录 | `DailyRecord_Reward` | `52000` | 每日记录：奖励 | 中 |    | [DailyRecord](protocols/DailyRecord.md) |
| 编队 | `Echelon_List` | `5000` | 编队：获取列表数据 | 低 |    | [Echelon](protocols/Echelon.md) |
| 编队 | `Echelon_Save` | `5001` | 编队：保存状态 | 中 | -  | [Echelon](protocols/Echelon.md) |
| 编队 | `Echelon_PresetList` | `5002` | 编队：预设列表 | 高 |    | [Echelon](protocols/Echelon.md) |
| 编队 | `Echelon_PresetSave` | `5003` | 编队：保存预设 | 高 | -  | [Echelon](protocols/Echelon.md) |
| 编队 | `Echelon_PresetGroupRename` | `5004` | 编队：预设Group重命名 | 高 | -  | [Echelon](protocols/Echelon.md) |
| 制约解除决战 | `EliminateRaid_Login` | `45000` | 制约解除决战：进入模块并同步基础数据 | 中 |    | [EliminateRaid](protocols/EliminateRaid.md) |
| 制约解除决战 | `EliminateRaid_Lobby` | `45001` | 制约解除决战：获取或进入模块大厅 | 低 |    | [EliminateRaid](protocols/EliminateRaid.md) |
| 制约解除决战 | `EliminateRaid_OpponentList` | `45002` | 制约解除决战：获取对手列表 | 低 |    | [EliminateRaid](protocols/EliminateRaid.md) |
| 制约解除决战 | `EliminateRaid_GetBestTeam` | `45003` | 制约解除决战：获取BestTeam | 低 |    | [EliminateRaid](protocols/EliminateRaid.md) |
| 制约解除决战 | `EliminateRaid_Sweep` | `45008` | 制约解除决战：执行扫荡 | 中 | -  | [EliminateRaid](protocols/EliminateRaid.md) |
| 制约解除决战 | `EliminateRaid_SeasonReward` | `45009` | 制约解除决战：领取赛季奖励 | 中 |    | [EliminateRaid](protocols/EliminateRaid.md) |
| 制约解除决战 | `EliminateRaid_RankingReward` | `45010` | 制约解除决战：排行奖励 | 中 |    | [EliminateRaid](protocols/EliminateRaid.md) |
| 制约解除决战 | `EliminateRaid_LimitedReward` | `45011` | 制约解除决战：Limited奖励 | 中 |    | [EliminateRaid](protocols/EliminateRaid.md) |
| 制约解除决战 | `EliminateRaid_RankingIndex` | `45012` | 制约解除决战：排行Index | 低 |    | [EliminateRaid](protocols/EliminateRaid.md) |
| 装备 | `Equipment_List` | `3000` | 装备：获取列表数据 | 低 |    | [Equipment](protocols/Equipment.md) |
| 装备 | `Equipment_Sell` | `3001` | 装备：执行 Sell 流程 | 中 |    | [Equipment](protocols/Equipment.md) |
| 装备 | `Equipment_Equip` | `3002` | 装备：装备 | 低 |    | [Equipment](protocols/Equipment.md) |
| 装备 | `Equipment_LevelUp` | `3003` | 装备：提升等级 | 中 |    | [Equipment](protocols/Equipment.md) |
| 装备 | `Equipment_TierUp` | `3004` | 装备：Tier提升 | 中 |    | [Equipment](protocols/Equipment.md) |
| 装备 | `Equipment_Lock` | `3005` | 装备：执行 Lock 流程 | 中 |    | [Equipment](protocols/Equipment.md) |
| 装备 | `Equipment_BatchGrowth` | `3006` | 装备：执行 BatchGrowth 流程 | 中 |    | [Equipment](protocols/Equipment.md) |
| 活动 | `Event_GetList` | `25000` | 活动：获取列表 | 低 |    | [Event](protocols/Event.md) |
| 活动 | `Event_GetImage` | `25001` | 活动：获取Image | 低 |    | [Event](protocols/Event.md) |
| 活动 | `Event_UseCoupon` | `25002` | 活动：使用Coupon | 中 |    | [Event](protocols/Event.md) |
| 活动 | `Event_RewardIncrease` | `25003` | 活动：奖励Increase | 中 |    | [Event](protocols/Event.md) |
| 活动内容 | `EventContent_AdventureList` | `30000` | 活动内容：Adventure列表 | 低 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_EnterMainStage` | `30001` | 活动内容：进入Main关卡 | 高 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_ConfirmMainStage` | `30002` | 活动内容：ConfirmMain关卡 | 低 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_EnterSubStage` | `30005` | 活动内容：进入Sub关卡 | 高 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_DeployEchelon` | `30007` | 活动内容：布置Echelon | 高 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_WithdrawEchelon` | `30008` | 活动内容：执行 WithdrawEchelon 流程 | 高 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_MapMove` | `30009` | 活动内容：执行 MapMove 流程 | 高 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_EndTurn` | `30010` | 活动内容：执行 EndTurn 流程 | 高 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_Portal` | `30012` | 活动内容：执行 Portal 流程 | 高 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_PurchasePlayCountHardStage` | `30013` | 活动内容：PurchasePlayCountHard关卡 | 中 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_ShopList` | `30014` | 活动内容：商店列表 | 低 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_ShopRefresh` | `30015` | 活动内容：商店刷新 | 中 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_ReceiveStageTotalReward` | `30016` | 活动内容：领取关卡Total奖励 | 中 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_EnterMainGroundStage` | `30017` | 活动内容：进入MainGround关卡 | 高 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_ShopBuyMerchandise` | `30019` | 活动内容：商店购买Merchandise | 中 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_ShopBuyRefreshMerchandise` | `30020` | 活动内容：商店购买刷新Merchandise | 中 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_SelectBuff` | `30021` | 活动内容：执行 SelectBuff 流程 | 中 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_BoxGachaShopList` | `30022` | 活动内容：Box招募商店列表 | 低 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_CollectionList` | `30025` | 活动内容：Collection列表 | 低 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_CollectionForMission` | `30026` | 活动内容：CollectionFor任务 | 低 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_ScenarioGroupHistoryUpdate` | `30027` | 活动内容：剧情Group历史记录更新 | 中 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_RestartMainStage` | `30031` | 活动内容：RestartMain关卡 | 高 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_LocationGetInfo` | `30032` | 活动内容：Location获取信息 | 低 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_LocationAttendSchedule` | `30033` | 活动内容：执行 LocationAttendSchedule 流程 | 中 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_SubEventLobby` | `30035` | 活动内容：Sub活动大厅 | 低 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_EnterStoryStage` | `30036` | 活动内容：进入Story关卡 | 高 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_DiceRaceLobby` | `30038` | 活动内容：DiceRace大厅 | 低 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_DiceRaceRoll` | `30039` | 活动内容：执行 DiceRaceRoll 流程 | 高 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_DiceRaceLapReward` | `30040` | 活动内容：DiceRaceLap奖励 | 中 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_PermanentList` | `30041` | 活动内容：常驻列表 | 低 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_DiceRaceUseItem` | `30042` | 活动内容：DiceRace使用Item | 高 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_TreasureLobby` | `30044` | 活动内容：Treasure大厅 | 低 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_TreasureNextRound` | `30046` | 活动内容：执行 TreasureNextRound 流程 | 中 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_ClueSearchGetInfo` | `30051` | 活动内容：Clue搜索获取信息 | 低 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_ClueSearchSubmit` | `30052` | 活动内容：Clue搜索提交 | 中 |    | [EventContent](protocols/EventContent.md) |
| 活动内容 | `EventContent_ClueSearchRoundComplete` | `30053` | 活动内容：Clue搜索RoundComplete | 低 |    | [EventContent](protocols/EventContent.md) |
| 场景/地图互动 | `Field_Sync` | `48000` | 场景/地图互动：同步模块状态 | 中 |    | [Field](protocols/Field.md) |
| 场景/地图互动 | `Field_Interaction` | `48001` | 场景/地图互动：执行 Interaction 流程 | 中 |    | [Field](protocols/Field.md) |
| 场景/地图互动 | `Field_QuestClear` | `48002` | 场景/地图互动：Quest清空 | 中 |    | [Field](protocols/Field.md) |
| 场景/地图互动 | `Field_SceneChanged` | `48003` | 场景/地图互动：执行 SceneChanged 流程 | 中 |    | [Field](protocols/Field.md) |
| 场景/地图互动 | `Field_EndDate` | `48004` | 场景/地图互动：执行 EndDate 流程 | 中 |    | [Field](protocols/Field.md) |
| 场景/地图互动 | `Field_EnterStage` | `48005` | 场景/地图互动：进入关卡 | 低 |    | [Field](protocols/Field.md) |
| 好友 | `Friend_List` | `43000` | 好友：获取列表数据 | 低 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_Remove` | `43001` | 好友：移除咖啡厅家具 | 中 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_GetFriendDetailedInfo` | `43002` | 好友：获取FriendDetailed信息 | 低 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_GetIdCard` | `43003` | 好友：获取IdCard | 低 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_SetIdCard` | `43004` | 好友：设置IdCard | 中 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_Search` | `43005` | 好友：搜索 | 低 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_SendFriendRequest` | `43006` | 好友：SendFriend请求 | 低 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_AcceptFriendRequest` | `43007` | 好友：AcceptFriend请求 | 低 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_DeclineFriendRequest` | `43008` | 好友：DeclineFriend请求 | 低 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_CancelFriendRequest` | `43009` | 好友：取消Friend请求 | 低 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_Check` | `43010` | 好友：检查状态 | 中 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_ListByIds` | `43011` | 好友：列表ByIds | 低 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_Block` | `43012` | 好友：执行 Block 流程 | 中 |    | [Friend](protocols/Friend.md) |
| 好友 | `Friend_Unblock` | `43013` | 好友：执行 Unblock 流程 | 中 |    | [Friend](protocols/Friend.md) |
| 物品 | `Item_List` | `4000` | 物品：获取列表数据 | 低 |    | [Item](protocols/Item.md) |
| 物品 | `Item_Sell` | `4001` | 物品：执行 Sell 流程 | 中 |    | [Item](protocols/Item.md) |
| 物品 | `Item_Consume` | `4002` | 物品：执行 Consume 流程 | 中 |    | [Item](protocols/Item.md) |
| 物品 | `Item_Lock` | `4003` | 物品：执行 Lock 流程 | 中 |    | [Item](protocols/Item.md) |
| 物品 | `Item_BulkConsume` | `4004` | 物品：执行 BulkConsume 流程 | 中 |    | [Item](protocols/Item.md) |
| 物品 | `Item_SelectTicket` | `4005` | 物品：Select票据 | 低 |    | [Item](protocols/Item.md) |
| 物品 | `Item_AutoSynth` | `4006` | 物品：执行 AutoSynth 流程 | 中 |    | [Item](protocols/Item.md) |
| 邮件 | `Mail_List` | `7000` | 邮件：获取列表数据 | 低 | ✓  | [Mail](protocols/Mail.md) |
| 邮件 | `Mail_Check` | `7001` | 邮件：检查状态 | 中 | ✓  | [Mail](protocols/Mail.md) |
| 邮件 | `Mail_Receive` | `7002` | 邮件：领取奖励 | 中 | ✓  | [Mail](protocols/Mail.md) |
| 邮件 | `Mail_ListSemiPermanent` | `7003` | 邮件：列表Semi常驻 | 低 |    | [Mail](protocols/Mail.md) |
| 邮件 | `Mail_ReceiveSemiPermanent` | `7004` | 邮件：领取Semi常驻 | 中 |    | [Mail](protocols/Mail.md) |
| 经营/管理玩法 | `Management_BannerList` | `100000` | 经营/管理玩法：Banner列表 | 低 |    | [Management](protocols/Management.md) |
| 经营/管理玩法 | `Management_ProtocolLockList` | `100001` | 经营/管理玩法：ProtocolLock列表 | 低 |    | [Management](protocols/Management.md) |
| 回忆大厅 | `MemoryLobby_List` | `12000` | 回忆大厅：获取列表数据 | 低 |    | [MemoryLobby](protocols/MemoryLobby.md) |
| 回忆大厅 | `MemoryLobby_SetMain` | `12001` | 回忆大厅：设置Main | 中 | -  | [MemoryLobby](protocols/MemoryLobby.md) |
| 回忆大厅 | `MemoryLobby_UpdateLobbyMode` | `12002` | 回忆大厅：更新大厅Mode | 中 | -  | [MemoryLobby](protocols/MemoryLobby.md) |
| 回忆大厅 | `MemoryLobby_Interact` | `12003` | 回忆大厅：与咖啡厅内角色互动/摸头 | 中 | -  | [MemoryLobby](protocols/MemoryLobby.md) |
| 小游戏 | `MiniGame_StageList` | `35000` | 小游戏：关卡列表 | 低 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_EnterStage` | `35001` | 小游戏：进入关卡 | 低 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_MissionList` | `35003` | 小游戏：任务列表 | 低 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_MissionReward` | `35004` | 小游戏：任务奖励 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_MissionMultipleReward` | `35005` | 小游戏：任务Multiple奖励 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_ShootingLobby` | `35006` | 小游戏：Shooting大厅 | 低 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_ShootingSweep` | `35009` | 小游戏：执行 ShootingSweep 流程 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_TableBoardSync` | `35010` | 小游戏：TableBoard同步 | 低 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_TableBoardMove` | `35011` | 小游戏：执行 TableBoardMove 流程 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_TableBoardEncounterInput` | `35012` | 小游戏：执行 TableBoardEncounterInput 流程 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_TableBoardClearThema` | `35015` | 小游戏：TableBoard清空Thema | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_TableBoardUseItem` | `35016` | 小游戏：TableBoard使用Item | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_TableBoardResurrect` | `35017` | 小游戏：执行 TableBoardResurrect 流程 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_TableBoardSweep` | `35018` | 小游戏：执行 TableBoardSweep 流程 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_TableBoardMoveThema` | `35019` | 小游戏：执行 TableBoardMoveThema 流程 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_DreamMakerGetInfo` | `35020` | 小游戏：DreamMaker获取信息 | 低 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_DreamMakerNewGame` | `35021` | 小游戏：DreamMakerNew游戏 | 高 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_DreamMakerRestart` | `35022` | 小游戏：执行 DreamMakerRestart 流程 | 高 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_DreamMakerAttendSchedule` | `35023` | 小游戏：执行 DreamMakerAttendSchedule 流程 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_DreamMakerDailyClosing` | `35024` | 小游戏：执行 DreamMakerDailyClosing 流程 | 高 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_DreamMakerEnding` | `35025` | 小游戏：执行 DreamMakerEnding 流程 | 高 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_DefenseGetInfo` | `35026` | 小游戏：Defense获取信息 | 低 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_RoadPuzzleGetInfo` | `35029` | 小游戏：RoadPuzzle获取信息 | 低 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_RoadPuzzleTilePlace` | `35030` | 小游戏：执行 RoadPuzzleTilePlace 流程 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_RoadPuzzleSaveStage` | `35031` | 小游戏：RoadPuzzle保存关卡 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_RoadPuzzleClearStage` | `35032` | 小游戏：RoadPuzzle清空关卡 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_CCGLobby` | `35033` | 小游戏：CCG大厅 | 低 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_CCGCreateGame` | `35034` | 小游戏：CCG创建游戏 | 低 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_CCGSweep` | `35035` | 小游戏：执行 CCGSweep 流程 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_CCGEnterStage` | `35036` | 小游戏：CCG进入关卡 | 低 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_CCGSelectCampAction` | `35041` | 小游戏：执行 CCGSelectCampAction 流程 | 中 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `MiniGame_CCGGiveupGame` | `35043` | 小游戏：CCGGiveup游戏 | 低 |    | [MiniGame](protocols/MiniGame.md) |
| 小游戏 | `Minigame_CCGReplaceCharacter` | `35040` | 小游戏：CCGReplace角色 | 低 |    | [Minigame](protocols/Minigame_protocols.md) |
| 任务 | `Mission_List` | `8000` | 任务：获取列表数据 | 低 | ✓  | [Mission](protocols/Mission.md) |
| 任务 | `Mission_Reward` | `8001` | 任务：奖励 | 中 | ✓  | [Mission](protocols/Mission.md) |
| 任务 | `Mission_MultipleReward` | `8002` | 任务：Multiple奖励 | 中 | ✓  | [Mission](protocols/Mission.md) |
| 任务 | `Mission_GuideReward` | `8003` | 任务：Guide奖励 | 中 |    | [Mission](protocols/Mission.md) |
| 任务 | `Mission_MultipleGuideReward` | `8004` | 任务：MultipleGuide奖励 | 中 |    | [Mission](protocols/Mission.md) |
| 任务 | `Mission_Sync` | `8005` | 任务：同步模块状态 | 中 |    | [Mission](protocols/Mission.md) |
| 任务 | `Mission_GuideMissionSeasonList` | `8006` | 任务：Guide任务赛季列表 | 低 |    | [Mission](protocols/Mission.md) |
| MomoTalk | `MomoTalk_OutLine` | `33000` | MomoTalk：执行 OutLine 流程 | 中 | ✓  | [MomoTalk](protocols/MomoTalk.md) |
| MomoTalk | `MomoTalk_MessageList` | `33001` | MomoTalk：Message列表 | 低 | ✓  | [MomoTalk](protocols/MomoTalk.md) |
| MomoTalk | `MomoTalk_Read` | `33002` | MomoTalk：读取内容 | 低 | ✓  | [MomoTalk](protocols/MomoTalk.md) |
| MomoTalk | `MomoTalk_Reply` | `33003` | MomoTalk：执行 Reply 流程 | 中 | -  | [MomoTalk](protocols/MomoTalk.md) |
| MomoTalk | `MomoTalk_FavorSchedule` | `33004` | MomoTalk：执行 FavorSchedule 流程 | 中 | ✓  | [MomoTalk](protocols/MomoTalk.md) |
| 多层总力战 | `MultiFloorRaid_Sync` | `49000` | 多层总力战：同步模块状态 | 中 |    | [MultiFloorRaid](protocols/MultiFloorRaid.md) |
| 多层总力战 | `MultiFloorRaid_ReceiveReward` | `49003` | 多层总力战：领取奖励 | 中 |    | [MultiFloorRaid](protocols/MultiFloorRaid.md) |
| 多层总力战 | `MultiFloorRaid_Login` | `49004` | 多层总力战：进入模块并同步基础数据 | 中 |    | [MultiFloorRaid](protocols/MultiFloorRaid.md) |
| 网络时间 | `NetworkTime_Sync` | `3` | 网络时间：同步模块状态 | 中 |    | [NetworkTime](protocols/NetworkTime.md) |
| 网络时间 | `NetworkTime_SyncReply` | `4` | 网络时间：同步Reply | 低 |    | [NetworkTime](protocols/NetworkTime.md) |
| 占位协议 | `None` | `0` | 占位协议：模块占位或基础协议 | 低 |    | [None](protocols/None.md) |
| 通知 | `Notification_LobbyCheck` | `36000` | 通知：大厅检查 | 中 | -  | [Notification](protocols/Notification.md) |
| 通知 | `Notification_EventContentReddotCheck` | `36001` | 通知：活动内容Reddot检查 | 中 |    | [Notification](protocols/Notification.md) |
| 开放条件 | `OpenCondition_List` | `15000` | 开放条件：获取列表数据 | 中 |    | [OpenCondition](protocols/OpenCondition.md) |
| 开放条件 | `OpenCondition_Set` | `15001` | 开放条件：设置 | 中 |    | [OpenCondition](protocols/OpenCondition.md) |
| 开放条件 | `OpenCondition_EventList` | `15002` | 开放条件：活动列表 | 中 |    | [OpenCondition](protocols/OpenCondition.md) |
| 设置 | `Option_Save` | `53000` | 设置：保存状态 | 中 |    | [Option](protocols/Option.md) |
| 常驻总力战 | `PermanentRaid_Lobby` | `54000` | 常驻总力战：获取或进入模块大厅 | 低 |    | [PermanentRaid](protocols/PermanentRaid.md) |
| ProofToken 验证 | `ProofToken_RequestQuestion` | `37000` | ProofToken 验证：请求 ProofToken 问题 | 高 | ✓  | [ProofToken](protocols/ProofToken.md) |
| ProofToken 验证 | `ProofToken_Submit` | `37001` | ProofToken 验证：提交 ProofToken 答案 | 高 | ✓  | [ProofToken](protocols/ProofToken.md) |
| 排队/网关票据 | `Queuing_GetTicket` | `50000` | 排队/网关票据：获取进入游戏网关所需票据 | 高 | ✓  | [Queuing](protocols/Queuing.md) |
| 排队/网关票据 | `Queuing_GetCryptoKeys` | `50001` | 排队/网关票据：获取CryptoKeys | 低 | ✓  | [Queuing](protocols/Queuing.md) |
| 排队/网关票据 | `Queuing_GetAuthTicket` | `50002` | 排队/网关票据：获取Auth票据 | 低 | ✓  | [Queuing](protocols/Queuing.md) |
| 排队/网关票据 | `Queuing_ProcessWaitingQueue` | `50003` | 排队/网关票据：执行 ProcessWaitingQueue 流程 | 中 | ✓  | [Queuing](protocols/Queuing.md) |
| 总力战 | `Raid_List` | `17000` | 总力战：获取列表数据 | 低 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_CompleteList` | `17001` | 总力战：Complete列表 | 低 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_Detail` | `17002` | 总力战：执行 Detail 流程 | 中 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_Search` | `17003` | 总力战：搜索 | 低 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_BattleUpdate` | `17006` | 总力战：战斗更新 | 高 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_Reward` | `17008` | 总力战：奖励 | 中 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_RewardAll` | `17009` | 总力战：奖励全部 | 中 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_Revive` | `17010` | 总力战：执行 Revive 流程 | 高 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_Share` | `17011` | 总力战：执行 Share 流程 | 中 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_SeasonInfo` | `17012` | 总力战：赛季信息 | 低 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_SeasonReward` | `17013` | 总力战：领取赛季奖励 | 中 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_Lobby` | `17014` | 总力战：获取或进入模块大厅 | 低 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_OpponentList` | `17016` | 总力战：获取对手列表 | 低 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_RankingReward` | `17017` | 总力战：排行奖励 | 中 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_Login` | `17018` | 总力战：进入模块并同步基础数据 | 中 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_Sweep` | `17019` | 总力战：执行扫荡 | 中 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_GetBestTeam` | `17020` | 总力战：获取BestTeam | 低 |    | [Raid](protocols/Raid.md) |
| 总力战 | `Raid_RankingIndex` | `17021` | 总力战：排行Index | 低 |    | [Raid](protocols/Raid.md) |
| 配方 | `Recipe_Craft` | `11000` | 配方：执行 Craft 流程 | 中 |    | [Recipe](protocols/Recipe.md) |
| 可重置内容 | `ResetableContent_Get` | `41000` | 可重置内容：获取数据 | 高 |    | [ResetableContent](protocols/ResetableContent.md) |
| 剧情 | `Scenario_List` | `19000` | 剧情：获取列表数据 | 低 |    | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_GroupHistoryUpdate` | `19002` | 剧情：Group历史记录更新 | 中 | -  | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_Skip` | `19003` | 剧情：执行 Skip 流程 | 中 | -  | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_Select` | `19004` | 剧情：执行 Select 流程 | 中 | -  | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_AccountStudentChange` | `19005` | 剧情：执行 AccountStudentChange 流程 | 中 | -  | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_LobbyStudentChange` | `19006` | 剧情：大厅StudentChange | 低 | -  | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_SpecialLobbyChange` | `19007` | 剧情：Special大厅Change | 低 | -  | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_Enter` | `19008` | 剧情：进入对应功能入口 | 低 | -  | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_EnterMainStage` | `19009` | 剧情：进入Main关卡 | 高 |    | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_ConfirmMainStage` | `19010` | 剧情：ConfirmMain关卡 | 低 |    | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_DeployEchelon` | `19011` | 剧情：布置Echelon | 高 |    | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_WithdrawEchelon` | `19012` | 剧情：执行 WithdrawEchelon 流程 | 高 |    | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_MapMove` | `19013` | 剧情：执行 MapMove 流程 | 高 |    | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_EndTurn` | `19014` | 剧情：执行 EndTurn 流程 | 高 |    | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_Portal` | `19018` | 剧情：执行 Portal 流程 | 高 |    | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_RestartMainStage` | `19019` | 剧情：RestartMain关卡 | 高 |    | [Scenario](protocols/Scenario.md) |
| 剧情 | `Scenario_SkipMainStage` | `19020` | 剧情：SkipMain关卡 | 低 |    | [Scenario](protocols/Scenario.md) |
| 学院交流会 | `SchoolDungeon_List` | `38000` | 学院交流会：获取列表数据 | 低 |    | [SchoolDungeon](protocols/SchoolDungeon.md) |
| 会话 | `Session_Info` | `2` | 会话：信息 | 低 |    | [Session](protocols/Session.md) |
| 商店/招募 | `Shop_BuyMerchandise` | `10000` | 商店/招募：购买商店商品 | 中 |    | [Shop](protocols/Shop.md) |
| 商店/招募 | `Shop_List` | `10002` | 商店/招募：获取列表数据 | 低 | ✓  | [Shop](protocols/Shop.md) |
| 商店/招募 | `Shop_Refresh` | `10003` | 商店/招募：刷新数据或商店内容 | 中 |    | [Shop](protocols/Shop.md) |
| 商店/招募 | `Shop_BuyEligma` | `10004` | 商店/招募：购买神名精髓相关商品 | 中 |    | [Shop](protocols/Shop.md) |
| 商店/招募 | `Shop_GachaRecruitList` | `10006` | 商店/招募：获取招募列表 | 低 |    | [Shop](protocols/Shop.md) |
| 商店/招募 | `Shop_BuyRefreshMerchandise` | `10007` | 商店/招募：购买刷新商品 | 中 |    | [Shop](protocols/Shop.md) |
| 商店/招募 | `Shop_BuyAP` | `10009` | 商店/招募：购买 AP | 中 | ✓  | [Shop](protocols/Shop.md) |
| 商店/招募 | `Shop_BeforehandGachaGet` | `10010` | 商店/招募：Beforehand招募获取 | 低 |    | [Shop](protocols/Shop.md) |
| 商店/招募 | `Shop_PickupSelectionGachaGet` | `10014` | 商店/招募：获取自选 Pickup 招募状态 | 低 |    | [Shop](protocols/Shop.md) |
| 扫荡历史 | `SkipHistory_List` | `18000` | 扫荡历史：获取列表数据 | 中 |    | [SkipHistory](protocols/SkipHistory.md) |
| 扫荡历史 | `SkipHistory_Save` | `18001` | 扫荡历史：保存状态 | 中 |    | [SkipHistory](protocols/SkipHistory.md) |
| 贴纸 | `Sticker_Login` | `47000` | 贴纸：进入模块并同步基础数据 | 中 |    | [Sticker](protocols/Sticker.md) |
| 贴纸 | `Sticker_Lobby` | `47001` | 贴纸：获取或进入模块大厅 | 低 |    | [Sticker](protocols/Sticker.md) |
| 贴纸 | `Sticker_UseSticker` | `47002` | 贴纸：使用贴纸 | 中 | -  | [Sticker](protocols/Sticker.md) |
| 系统 | `System_Version` | `1` | 系统：获取系统版本 | 低 |    | [System](protocols/System.md) |
| 语音/假名 | `TTS_GetFile` | `31000` | 语音/假名：获取文件 | 低 | -  | [TTS](protocols/TTS.md) |
| 语音/假名 | `TTS_GetKana` | `31001` | 语音/假名：获取假名/读音数据 | 低 |  -  | [TTS](protocols/TTS.md) |
| 综合战术考试 | `TimeAttackDungeon_Lobby` | `39000` | 综合战术考试：获取或进入模块大厅 | 中 |    | [TimeAttackDungeon](protocols/TimeAttackDungeon.md) |
| 综合战术考试 | `TimeAttackDungeon_Sweep` | `39004` | 综合战术考试：执行扫荡 | 中 |    | [TimeAttackDungeon](protocols/TimeAttackDungeon.md) |
| 综合战术考试 | `TimeAttackDungeon_Login` | `39006` | 综合战术考试：进入模块并同步基础数据 | 中 |    | [TimeAttackDungeon](protocols/TimeAttackDungeon.md) |
| Toast 提示 | `Toast_List` | `16000` | Toast 提示：获取列表数据 | 低 |    | [Toast](protocols/Toast.md) |
| 悬赏通缉/日常副本 | `WeekDungeon_List` | `23000` | 悬赏通缉/日常副本：获取列表数据 | 低 | ✓  | [WeekDungeon](protocols/WeekDungeon.md) |
| 世界 Raid | `WorldRaid_Lobby` | `40000` | 世界 Raid：获取或进入模块大厅 | 低 |    | [WorldRaid](protocols/WorldRaid.md) |
| 世界 Raid | `WorldRaid_BossList` | `40001` | 世界 Raid：Boss列表 | 低 |    | [WorldRaid](protocols/WorldRaid.md) |
| 世界 Raid | `WorldRaid_ReceiveReward` | `40004` | 世界 Raid：领取奖励 | 中 |    | [WorldRaid](protocols/WorldRaid.md) |
| 世界 Raid | `WorldRaid_UpdateCarrierSkill` | `40005` | 世界 Raid：更新CarrierSkill | 中 |    | [WorldRaid](protocols/WorldRaid.md) |
