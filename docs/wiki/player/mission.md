# 任务页面

这一页对应游戏里的任务页：每日、每周、成就、活动和指南任务。SDK 可读取任务进度、领取已完成任务的奖励，但不会代替用户完成战斗、竞技场、小游戏结算等任务条件。

能看什么：所有任务的进度和红点状态、指南任务赛季。
能做什么：领取单个已完成任务、按分类批量领取（都会改账号资源）。

## SDK 入口

只读（不改账号）：

| 方法 | 用途 | 返回 |
| --- | --- | --- |
| `client.mission.list(*, event_content_id=None)` | 任务列表与进度；传活动 ID 看活动任务。 | 整理后的 dict |
| `client.mission.guide_season_list()` | 指南任务/新手任务赛季列表。 | 整理后的 dict |
| `client.mission.sync()` | 同步任务状态。 | 服务端原始负载 |

领奖（改账号资源，无 `confirm`，由 `validate=True` 守卫）：

| 方法 | 用途 |
| --- | --- |
| `client.mission.reward(mission_unique_id, *, progress_server_id=None, event_content_id=None, validate=True)` | 领取单个已完成任务。 |
| `client.mission.multiple_reward(mission_category, *, event_content_id=None, guide_mission_season_id=None, validate=True)` | 按分类批量领取。 |

## 任务列表

```python
missions = await client.mission.list()
```

看某个活动的任务时传活动内容 ID：

```python
missions = await client.mission.list(event_content_id=event_content_id)
```

| 参数 | 游戏含义 |
| --- | --- |
| `event_content_id` | 活动任务所属活动 ID；普通每日/每周/成就任务不传。 |

返回 SDK 整理后的 dict：业务字段（`progress` 当前任务进度、`mission_history_unique_ids` 历史、`daily_sudden_mission_info`、`cleared_original_mission_ids`）加 `extra`。

```python
missions = await client.mission.list()
completed = [item for item in missions["progress"] if item.get("Complete") is True]
```

每日签到、课程表、咖啡厅摸头等完成后，`progress` 里可能出现新的 `Complete=True` 项。

## 领取单个任务

对应点击某一条已完成任务的领取按钮。

```python
result = await client.mission.reward(mission_unique_id)
```

活动任务或服务端需要明确进度记录时：

```python
result = await client.mission.reward(
    mission_unique_id,
    progress_server_id=progress_server_id,
    event_content_id=event_content_id,
)
```

| 参数 | 游戏含义 |
| --- | --- |
| `mission_unique_id` | 任务 ID，来自 `progress`。 |
| `progress_server_id` | 进度记录 ID，通常来自同一条 `progress`。 |
| `event_content_id` | 活动任务所属活动 ID。 |
| `validate` | 默认 `True`，会先读任务列表确认任务存在且 `Complete=True`。 |

返回 SDK 整理后的 dict：`added_history`、`mission_progress`、`parcel_result` 加 `extra`。

## 按分类批量领取

对应任务页里按分类一键领取。

```python
result = await client.mission.multiple_reward("daily")
```

`mission_category` 接受分类名字符串或对应整数，常用值：

| 参数值 | 游戏里对应 |
| --- | --- |
| `"daily"` | 每日任务 |
| `"weekly"` | 每周任务 |
| `"achievement"` | 成就任务 |
| `"guide"` / `"guide_mission"` | 指南任务 |
| `"event_achievement"` | 活动成就任务 |
| `"event_fixed"` | 活动固定任务 |

代码里还登记了 `challenge`、`all`、`mini_game_score`、`mini_game_event`、`daily_sudden`、`daily_fixed` 等分类，完整映射以 `service.py` 里的 `MISSION_CATEGORIES` 为准。

返回 SDK 整理后的 dict：`added_histories`、`mission_progress`、`parcel_result` 加 `extra`。默认 `validate=True` 会先读任务列表，确认至少有一项已完成任务再发领奖请求。

## 指南任务赛季

```python
seasons = await client.mission.guide_season_list()
```

返回 SDK 整理后的 dict：`guide_mission_seasons` 加 `count` 加 `extra`。

## 注意

- `reward` / `multiple_reward` 没有 `confirm` 参数，由 `validate=True` 守卫：任务不存在、未完成、或没有任何已完成任务时抛 `UnsafeOperationError` 且不发包。
- 任务领奖可能遇到 NGS 校验差异，服务端返回 `1032 NexonNgsmValidateFail` 时应视为可预期的账号 / 环境校验失败，而非单纯的参数错误。
- `mission_unique_id`、`progress_server_id`、`event_content_id`、赛季 ID 等一律来自当前账号可见数据（`mission.list()` / `guide_season_list()`），不要手填。
- 逐协议接入状态见仓库根 `docs/protocols.md`。
