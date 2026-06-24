# 玩家文档总览

本组文档按游戏内的功能页组织，而非按协议名罗列。每页说明对应的游戏功能、可查询的内容、需要传入的参数、返回结果的大致结构，以及相关的显式确认要求或前置条件。

## 只读页面（打开看状态，不改账号）

- [账号和基础状态](game-account.md) — 资源栏、货币同步、教程进度、账号等级奖励状态
- [通用只读页面](game-readonly.md) — 学生、编队、仓库、剧情、交流会等基础查询
- [好友、社团、活动、Raid、贴纸等扩展只读](readonly-extended.md) — 好友、社团、活动、总力战/大决战/多层/世界 Raid、贴纸、通关编队、开放条件、综合战术考试、红点、语音、服务器时间等
- [商店和招募页面](shop.md) — 商店状态、AP 补充、预抽卡和 Pickup 展示
- [咖啡厅](cafe.md) / [任务](mission.md) / [战斗通行证](battle-pass.md) / [课程表](academy.md) / [MomoTalk](momotalk.md) — 各功能页状态
- [邮件](mail.md) / [签到](attendance.md) / [充值与购买状态](billing.md) / [扫荡](sweep.md) — 邮件、签到、购买状态快照、扫荡

## 显式确认变更页面（需 `confirm=True`）

- [显式确认变更页面](state-changing.md) — 游戏里“真正点下去”的操作，按风险分档：**领取奖励**、**设置/偏好**（不消耗资源）、**养成/消耗**（消耗石/材料）、**破坏性/社团**（不可逆）。全部强制 `confirm=True`，不传则抛 `UnsafeOperationError` 且不发请求。

## 不知道某个参数填什么？

枚举值（ContentType / StageDifficulty / ShopCategoryType / EchelonType / SkillSlot …）和需要自己拼的复杂对象（ConsumeRequestDB / OptionDB 等）的取值与来源，统一见 [参数取值参考](../reference.md)。

## 说明

- 会消耗资源或改变状态的入口默认不会执行，必须显式 `confirm=True`，否则抛 `UnsafeOperationError` 且不发请求。
- 只读方法的返回值按该方法源码里是否有 `format_*` 区分：经过整理的返回“业务字段 + `count` + `extra`”的 dict，未整理的直接返回服务端原始负载。具体形状以各页说明和当前 `service.py` 为准，不要按某个固定键名集合硬编码。
- 涉及活动、赛季、关卡或队伍 ID 的内容，一律以当前账号可见页面或游戏数据为准，不要手填。
- 逐协议接入状态见仓库根 `docs/protocols.md`，本文档不写死协议数量。
- SDK 的功能边界见[调用教程总览的公平边界](../README.md#公平边界)。
