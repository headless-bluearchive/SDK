# 扫荡

这一页单独说明游戏里的扫荡功能。扫荡不是战斗结算，也不是成绩提交；它只应该用于账号已经满足通关和扫荡条件的关卡。SDK 不会替你选择关卡、不会绕过通关记录，也不会自动消耗 AP。

## 多扫荡预设

对应游戏里保存的多扫荡预设列表。这个方法只读取预设，不执行扫荡。

```python
presets = await client.sweep.preset_list()
```

返回结构：

```python
{
    "presets": [...],  # MultiSweepPresetDBs
    "extra": {},
}
```

常见用法：

```python
presets = await client.sweep.preset_list()
for preset in presets["presets"]:
    print(preset.get("Name"), preset.get("MultiSweepParameters"))
```

## 单关扫荡

对应游戏里在某个可扫荡关卡上点击扫荡并确认次数。会消耗 AP/票券并领取掉落，因此必须显式确认。

```python
result = await client.sweep.request(
    content=content_type,
    stage_id=stage_id,
    count=1,
    event_content_id=0,
    confirm=True,
)
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `content` | 关卡所属内容类型。 |
| `stage_id` | 要扫荡的关卡 ID。 |
| `count` | 扫荡次数，必须大于 `0`。 |
| `event_content_id` | 活动关卡对应活动内容 ID；普通关卡通常为 `0`。 |
| `confirm=True` | 明确允许资源消耗。 |

返回结构：

```python
{
    "clear_parcels": [...],
    "bonus_parcels": [...],
    "event_content_bonus_parcels": [...],
    "parcel_result": {...},
    "campaign_stage_history": {...},
    "extra": {},
}
```

## 多关扫荡

对应游戏里一次执行多个扫荡目标。每个目标都要明确给出内容类型、关卡 ID 和次数。

```python
result = await client.sweep.multi_sweep(
    [
        {
            "content_type": content_type,
            "stage_id": stage_id,
            "sweep_count": 1,
            "event_content_id": 0,
        }
    ],
    confirm=True,
)
```

返回结构：

```python
{
    "clear_parcels": [...],
    "bonus_parcels": [...],
    "event_content_bonus_parcels": [...],
    "parcel_result": {...},
    "campaign_stage_history": [...],
    "extra": {},
}
```

调用前建议先读取：

```python
currency = await client.account.currency()
campaign = await client.campaign.list()
week = await client.week_dungeon.list()
presets = await client.sweep.preset_list()
```

调用方应自行确认用户授权、AP/票券数量、关卡是否已通关、次数是否符合预期。没有 `confirm=True` 会直接抛 `UnsafeOperationError`。
