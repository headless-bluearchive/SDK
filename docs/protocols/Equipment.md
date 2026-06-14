# Equipment 协议

装备模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Equipment_List` | `3000` | 装备：获取列表数据 | `EquipmentItemListRequest` | `EquipmentItemListResponse` |
| `Equipment_Sell` | `3001` | 装备：执行 Sell 流程 | `EquipmentItemSellRequest` | `EquipmentItemSellResponse` |
| `Equipment_Equip` | `3002` | 装备：装备 | `EquipmentItemEquipRequest` | `EquipmentItemEquipResponse` |
| `Equipment_LevelUp` | `3003` | 装备：提升等级 | `EquipmentItemLevelUpRequest` | `EquipmentItemLevelUpResponse` |
| `Equipment_TierUp` | `3004` | 装备：Tier提升 | `EquipmentItemTierUpRequest` | `EquipmentItemTierUpResponse` |
| `Equipment_Lock` | `3005` | 装备：执行 Lock 流程 | `EquipmentItemLockRequest` | `EquipmentItemLockResponse` |
| `Equipment_BatchGrowth` | `3006` | 装备：执行 BatchGrowth 流程 | `EquipmentBatchGrowthRequest` | `EquipmentBatchGrowthResponse` |

## 字段结构参考

### Equipment_List

- 协议号：`3000`
- 作用：装备：获取列表数据
- RequestClass：`EquipmentItemListRequest`
- ResponseClass：`EquipmentItemListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EquipmentDBs` | `List<EquipmentDB>?` | Equipment 数据列表。 |

### Equipment_Sell

- 协议号：`3001`
- 作用：装备：执行 Sell 流程
- RequestClass：`EquipmentItemSellRequest`
- ResponseClass：`EquipmentItemSellResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetServerIds` | `List<long>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |

### Equipment_Equip

- 协议号：`3002`
- 作用：装备：装备
- RequestClass：`EquipmentItemEquipRequest`
- ResponseClass：`EquipmentItemEquipResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterServerId` | `long` | 角色服务器 ID。 |
| `EquipmentServerIds` | `List<long>?` | ID 列表。 |
| `EquipmentServerId` | `long` | 装备服务器 ID。 |
| `SlotIndex` | `int` | 槽位索引索引。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterDB` | `CharacterDB?` | 角色数据。 |
| `EquipmentDBs` | `List<EquipmentDB>?` | Equipment 数据列表。 |

### Equipment_LevelUp

- 协议号：`3003`
- 作用：装备：提升等级
- RequestClass：`EquipmentItemLevelUpRequest`
- ResponseClass：`EquipmentItemLevelUpResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetServerId` | `long` | 目标服务器 ID。 |
| `ConsumeServerIds` | `List<long>?` | ID 列表。 |
| `ConsumeRequestDB` | `ConsumeRequestDB?` | 消耗请求。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EquipmentDB` | `EquipmentDB?` | 装备数据。 |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |

### Equipment_TierUp

- 协议号：`3004`
- 作用：装备：Tier提升
- RequestClass：`EquipmentItemTierUpRequest`
- ResponseClass：`EquipmentItemTierUpResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetEquipmentServerId` | `long` | 目标装备服务器 ID。 |
| `ReplaceInfos` | `List<SelectTicketReplaceInfo>?` | 替换信息列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EquipmentDB` | `EquipmentDB?` | 装备数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |

### Equipment_Lock

- 协议号：`3005`
- 作用：装备：执行 Lock 流程
- RequestClass：`EquipmentItemLockRequest`
- ResponseClass：`EquipmentItemLockResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetServerId` | `long` | 目标服务器 ID。 |
| `IsLocked` | `bool` | 布尔状态。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EquipmentDB` | `EquipmentDB?` | 装备数据。 |

### Equipment_BatchGrowth

- 协议号：`3006`
- 作用：装备：执行 BatchGrowth 流程
- RequestClass：`EquipmentBatchGrowthRequest`
- ResponseClass：`EquipmentBatchGrowthResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EquipmentBatchGrowthRequestDBs` | `List<EquipmentBatchGrowthRequestDB>?` | EquipmentBatchGrowthRequest 数据列表。 |
| `GearTierUpRequestDB` | `GearTierUpRequestDB?` | 装备TierUpRequest数据。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EquipmentDBs` | `List<EquipmentDB>?` | Equipment 数据列表。 |
| `GearDB` | `GearDB?` | 装备数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |
