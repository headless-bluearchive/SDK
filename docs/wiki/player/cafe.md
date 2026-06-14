# 咖啡厅

咖啡厅目前封装了三件事：读状态、摸头、收收益。不是装修模拟器，家具摆放、预设编辑那些高风险改状态接口先不碰。

## 读取状态

```python
state = await client.cafe.get()
```

返回重点：

| 字段 | 说明 |
| --- | --- |
| `cafes` | 咖啡厅列表，当前支持两个咖啡厅。 |
| `furniture` | 家具状态。 |
| `interaction_targets` | SDK 整理出的可摸头目标。 |

`CafeVisitCharacterDBs` 在 live 里可能是 map：

```json
{
  "10100": {
    "ServerId": 853994605,
    "UniqueId": 10100
  }
}
```

真正给 `Cafe_Interact.CharacterId` 用的是 map key / `UniqueId`，不是 `ServerId`。这个坑 SDK 已经填了。

## 摸头

```python
state = await client.cafe.get()

for target in state["interaction_targets"]:
    result = await client.cafe.interact(
        cafe_db_id=target["CafeDBId"],
        character_id=target["CharacterId"],
    )
```

如果只想让 SDK 自动选一个目标：

```python
result = await client.cafe.interact()
```

多个可摸头目标同时存在时，SDK 会让你显式传 `cafe_db_id` 和 `character_id`，免得替你乱点。

## 收收益

```python
result = await client.cafe.receive_currency()
```

`receive_currency()` 默认会先读咖啡厅状态，确认 `cafe_db_id` 存在。要指定哪个咖啡厅就传：

```python
await client.cafe.receive_currency(cafe_db_id=4077273)
```

live 验证：`Cafe_Get`、`Cafe_Interact`、`Cafe_ReceiveCurrency` 均已接入测试过。收益领取属于状态变更，外部别拿它当只读接口循环刷。
