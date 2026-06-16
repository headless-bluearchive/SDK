# 咖啡厅

这一页对应游戏里的咖啡厅页面：查看咖啡厅状态、给来访学生摸头、领取咖啡厅产出，以及查看奖杯历史。SDK 不处理家具摆放、预设编辑、邀请券使用等更复杂的装修/状态变更功能。

## 咖啡厅页面状态

对应打开咖啡厅后看到的咖啡厅等级、家具、来访学生和可互动状态。

```python
state = await client.cafe.get()
```

通常不需要参数；SDK 会使用当前账号的 `account_id`。如果要查询指定账号的咖啡厅，可以传 `account_server_id`。

返回结构：

```python
{
    "cafe": {...},                 # 主咖啡厅状态
    "cafes": [...],                # 咖啡厅列表，当前游戏通常有两个咖啡厅
    "furniture": [...],            # 家具状态
    "interaction_targets": [...],  # SDK 整理出的可摸头目标
    "extra": {},
}
```

`interaction_targets` 的单项长这样：

```python
{
    "CafeDBId": 4077273,
    "CharacterId": 10100,
}
```

live 中 `CafeVisitCharacterDBs` 有时是 map，真正给摸头请求使用的是 map key 或 `UniqueId`，不是 `ServerId`。SDK 已经把这个差异整理进 `interaction_targets`。

## 摸头

对应游戏里点击咖啡厅来访学生获得羁绊点数。这个动作会改变账号状态。

```python
state = await client.cafe.get()

for target in state["interaction_targets"]:
    result = await client.cafe.interact(
        cafe_db_id=target["CafeDBId"],
        character_id=target["CharacterId"],
    )
```

如果当前只有一个可摸头目标，可以让 SDK 自动选择：

```python
result = await client.cafe.interact()
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `cafe_db_id` | 咖啡厅实例 ID，来自 `interaction_targets`。 |
| `character_id` | 可摸头学生 ID，来自 `interaction_targets`。 |
| `validate` | 默认 `True`，会先读取咖啡厅状态确认目标存在。 |

返回结构：

```python
{
    "cafe": {...},           # 摸头后的咖啡厅状态
    "character": {...},      # 被互动学生的状态更新
    "parcel_result": {...},  # 奖励/资源变化
    "extra": {},
}
```

多个可摸头目标同时存在时，SDK 会要求你显式传 `cafe_db_id` 和 `character_id`。

## 领取咖啡厅收益

对应游戏里点击咖啡厅收益领取。这个动作会改变账号资源。

```python
result = await client.cafe.receive_currency()
```

要指定某个咖啡厅：

```python
result = await client.cafe.receive_currency(cafe_db_id=4077273)
```

返回结构：

```python
{
    "cafe": {...},
    "cafes": [...],
    "parcel_result": {...},
    "extra": {},
}
```

`receive_currency()` 默认会先读取咖啡厅状态，确认 `cafe_db_id` 存在。

## 奖杯历史

对应咖啡厅里可展示的 Raid/赛季相关奖杯历史。

```python
history = await client.cafe.trophy_history()
```

返回结构：

```python
{
    "raid_season_ranking_history": [...],
    "count": 0,
    "extra": {},
}
```

live 验证：`Cafe_Get`、`Cafe_Interact`、`Cafe_ReceiveCurrency` 均已接入测试过。收益领取和摸头属于账号状态变更，不要把它们放进循环轮询。
