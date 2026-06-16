# 学生、主线、日常副本和扫荡

这一页对应游戏里最基础的战斗准备页面：学生名册、主线关卡地图、悬赏通缉/日常副本历史，以及扫荡预设。这里的查询只读取账号当前状态，不会领奖、不消耗 AP、不提交战斗结果。

## 学生名册

对应游戏里的“学生”页面。适合用来显示当前账号拥有哪些学生、每个学生的等级/星级/装备等服务端记录。

```python
characters = await client.character.list()
```

不需要参数。

返回结构：

```python
{
    "characters": [...],      # 持有学生列表，对应 CharacterDBs
    "tss_characters": [...],  # TSSCharacterDBs，通常用于特殊同步学生数据
    "count": 0,               # characters 数量
    "extra": {...},           # SDK 尚未单独命名的其它字段
}
```

常见用法：

```python
characters = await client.character.list()
for character in characters["characters"]:
    print(character.get("UniqueId"), character.get("Level"))
```

## 主线关卡进度

对应游戏里的主线关卡地图和章节进度。它返回的是“这个账号已经打过哪些关卡、章节奖励历史、地图对象历史”，不是战斗中的存档，也不能用于伪造结算。

```python
campaign = await client.campaign.list()
```

不需要参数。

返回结构：

```python
{
    "chapter_clear_reward_history": [...],  # 章节奖励领取历史
    "stage_history": [...],                 # 主线关卡通关/历史记录
    "strategy_object_history": [...],       # 战略地图对象历史
    "stage_count": 0,                       # stage_history 数量
    "extra": {...},
}
```

常见用法：

```python
campaign = await client.campaign.list()
cleared_stage_ids = {
    item.get("StageUniqueId")
    for item in campaign["stage_history"]
    if item.get("Clear") is True
}
```

## 悬赏通缉和日常副本

对应游戏里的悬赏通缉、日常副本等关卡历史。学院交流会在游戏里属于另一个入口，见 [好友、社团、活动、Raid、小游戏等页面数据](readonly-extended.md) 的 `client.school_dungeon.list()`。

```python
week = await client.week_dungeon.list()
```

不需要参数。

返回结构：

```python
{
    "additional_stage_ids": [...],  # 当前额外开放的关卡 ID
    "stage_history": [...],         # 悬赏通缉/日常副本历史
    "stage_count": 0,               # stage_history 数量
    "extra": {...},
}
```

## 扫荡预设

对应游戏里的多扫荡预设页面。它只读取用户保存过的预设，不会执行扫荡。

```python
presets = await client.sweep.preset_list()
```

返回结构：

```python
{
    "presets": [...],  # MultiSweepPresetDBs
    "extra": {...},
}
```

## 执行扫荡

对应游戏里点击“扫荡”按钮。这个动作会消耗 AP/票券并改变账号资源，因此 SDK 要求显式确认。

单关扫荡：

```python
result = await client.sweep.request(
    content=content_type,
    stage_id=stage_id,
    count=1,
    event_content_id=0,
    confirm=True,
)
```

多扫荡：

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

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `content` / `content_type` | 关卡所属内容类型，例如主线、活动、日常副本等。 |
| `stage_id` | 要扫荡的关卡 ID。必须是账号已满足扫荡条件的关卡。 |
| `count` / `sweep_count` | 扫荡次数。 |
| `event_content_id` | 活动关卡使用的活动内容 ID；普通关卡通常为 `0`。 |
| `confirm=True` | 明确告诉 SDK 这是资源消耗操作。 |

返回结构：

```python
{
    "clear_parcels": [...],                # 基础掉落
    "bonus_parcels": [...],                # 额外掉落
    "event_content_bonus_parcels": [...],  # 活动加成掉落
    "parcel_result": {...},                # 账号物品/资源变动结果
    "campaign_stage_history": {...},       # 单关扫荡时的关卡历史更新
    "extra": {...},
}
```

`multi_sweep()` 的 `campaign_stage_history` 是列表。没有 `confirm=True` 会抛 `UnsafeOperationError`。调用方应先用账号资源、关卡历史和自己的用户授权逻辑确认 AP、次数和扫荡条件。

live 验证：

```text
Character_List ok
Campaign_List ok
WeekDungeon_List ok
ContentSweep_MultiSweepPresetList ok
```
