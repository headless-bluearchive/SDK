# Cafe 协议

咖啡厅模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 每日任务影响

`Cafe_Interact` 对应咖啡厅学生互动/摸头，可覆盖“在咖啡厅获得学生羁绊点数”类每日任务。

`Cafe_Interact` 已通过 live 状态变更验证。发包前应先用 `Cafe_Get` 确认可互动目标，并确认账号开放条件中包含 `Cafe=4` / `Cafe_Invite=38`；如果服务端返回 `ErrorCode=14000 (OpenConditionClosed)`，说明当前账号状态未开放咖啡厅互动，不要用 `OpenCondition_Set` 强行改状态。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Cafe_Get` | `20000` | 咖啡厅：获取数据 | `CafeGetInfoRequest` | `CafeGetInfoResponse` |
| `Cafe_Ack` | `20001` | 咖啡厅：确认咖啡厅状态变更 | `CafeAckRequest` | `CafeAckResponse` |
| `Cafe_Deploy` | `20002` | 咖啡厅：布置咖啡厅家具 | `CafeDeployFurnitureRequest` | `CafeDeployFurnitureResponse` |
| `Cafe_Relocate` | `20003` | 咖啡厅：移动咖啡厅家具 | `CafeRelocateFurnitureRequest` | `CafeRelocateFurnitureResponse` |
| `Cafe_Remove` | `20004` | 咖啡厅：移除咖啡厅家具 | `CafeRemoveFurnitureRequest` | `CafeRemoveFurnitureResponse` |
| `Cafe_RemoveAll` | `20005` | 咖啡厅：移除全部咖啡厅家具 | `CafeRemoveAllFurnitureRequest` | `CafeRemoveAllFurnitureResponse` |
| `Cafe_Interact` | `20006` | 咖啡厅：与咖啡厅内角色互动/摸头 | `CafeInteractWithCharacterRequest` | `CafeInteractWithCharacterResponse` |
| `Cafe_ListPreset` | `20007` | 咖啡厅：获取预设列表 | `CafeListPresetRequest` | `CafeListPresetResponse` |
| `Cafe_RenamePreset` | `20008` | 咖啡厅：重命名咖啡厅预设 | `CafeRenamePresetRequest` | `CafeRenamePresetResponse` |
| `Cafe_ClearPreset` | `20009` | 咖啡厅：清空咖啡厅预设 | `CafeClearPresetRequest` | `CafeClearPresetResponse` |
| `Cafe_UpdatePresetFurniture` | `20010` | 咖啡厅：更新预设家具布局 | `CafeUpdatePresetFurnitureRequest` | `CafeUpdatePresetFurnitureResponse` |
| `Cafe_ApplyPreset` | `20011` | 咖啡厅：应用咖啡厅家具预设 | `CafeApplyPresetRequest` | `CafeApplyPresetResponse` |
| `Cafe_RankUp` | `20012` | 咖啡厅：提升等级 | `CafeRankUpRequest` | `CafeRankUpResponse` |
| `Cafe_ReceiveCurrency` | `20013` | 咖啡厅：领取咖啡厅产出货币 | `CafeReceiveCurrencyRequest` | `CafeReceiveCurrencyResponse` |
| `Cafe_GiveGift` | `20014` | 咖啡厅：赠送礼物 | `CafeGiveGiftRequest` | `CafeGiveGiftResponse` |
| `Cafe_SummonCharacter` | `20015` | 咖啡厅：邀请角色到咖啡厅 | `CafeSummonCharacterRequest` | `CafeSummonCharacterResponse` |
| `Cafe_TrophyHistory` | `20016` | 咖啡厅：获取咖啡厅奖杯历史 | `CafeTrophyHistoryRequest` | `CafeTrophyHistoryResponse` |
| `Cafe_ApplyTemplate` | `20017` | 咖啡厅：应用咖啡厅模板 | `CafeApplyTemplateRequest` | `CafeApplyTemplateResponse` |
| `Cafe_Open` | `20018` | 咖啡厅：打开或解锁对应内容 | `CafeOpenRequest` | `CafeOpenResponse` |
| `Cafe_Travel` | `20019` | 咖啡厅：切换或访问咖啡厅区域 | `CafeTravelRequest` | `CafeTravelResponse` |
| `Cafe_SummonCharacterTicketUse` | `20020` | 咖啡厅：使用咖啡厅邀请券 | `CafeSummonCharacterTicketUseRequest` | `CafeSummonCharacterTicketUseResponse` |
| `Cafe_PresetDetail` | `20021` | 咖啡厅：获取咖啡厅预设详情 | `CafePresetDetailRequest` | `CafePresetDetailResponse` |
| `Cafe_UpdateCopyPresetFurniture` | `20022` | 咖啡厅：更新复制预设中的家具布局 | `CafeUpdateCopyPresetFurnitureRequest` | `CafeUpdateCopyPresetFurnitureResponse` |

## 字段结构参考

### Cafe_Get

- 协议号：`20000`
- 作用：咖啡厅：获取数据
- RequestClass：`CafeGetInfoRequest`
- ResponseClass：`CafeGetInfoResponse`
- 状态：SDK 已封装并通过 live 只读验证。

#### SDK 方法

```python
cafe = await client.cafe.get()
```

返回结构：

| 字段 | 说明 |
| --- | --- |
| `cafe` | 当前主要咖啡厅数据。 |
| `cafes` | 咖啡厅数据列表。 |
| `furniture` | 家具数据列表。 |
| `interaction_targets` | SDK 从 `CafeVisitCharacterDBs` 解析出的可用于 `Cafe_Interact` 的候选目标列表。 |
| `extra` | 服务端返回中的其他顶层字段。 |

live 返回中通常有两个 `CafeDB`，对应两个咖啡厅区域。`CafeVisitCharacterDBs` 可能不是数组，而是以角色 ID 为 key 的对象，例如 `{ "10100": { "LastInteractTime": "...", "ServerId": 853994605, "UniqueId": 10100 } }`。SDK 会同时扫描两个咖啡厅，并把 map key / `UniqueId` 作为 `Cafe_Interact` 的 `CharacterId`；`ServerId` 是角色实例服务器 ID，不用于 `Cafe_Interact.CharacterId`。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountServerId` | `long` | 账号服务器 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDB` | `CafeDB?` | 咖啡厅数据。 |
| `CafeDBs` | `List<CafeDB>?` | 咖啡厅数据列表。 |
| `FurnitureDBs` | `List<FurnitureDB>?` | 家具数据列表。 |

### Cafe_Ack

- 协议号：`20001`
- 作用：咖啡厅：确认咖啡厅状态变更
- RequestClass：`CafeAckRequest`
- ResponseClass：`CafeAckResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDB` | `CafeDB?` | 咖啡厅数据。 |

### Cafe_Deploy

- 协议号：`20002`
- 作用：咖啡厅：布置咖啡厅家具
- RequestClass：`CafeDeployFurnitureRequest`
- ResponseClass：`CafeDeployFurnitureResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |
| `FurnitureDB` | `FurnitureDB?` | 家具数据。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDB` | `CafeDB?` | 咖啡厅数据。 |
| `NewFurnitureServerId` | `long` | 新家具服务器 ID。 |
| `ChangedFurnitureDBs` | `List<FurnitureDB>?` | 变更后的家具数据列表。 |

### Cafe_Relocate

- 协议号：`20003`
- 作用：咖啡厅：移动咖啡厅家具
- RequestClass：`CafeRelocateFurnitureRequest`
- ResponseClass：`CafeRelocateFurnitureResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |
| `FurnitureDB` | `FurnitureDB?` | 家具数据。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDB` | `CafeDB?` | 咖啡厅数据。 |
| `RelocatedFurnitureDB` | `FurnitureDB?` | 移动后的家具数据。 |

### Cafe_Remove

- 协议号：`20004`
- 作用：咖啡厅：移除咖啡厅家具
- RequestClass：`CafeRemoveFurnitureRequest`
- ResponseClass：`CafeRemoveFurnitureResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |
| `FurnitureServerIds` | `List<long>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDB` | `CafeDB?` | 咖啡厅数据。 |
| `FurnitureDBs` | `List<FurnitureDB>?` | 家具数据列表。 |

### Cafe_RemoveAll

- 协议号：`20005`
- 作用：咖啡厅：移除全部咖啡厅家具
- RequestClass：`CafeRemoveAllFurnitureRequest`
- ResponseClass：`CafeRemoveAllFurnitureResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDB` | `CafeDB?` | 咖啡厅数据。 |
| `FurnitureDBs` | `List<FurnitureDB>?` | 家具数据列表。 |

### Cafe_Interact

- 协议号：`20006`
- 作用：咖啡厅：与咖啡厅内角色互动/摸头
- RequestClass：`CafeInteractWithCharacterRequest`
- ResponseClass：`CafeInteractWithCharacterResponse`
- 状态：SDK 已封装并通过 live 状态变更验证。

#### SDK 方法

```python
result = await client.cafe.interact()
```

默认会先调用 `Cafe_Get`，从 `CafeVisitCharacterDBs` 中确认可互动角色。没有可互动目标时会拒绝发包；如果存在多个候选，需要显式传入：

```python
result = await client.cafe.interact(cafe_db_id=cafe_db_id, character_id=character_id)
```

返回结构：

| 字段 | 说明 |
| --- | --- |
| `cafe` | 互动后的咖啡厅数据。 |
| `character` | 互动后的角色数据。 |
| `parcel_result` | 奖励或道具变更结果。 |
| `extra` | 服务端返回中的其他顶层字段。 |

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |
| `CharacterId` | `long` | 角色模板 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDB` | `CafeDB?` | 咖啡厅数据。 |
| `CharacterDB` | `CharacterDB?` | 角色数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Cafe_ListPreset

- 协议号：`20007`
- 作用：咖啡厅：获取预设列表
- RequestClass：`CafeListPresetRequest`
- ResponseClass：`CafeListPresetResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafePresetDBs` | `List<CafePresetDB>?` | CafePreset 数据列表。 |

### Cafe_RenamePreset

- 协议号：`20008`
- 作用：咖啡厅：重命名咖啡厅预设
- RequestClass：`CafeRenamePresetRequest`
- ResponseClass：`CafeRenamePresetResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SlotId` | `int` | 槽位 ID。 |
| `PresetName` | `string?` | 预设名称。 |

#### Response 字段

无字段或未匹配到结构。

### Cafe_ClearPreset

- 协议号：`20009`
- 作用：咖啡厅：清空咖啡厅预设
- RequestClass：`CafeClearPresetRequest`
- ResponseClass：`CafeClearPresetResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SlotId` | `int` | 槽位 ID。 |

#### Response 字段

无字段或未匹配到结构。

### Cafe_UpdatePresetFurniture

- 协议号：`20010`
- 作用：咖啡厅：更新预设家具布局
- RequestClass：`CafeUpdatePresetFurnitureRequest`
- ResponseClass：`CafeUpdatePresetFurnitureResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |
| `SlotId` | `int` | 槽位 ID。 |

#### Response 字段

无字段或未匹配到结构。

### Cafe_ApplyPreset

- 协议号：`20011`
- 作用：咖啡厅：应用咖啡厅家具预设
- RequestClass：`CafeApplyPresetRequest`
- ResponseClass：`CafeApplyPresetResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SlotId` | `int` | 槽位 ID。 |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |
| `UseOtherCafeFurniture` | `bool` | 是否使用其他咖啡厅家具。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDBs` | `List<CafeDB>?` | 咖啡厅数据列表。 |
| `FurnitureDBs` | `List<FurnitureDB>?` | 家具数据列表。 |

### Cafe_RankUp

- 协议号：`20012`
- 作用：咖啡厅：提升等级
- RequestClass：`CafeRankUpRequest`
- ResponseClass：`CafeRankUpResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountServerId` | `long` | 账号服务器 ID。 |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |
| `ConsumeRequestDB` | `ConsumeRequestDB?` | 消耗请求。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDB` | `CafeDB?` | 咖啡厅数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |

### Cafe_ReceiveCurrency

- 协议号：`20013`
- 作用：咖啡厅：领取咖啡厅产出货币
- RequestClass：`CafeReceiveCurrencyRequest`
- ResponseClass：`CafeReceiveCurrencyResponse`
- 状态：SDK 已封装并通过 live 状态变更验证。

#### SDK 方法

```python
result = await client.cafe.receive_currency()
```

默认会先调用 `Cafe_Get`，选择当前账号的第一个 `CafeDBId` 后领取。调用方也可以显式传入：

```python
result = await client.cafe.receive_currency(cafe_db_id=cafe_db_id)
```

返回结构：

| 字段 | 说明 |
| --- | --- |
| `cafe` | 本次请求对应的咖啡厅数据。 |
| `cafes` | 更新后的咖啡厅数据列表。 |
| `parcel_result` | 领取收益后的奖励或道具变更结果。 |
| `extra` | 服务端返回中的其他顶层字段。 |

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountServerId` | `long` | 账号服务器 ID。 |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDB` | `CafeDB?` | 咖啡厅数据。 |
| `CafeDBs` | `List<CafeDB>?` | 咖啡厅数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Cafe_GiveGift

- 协议号：`20014`
- 作用：咖啡厅：赠送礼物
- RequestClass：`CafeGiveGiftRequest`
- ResponseClass：`CafeGiveGiftResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |
| `CharacterUniqueId` | `long` | 角色服务器唯一 ID。 |
| `ConsumeRequestDB` | `ConsumeRequestDB?` | 消耗请求。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |

### Cafe_SummonCharacter

- 协议号：`20015`
- 作用：咖啡厅：邀请角色到咖啡厅
- RequestClass：`CafeSummonCharacterRequest`
- ResponseClass：`CafeSummonCharacterResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |
| `CharacterServerId` | `long` | 角色服务器 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDB` | `CafeDB?` | 咖啡厅数据。 |
| `CafeDBs` | `List<CafeDB>?` | 咖啡厅数据列表。 |

### Cafe_TrophyHistory

- 协议号：`20016`
- 作用：咖啡厅：获取咖啡厅奖杯历史
- RequestClass：`CafeTrophyHistoryRequest`
- ResponseClass：`CafeTrophyHistoryResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidSeasonRankingHistoryDBs` | `List<RaidSeasonRankingHistoryDB>?` | RaidSeasonRankingHistory 数据列表。 |

### Cafe_ApplyTemplate

- 协议号：`20017`
- 作用：咖啡厅：应用咖啡厅模板
- RequestClass：`CafeApplyTemplateRequest`
- ResponseClass：`CafeApplyTemplateResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TemplateId` | `long` | 模板 ID。 |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |
| `UseOtherCafeFurniture` | `bool` | 是否使用其他咖啡厅家具。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDBs` | `List<CafeDB>?` | 咖啡厅数据列表。 |
| `FurnitureDBs` | `List<FurnitureDB>?` | 家具数据列表。 |

### Cafe_Open

- 协议号：`20018`
- 作用：咖啡厅：打开或解锁对应内容
- RequestClass：`CafeOpenRequest`
- ResponseClass：`CafeOpenResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeId` | `long` | 咖啡厅 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `OpenedCafeDB` | `CafeDB?` | Opened咖啡厅数据。 |
| `FurnitureDBs` | `List<FurnitureDB>?` | 家具数据列表。 |

### Cafe_Travel

- 协议号：`20019`
- 作用：咖啡厅：切换或访问咖啡厅区域
- RequestClass：`CafeTravelRequest`
- ResponseClass：`CafeTravelResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetAccountId` | `Nullable<long>` | 目标账号 ID。 |
| `CurrentVisitingAccountId` | `Nullable<long>` | 当前正在访问的账号 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `FriendDB` | `FriendDB?` | 好友数据。 |
| `CafeDBs` | `List<CafeDB>?` | 咖啡厅数据列表。 |

### Cafe_SummonCharacterTicketUse

- 协议号：`20020`
- 作用：咖啡厅：使用咖啡厅邀请券
- RequestClass：`CafeSummonCharacterTicketUseRequest`
- ResponseClass：`CafeSummonCharacterTicketUseResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDBId` | `long` | 咖啡厅实例 ID。 |
| `CharacterServerId` | `long` | 角色服务器 ID。 |
| `ConsumeRequestDB` | `ConsumeRequestDB?` | 消耗请求。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CafeDB` | `CafeDB?` | 咖啡厅数据。 |
| `CafeDBs` | `List<CafeDB>?` | 咖啡厅数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Cafe_PresetDetail

- 协议号：`20021`
- 作用：咖啡厅：获取咖啡厅预设详情
- RequestClass：`CafePresetDetailRequest`
- ResponseClass：`CafePresetDetailResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Cafe_UpdateCopyPresetFurniture

- 协议号：`20022`
- 作用：咖啡厅：更新复制预设中的家具布局
- RequestClass：`CafeUpdateCopyPresetFurnitureRequest`
- ResponseClass：`CafeUpdateCopyPresetFurnitureResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
