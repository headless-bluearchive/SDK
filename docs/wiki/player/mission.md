# 任务

这一页对应游戏里的任务页面：每日任务、每周任务、成就任务、活动任务和指南任务。SDK 可以读取任务进度，也可以领取已经完成的任务奖励；它不会帮用户完成战斗、竞技场、小游戏结算等任务条件。

## 任务列表

对应打开任务页面后看到的所有任务进度和红点状态。

```python
missions = await client.mission.list()
```

查看某个活动的任务时传活动内容 ID：

```python
missions = await client.mission.list(event_content_id=event_content_id)
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `event_content_id` | 活动任务所属活动 ID；普通每日/每周/成就任务不需要传。 |

返回结构：

```python
{
    "mission_history_unique_ids": [...],  # 已领取/已完成历史
    "progress": [...],                    # 当前任务进度，对应 ProgressDBs
    "daily_sudden_mission_info": {...},   # 每日突发任务信息
    "cleared_original_mission_ids": [...],
    "extra": {},
}
```

常见用法：

```python
missions = await client.mission.list()
completed = [
    item
    for item in missions["progress"]
    if item.get("Complete") is True
]
```

每日签到、课程表、咖啡厅摸头等操作完成后，任务列表里可能会出现新的 `Complete=True` 项。

## 领取单个任务

对应游戏里点击某一条已完成任务的领取按钮。

```python
result = await client.mission.reward(mission_unique_id)
```

如果是活动任务或服务端需要明确进度记录，可以传：

```python
result = await client.mission.reward(
    mission_unique_id,
    progress_server_id=progress_server_id,
    event_content_id=event_content_id,
)
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `mission_unique_id` | 任务 ID，来自 `progress`。 |
| `progress_server_id` | 进度记录 ID，通常来自同一条 `progress`。 |
| `event_content_id` | 活动任务所属活动 ID。 |
| `validate` | 默认 `True`，会先读取任务列表，确认任务存在且 `Complete=True`。 |

返回结构：

```python
{
    "added_history": {...},
    "mission_progress": [...],
    "parcel_result": {...},
    "extra": {},
}
```

## 按分类批量领取

对应任务页里按分类一键领取，例如每日任务一键领取。

```python
result = await client.mission.multiple_reward("daily")
```

常用分类：

| 参数值 | 游戏里对应 |
| --- | --- |
| `"daily"` | 每日任务 |
| `"weekly"` | 每周任务 |
| `"achievement"` | 成就任务 |
| `"guide"` / `"guide_mission"` | 指南任务 |
| `"event_achievement"` | 活动成就任务 |
| `"event_fixed"` | 活动固定任务 |

返回结构：

```python
{
    "added_histories": [...],
    "mission_progress": [...],
    "parcel_result": {...},
    "extra": {},
}
```

SDK 默认会先读取任务列表，确认当前至少有已完成任务再发送领奖请求。

## 指南任务赛季

对应游戏里的指南任务/新手任务赛季列表。

```python
seasons = await client.mission.guide_season_list()
```

返回结构：

```python
{
    "guide_mission_seasons": [...],
    "count": 0,
    "extra": {},
}
```

## live 结果和限制

读取任务列表已验证可用。任务领奖会遇到 NGS 校验差异：

```text
小号：Mission_Reward / Mission_MultipleReward 返回 1032 NexonNgsmValidateFail
大号：Mission_MultipleReward("daily") live 成功
```

调用方应把 `1032 NexonNgsmValidateFail` 当成可预期的账号/环境校验失败，而不是简单参数错误。读取任务进度和领取任务奖励是两件事。
