# Mission 协议

任务模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 每日任务影响

`Mission_List`、`Mission_Reward`、`Mission_MultipleReward` 可用于读取每日任务进度并领取已经完成的任务奖励。

这些协议只处理任务列表与领奖，不负责完成战斗、竞技场、学园交流会等任务条件。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Mission_List` | `8000` | 任务：获取列表数据 | `MissionListRequest` | `MissionListResponse` |
| `Mission_Reward` | `8001` | 任务：奖励 | `MissionRewardRequest` | `MissionRewardResponse` |
| `Mission_MultipleReward` | `8002` | 任务：Multiple奖励 | `MissionMultipleRewardRequest` | `MissionMultipleRewardResponse` |
| `Mission_GuideReward` | `8003` | 任务：Guide奖励 | `` | `` |
| `Mission_MultipleGuideReward` | `8004` | 任务：MultipleGuide奖励 | `` | `` |
| `Mission_Sync` | `8005` | 任务：同步模块状态 | `MissionSyncRequest` | `MissionSyncResponse` |
| `Mission_GuideMissionSeasonList` | `8006` | 任务：Guide任务赛季列表 | `GuideMissionSeasonListRequest` | `GuideMissionSeasonListResponse` |

## 字段结构参考

### Mission_List

- 协议号：`8000`
- 作用：任务：获取列表数据
- RequestClass：`MissionListRequest`
- ResponseClass：`MissionListResponse`
- 状态：SDK 已封装并通过 live 只读验证。

#### SDK 方法

```python
missions = await client.mission.list()
```

返回结构：

| 字段 | 说明 |
| --- | --- |
| `mission_history_unique_ids` | 已领取/历史任务 ID 列表。 |
| `progress` | 当前任务进度列表。 |
| `daily_sudden_mission_info` | 每日突发任务信息。 |
| `cleared_original_mission_ids` | 已清理原始任务 ID 列表。 |
| `extra` | 服务端返回中的其他顶层字段。 |

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `Nullable<long>` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MissionHistoryUniqueIds` | `List<long>?` | ID 列表。 |
| `ProgressDBs` | `List<MissionProgressDB>?` | Progress 数据列表。 |
| `DailySuddenMissionInfo` | `object?` | 每日突发任务信息。 |
| `ClearedOrignalMissionIds` | `List<long>?` | ID 列表。 |

### Mission_Reward

- 协议号：`8001`
- 作用：任务：奖励
- RequestClass：`MissionRewardRequest`
- ResponseClass：`MissionRewardResponse`
- 状态：SDK 已封装；当前小号 live 测试中 `Mission_List` 可读，但 `Mission_Reward` 返回 `ErrorCode=1032 NexonNgsmValidateFail`，暂不视为稳定可领奖入口。

#### SDK 方法

```python
reward = await client.mission.reward(mission_unique_id)
```

`reward()` 只领取调用方显式指定且已经完成的任务奖励，不会完成任务，也不会自动领取全部每日任务。默认会先调用 `Mission_List` 确认任务存在且已完成，再发送领奖请求。

返回结构：

| 字段 | 说明 |
| --- | --- |
| `added_history` | 本次新增的任务历史记录。 |
| `mission_progress` | 服务端随领奖返回的任务进度更新列表。 |
| `parcel_result` | 奖励或道具变更结果。 |
| `extra` | 服务端返回中的其他顶层字段。 |

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MissionUniqueId` | `long` | 任务唯一 ID。 |
| `ProgressServerId` | `long` | Progress服务器 ID。 |
| `EventContentId` | `Nullable<long>` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AddedHistoryDB` | `MissionHistoryDB?` | Added历史数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Mission_MultipleReward

- 协议号：`8002`
- 作用：任务：Multiple奖励
- RequestClass：`MissionMultipleRewardRequest`
- ResponseClass：`MissionMultipleRewardResponse`
- 状态：SDK 已封装；调用前会先读取 `Mission_List`，确认存在已完成任务后再领取指定分类奖励。当前小号 live 测试中 `Mission_MultipleReward("daily")` 返回 `ErrorCode=1032 NexonNgsmValidateFail`，暂不视为稳定可领奖入口。
#### SDK 方法

```python
reward = await client.mission.multiple_reward("daily")
```

`daily` 对应每日任务分类；外部仍负责决定何时调用，SDK 不封装一键每日流程。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MissionCategory` | `MissionCategory` | 任务分类。 |
| `GuideMissionSeasonId` | `Nullable<long>` | Guide任务赛季 ID。 |
| `EventContentId` | `Nullable<long>` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AddedHistoryDBs` | `List<MissionHistoryDB>?` | AddedHistory 数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Mission_GuideReward

- 协议号：`8003`
- 作用：任务：Guide奖励
- RequestClass：``
- ResponseClass：``
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Mission_MultipleGuideReward

- 协议号：`8004`
- 作用：任务：MultipleGuide奖励
- RequestClass：``
- ResponseClass：``
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Mission_Sync

- 协议号：`8005`
- 作用：任务：同步模块状态
- RequestClass：`MissionSyncRequest`
- ResponseClass：`MissionSyncResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Mission_GuideMissionSeasonList

- 协议号：`8006`
- 作用：任务：Guide任务赛季列表
- RequestClass：`GuideMissionSeasonListRequest`
- ResponseClass：`GuideMissionSeasonListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `GuideMissionSeasonDBs` | `List<GuideMissionSeasonDB>?` | GuideMissionSeason 数据列表。 |
