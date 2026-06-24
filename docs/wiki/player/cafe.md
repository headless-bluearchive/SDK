# 咖啡厅页面

这一页对应游戏里的咖啡厅：查看咖啡厅状态、给来访学生摸头、领取咖啡厅产出、看奖杯历史，以及读取家具预设。装修类（家具布局、预设改名/应用、模板、串门）和养成类（升级、送礼、召唤学生）写操作集中在[显式确认变更页面](state-changing.md)，那些方法一律需 `confirm=True`。

能看什么：咖啡厅等级、家具、来访学生、可摸头目标、奖杯历史、家具预设。
能做什么：摸头获得羁绊点数、领取咖啡厅收益（都会改账号状态）。

## SDK 入口

只读（不改账号）：

| 方法 | 用途 | 返回 |
| --- | --- | --- |
| `client.cafe.get(*, account_server_id=None)` | 咖啡厅页面状态；默认用当前账号 ID。 | 整理后的 dict |
| `client.cafe.list_preset()` | 家具预设列表。 | 服务端原始负载 |
| `client.cafe.preset_detail(*, preset_type, slot_id)` | 单个家具预设详情。 | 服务端原始负载 |
| `client.cafe.trophy_history()` | Raid/赛季奖杯历史。 | 整理后的 dict |

轻量互动（改账号状态，无 `confirm`，由 `validate=True` 守卫）：

| 方法 | 用途 |
| --- | --- |
| `client.cafe.interact(*, cafe_db_id=None, character_id=None, validate=True)` | 摸头，获得学生羁绊点数。 |
| `client.cafe.receive_currency(*, cafe_db_id=None, account_server_id=None, validate=True)` | 领取咖啡厅收益。 |

装修 / 养成（需 `confirm=True`，详见 [state-changing.md](state-changing.md)）：`ack`、`rename_preset`、`clear_preset`、`update_preset_furniture`、`apply_preset`、`apply_template`、`open`、`travel`、`update_copy_preset_furniture`、`rank_up`、`give_gift`、`summon_character`、`summon_character_ticket_use`。这些方法不传 `confirm=True` 会抛 `UnsafeOperationError` 且不发包。

## 咖啡厅页面状态

```python
state = await client.cafe.get()
```

通常不需要参数，SDK 用当前账号的 `account_id`；要查指定账号传 `account_server_id`。

返回 SDK 整理后的 dict：业务字段（主咖啡厅 `cafe`、`cafes` 列表、`furniture`，以及 SDK 整理出的可摸头目标 `interaction_targets`）加 `extra`（其余原始字段）。`interaction_targets` 单项形如 `{"CafeDBId": ..., "CharacterId": ...}`。

live 中 `CafeVisitCharacterDBs` 有时是 map，真正给摸头请求用的是 map key 或 `UniqueId`，不是 `ServerId`；SDK 已将该差异整理进 `interaction_targets`，直接使用即可。

## 摸头

对应点击咖啡厅来访学生获得羁绊点数，会改账号状态。

```python
state = await client.cafe.get()
for target in state["interaction_targets"]:
    result = await client.cafe.interact(
        cafe_db_id=target["CafeDBId"],
        character_id=target["CharacterId"],
    )
```

只有一个可摸头目标时可以让 SDK 自动选择：

```python
result = await client.cafe.interact()
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `cafe_db_id` | 咖啡厅实例 ID，来自 `interaction_targets`。 |
| `character_id` | 可摸头学生 ID，来自 `interaction_targets`。 |
| `validate` | 默认 `True`，会先读咖啡厅状态确认目标存在。 |

返回 SDK 整理后的 dict：摸头后的 `cafe`、被互动学生 `character`、`parcel_result`（资源变化）加 `extra`。多个可摸头目标同时存在且未显式指定时，SDK 会要求传 `cafe_db_id` 和 `character_id`，不会自动随机选择。

## 领取咖啡厅收益

对应点击咖啡厅收益领取，会改账号资源。

```python
result = await client.cafe.receive_currency()
```

要指定某个咖啡厅时传 `cafe_db_id`（来自 `cafe.get()` 的 `cafes`）：

```python
result = await client.cafe.receive_currency(cafe_db_id=cafe_db_id)
```

返回 SDK 整理后的 dict：`cafe`、`cafes`、`parcel_result` 加 `extra`。默认 `validate=True` 会先读咖啡厅状态确认 `cafe_db_id` 存在。

## 奖杯历史

对应咖啡厅里可展示的 Raid/赛季奖杯历史。

```python
history = await client.cafe.trophy_history()
```

返回 SDK 整理后的 dict：`raid_season_ranking_history` 加 `count` 加 `extra`。

## 注意

- 摸头和领收益属于账号状态变更，不要放进循环轮询。它们没有 `confirm` 参数，由 `validate=True` 的前置查询守卫：目标/咖啡厅不存在时抛 `UnsafeOperationError` 且不发包。
- 装修和养成类方法（上表）需显式 `confirm=True`，否则抛 `UnsafeOperationError` 且不发包；详细参数和返回见 [state-changing.md](state-changing.md)。
- `cafe_db_id`、`character_id`、`slot_id` 等一律来自当前账号可见数据（`cafe.get()` / `list_preset()`），不要手填。
- `trophy_history()` 在部分账号上可能返回 `ErrorCode=14000 OpenConditionClosed`，通常表示奖杯页尚未对该账号开放，并非参数错误。
- 逐协议接入状态见仓库根 `docs/protocols.md`。
