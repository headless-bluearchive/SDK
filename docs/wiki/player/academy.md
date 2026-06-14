# 课程表

课程表模块只接普通课程表：`Academy_GetInfo` 和 `Academy_AttendSchedule`。`Academy_AttendFavorSchedule` 不是每日“执行课程表”的入口，不要再拿它当每日任务解法。

## 状态

```python
info = await client.academy.get_info()
```

返回：

| 字段 | 说明 |
| --- | --- |
| `academy` | 当前课程表主体状态。 |
| `locations` | 地点列表。 |
| `available_zone_ids` | 当前可见区域 ID。 |
| `attended_zone_ids` | 今日已执行区域 ID。 |

## 执行课程表

```python
result = await client.academy.attend_schedule(zone_id=zone_id)
```

如果只剩一个可执行区域，SDK 可以自动推导：

```python
result = await client.academy.attend_schedule()
```

如果有多个区域，SDK 会要求你传 `zone_id`，不替你选。已经执行过的区域也会被挡掉。

课程表会改变账号状态，也可能消耗当天次数。外部流程要先读 `get_info()`，再决定是否调用。
