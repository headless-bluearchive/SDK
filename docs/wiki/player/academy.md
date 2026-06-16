# 课程表

这一页对应游戏里的课程表/日程页面。SDK 支持读取当前可执行区域和执行普通课程表。执行课程表会消耗当天次数并改变账号状态，因此调用前应先读取状态，再由调用方确认要点哪个区域。

`Academy_AttendFavorSchedule` 不是每日课程表按钮，不要把它当作“执行课程表”的入口。

## 课程表页面状态

对应打开课程表页面后看到的区域、地点、学生和今日已执行状态。

```python
info = await client.academy.get_info()
```

不需要参数。

返回结构：

```python
{
    "academy": {...},             # 当前课程表主体状态，对应 AcademyDB
    "locations": [...],           # 地点列表，对应 AcademyLocationDBs
    "available_zone_ids": [...],  # 当前账号可见区域 ID
    "attended_zone_ids": [...],   # 今日已经执行过课程表的区域 ID
    "extra": {},
}
```

常见用法：

```python
info = await client.academy.get_info()
available = set(info["available_zone_ids"])
attended = set(info["attended_zone_ids"])
candidate_zone_ids = sorted(available - attended)
```

## 执行课程表

对应游戏里在某个课程表区域点击执行。它会改变账号状态并可能给学生好感、道具或任务进度。

```python
result = await client.academy.attend_schedule(zone_id=zone_id)
```

如果当前只剩一个可执行区域，SDK 可以从 `get_info()` 自动推导：

```python
result = await client.academy.attend_schedule()
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `zone_id` | 要执行课程表的区域 ID，来自 `available_zone_ids`。 |
| `validate` | 默认 `True`，会先读取课程表状态，确认区域存在且今天还没执行。 |

返回结构：

```python
{
    "academy": {...},        # 执行后的课程表状态
    "parcel_result": {...},  # 获得的奖励/资源变化
    "extra_rewards": [...],  # 额外奖励
    "extra": {},
}
```

如果有多个可执行区域，SDK 会要求显式传 `zone_id`，不会替用户随机选。已经执行过的区域也会被本地校验拦住。
