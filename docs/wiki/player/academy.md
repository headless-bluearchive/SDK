# 课程表页面

这一页对应游戏里的课程表/日程页。SDK 支持读取当前可执行区域、执行普通课程表。执行课程表会消耗当天次数并改账号状态，所以应先读状态、再由调用方确认要执行哪个区域。

能看什么：课程表区域、地点、学生、今日已执行状态。
能做什么：在某个区域执行一次普通课程表（会改账号状态，可能给好感/道具/任务进度）。

`Academy_AttendFavorSchedule`（提升羁绊的日程）当前没有封装成 SDK 入口，不要把它当作"执行课程表"。

## SDK 入口

| 方法 | 用途 | confirm | 返回 |
| --- | --- | --- | --- |
| `client.academy.get_info()` | 课程表页面状态。 | 否 | 整理后的 dict |
| `client.academy.attend_schedule(*, zone_id=None, validate=True)` | 在某区域执行普通课程表；改账号状态。 | 否（守卫是 `validate=True`） | 整理后的 dict |

## 课程表页面状态

```python
info = await client.academy.get_info()
```

不需要参数。

返回 SDK 整理后的 dict：业务字段（`academy` 主体状态、`locations` 地点列表、`available_zone_ids` 当前可见区域、`attended_zone_ids` 今日已执行区域）加 `extra`。

```python
info = await client.academy.get_info()
available = set(info["available_zone_ids"])
attended = set(info["attended_zone_ids"])
candidate_zone_ids = sorted(available - attended)
```

## 执行课程表

对应在某个课程表区域点击执行，会改账号状态并可能给学生好感、道具或任务进度。

```python
result = await client.academy.attend_schedule(zone_id=zone_id)
```

当前只剩一个可执行区域时，SDK 可以从 `get_info()` 自动推导：

```python
result = await client.academy.attend_schedule()
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `zone_id` | 要执行课程表的区域 ID，来自 `available_zone_ids`。 |
| `validate` | 默认 `True`，会先读课程表状态确认区域存在且今天还没执行。 |

返回 SDK 整理后的 dict：执行后的 `academy`、`parcel_result`（奖励/资源变化）、`extra_rewards`（额外奖励）加 `extra`。

## 注意

- `attend_schedule` 没有 `confirm` 参数，由 `validate=True` 守卫：区域不在可见列表、或今天已执行过时抛 `UnsafeOperationError` 且不发包。多个可执行区域并存且未显式指定 `zone_id` 时同样拒绝执行，不会自动随机选择。
- `zone_id` 一律来自当前账号可见的 `available_zone_ids`，不要手填。
- 逐协议接入状态见仓库根 `docs/protocols.md`。
