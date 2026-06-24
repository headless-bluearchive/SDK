# BattlePass 协议

战斗通行证模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `BattlePass_GetInfo` | `51000` | 战斗通行证：获取模块信息 | `BattlePassGetInfoRequest` | `BattlePassGetInfoResponse` |
| `BattlePass_BuyLevel` | `51001` | 战斗通行证：购买Level | `BattlePassBuyLevelRequest` | `BattlePassBuyLevelResponse` |
| `BattlePass_ReceiveReward` | `51002` | 战斗通行证：领取奖励 | `BattlePassReceiveRewardRequest` | `BattlePassReceiveRewardResponse` |
| `BattlePass_MissionList` | `51003` | 战斗通行证：任务列表 | `BattlePassMissionListRequest` | `BattlePassMissionListResponse` |
| `BattlePass_MissionSingleReward` | `51004` | 战斗通行证：任务Single奖励 | `BattlePassMissionSingleRewardRequest` | `BattlePassMissionSingleRewardResponse` |
| `BattlePass_MissionMultipleReward` | `51005` | 战斗通行证：任务Multiple奖励 | `BattlePassMissionMultipleRewardRequest` | `BattlePassMissionMultipleRewardResponse` |
| `BattlePass_Check` | `51006` | 战斗通行证：检查领取状态 | `BattlePassCheckRequest` | `BattlePassCheckResponse` |

## 字段结构参考

### BattlePass_GetInfo

- 协议号：`51000`
- 作用：战斗通行证：获取模块信息
- RequestClass：`BattlePassGetInfoRequest`
- ResponseClass：`BattlePassGetInfoResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BattlePassId` | `long` | 战斗Pass ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BattlePassInfo` | `BattlePassInfoDB?` | 战斗Pass信息数据。 |

### BattlePass_BuyLevel

- 协议号：`51001`
- 作用：战斗通行证：购买Level
- RequestClass：`BattlePassBuyLevelRequest`
- ResponseClass：`BattlePassBuyLevelResponse`
- 状态：SDK 已封装为战斗通行证页面的领取状态读取方法，不会自动领取奖励。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BattlePassId` | `long` | 战斗Pass ID。 |
| `BattlePassBuyLevelCount` | `int` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BattlePassInfo` | `BattlePassInfoDB?` | 战斗Pass信息数据。 |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |

### BattlePass_ReceiveReward

- 协议号：`51002`
- 作用：战斗通行证：领取奖励
- RequestClass：`BattlePassReceiveRewardRequest`
- ResponseClass：`BattlePassReceiveRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BattlePassId` | `long` | 战斗Pass ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BattlePassInfo` | `BattlePassInfoDB?` | 战斗Pass信息数据。 |
| `ParcelResult` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### BattlePass_MissionList

- 协议号：`51003`
- 作用：战斗通行证：任务列表
- RequestClass：`BattlePassMissionListRequest`
- ResponseClass：`BattlePassMissionListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BattlePassId` | `long` | 战斗Pass ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MissionHistoryUniqueIds` | `List<long>?` | ID 列表。 |
| `ProgressDBs` | `List<MissionProgressDB>?` | Progress 数据列表。 |

### BattlePass_MissionSingleReward

- 协议号：`51004`
- 作用：战斗通行证：任务Single奖励
- RequestClass：`BattlePassMissionSingleRewardRequest`
- ResponseClass：`BattlePassMissionSingleRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BattlePassId` | `long` | 战斗Pass ID。 |
| `MissionUniqueId` | `long` | 任务唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AddedHistoryDB` | `MissionHistoryDB?` | Added历史数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `BattlePassInfo` | `BattlePassInfoDB?` | 战斗Pass信息数据。 |

### BattlePass_MissionMultipleReward

- 协议号：`51005`
- 作用：战斗通行证：任务Multiple奖励
- RequestClass：`BattlePassMissionMultipleRewardRequest`
- ResponseClass：`BattlePassMissionMultipleRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MissionCategory` | `MissionCategory` | 任务分类。 |
| `BattlePassId` | `long` | 战斗Pass ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AddedHistoryDBs` | `List<MissionHistoryDB>?` | AddedHistory 数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `BattlePassInfo` | `BattlePassInfoDB?` | 战斗Pass信息数据。 |

### BattlePass_Check

- 协议号：`51006`
- 作用：战斗通行证：检查状态
- RequestClass：`BattlePassCheckRequest`
- ResponseClass：`BattlePassCheckResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BattlePassId` | `long` | 战斗Pass ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `HasNotReceiveReward` | `bool` | 当前页面是否还有未领取奖励。 |
| `HasCompleteMission` | `bool` | 当前页面是否已经完成对应任务。 |

SDK 侧对应 `client.battle_pass.get_info(battle_pass_id)` / `mission_list(battle_pass_id)` / `check(battle_pass_id)`，用于读取战斗通行证页面、任务和领取状态，不会自动领取奖励。

当前登录链路里如果能提前知道赛季 ID，也可以在登录时传 `session_bootstrap_battle_pass_id`，让登录阶段顺带同步一次。`battle_pass_id` 不要手填成通用常量。
