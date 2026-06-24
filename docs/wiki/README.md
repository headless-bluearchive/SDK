# 调用教程

本文档面向外部调用方，说明 `Client` 的登录方式、session 的保存与恢复、各模块的调用方法，以及使用上的边界。

## 基础

- [功能完成度](features.md) — 已封装功能一览 + 需 `confirm=True` 的状态变更分档
- [登录鉴权](base/auth.md) — 实例化 `Client`、登录、保存/恢复 `session` 与 `profile`
- [官方资源数据](base/official-data.md) — 同步 TableBundles 主数据，给只读计算提供依据
- [参数取值参考](reference.md) — **所有需要自己填的枚举值和复杂对象**（ContentType / StageDifficulty / ShopCategoryType 等数值、以及 ConsumeRequestDB/OptionDB 等结构与来源）
- [示例代码](example/README.md) — 可直接运行的完整示例（如[完成每日任务全流程](example/complete_daily_tasks.py)）
- [错误对照](../error.md) — 常见异常与处理建议

## 公平边界

SDK 只提供“查看页面状态”和少量需要显式确认的日常操作，不提供任何会影响游戏公平性的链路。以下内容不在 SDK 范围内：

- 战斗进入 / 战斗结算 / 成绩提交
- 竞技场对战
- 小游戏对局 / 小游戏结算
- 抽卡购买 / 抽卡保存
- 支付下单
- 风控（XignCode 等）上报
- 账号危险操作（注销、解绑、重置等）

## 游戏功能调用

入口总览见 [游戏功能调用总览](player/README.md)。所有功能页按“读”和“写”分两类。

### 只读页面（打开看状态，不改账号）

- [账号资源](player/game-account.md)
- [学生、主线、日常副本和扫荡](player/game-readonly.md)
- [好友、社团、活动、Raid、贴纸等扩展只读](player/readonly-extended.md)
- [商店、AP 补充和招募状态](player/shop.md)
- [扫荡预设](player/sweep.md)
- [签到](player/attendance.md) · [咖啡厅](player/cafe.md) · [任务](player/mission.md) · [战斗通行证](player/battle-pass.md) · [课程表](player/academy.md) · [MomoTalk](player/momotalk.md)
- [邮件](player/mail.md) · [充值与购买状态](player/billing.md)

### 显式确认变更（需 `confirm=True`）

- [显式确认变更页面](player/state-changing.md) — 领取奖励 / 设置·偏好 / 养成·消耗 / 破坏性·社团，全部强制 `confirm=True`，不传则抛 `UnsafeOperationError` 且不发请求。

## 协议接入状态

逐协议的接入与完成情况见仓库根 [`docs/protocols.md`](../protocols.md)。本 wiki 不写死协议数量，方法清单一律以各模块 `service.py` 当前代码为准。
