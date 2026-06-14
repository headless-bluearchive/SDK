# 任务

任务模块负责读任务列表和领取已经完成的任务奖励。它不会帮你完成任务，更不会把“每日流程”封成一个大按钮。SDK 不是代练。

## 列表

```python
missions = await client.mission.list()
```

返回重点：

| 字段 | 说明 |
| --- | --- |
| `progress` | 当前任务进度。 |
| `mission_history_unique_ids` | 已领取历史。 |
| `daily_sudden_mission_info` | 每日突发任务信息。 |
| `cleared_original_mission_ids` | 已清理原始任务 ID。 |

`Mission_List` 是稳定可读接口。每日签到完成后，任务列表里可能会出现新的 `Complete=True` 任务。

## 领取

单条：

```python
result = await client.mission.reward(mission_unique_id)
```

按分类批量：

```python
result = await client.mission.multiple_reward("daily")
```

调用前 SDK 会先 `Mission_List`，确认有完成项再发领奖请求。

## 当前限制

任务领奖会遇到 NGS 校验差异，不要假装它已经天下无敌：

```text
小号：Mission_Reward / Mission_MultipleReward 返回 1032 NexonNgsmValidateFail
大号：Mission_MultipleReward("daily") live 成功
```

所以外部调用方要把 `1032 NexonNgsmValidateFail` 当成可预期失败，而不是参数填错。能读列表是一回事，能领奖是另一回事。
