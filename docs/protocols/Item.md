# Item 协议

道具模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Item_List` | `4000` | 物品：获取列表数据 | `ItemListRequest` | `ItemListResponse` |
| `Item_Sell` | `4001` | 物品：执行 Sell 流程 | `ItemSellRequest` | `ItemSellResponse` |
| `Item_Consume` | `4002` | 物品：执行 Consume 流程 | `ItemConsumeRequest` | `ItemConsumeResponse` |
| `Item_Lock` | `4003` | 物品：执行 Lock 流程 | `ItemLockRequest` | `ItemLockResponse` |
| `Item_BulkConsume` | `4004` | 物品：执行 BulkConsume 流程 | `ItemBulkConsumeRequest` | `ItemBulkConsumeResponse` |
| `Item_SelectTicket` | `4005` | 物品：Select票据 | `ItemSelectTicketRequest` | `ItemSelectTicketResponse` |
| `Item_AutoSynth` | `4006` | 物品：执行 AutoSynth 流程 | `ItemAutoSynthRequest` | `ItemAutoSynthResponse` |

## 字段结构参考

### Item_List

- 协议号：`4000`
- 作用：物品：获取列表数据
- RequestClass：`ItemListRequest`
- ResponseClass：`ItemListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ItemDBs` | `List<ItemDB>?` | Item 数据列表。 |
| `ExpiryItemDBs` | `List<ItemDB>?` | ExpiryItem 数据列表。 |

### Item_Sell

- 协议号：`4001`
- 作用：物品：执行 Sell 流程
- RequestClass：`ItemSellRequest`
- ResponseClass：`ItemSellResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetServerIds` | `List<long>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |

### Item_Consume

- 协议号：`4002`
- 作用：物品：执行 Consume 流程
- RequestClass：`ItemConsumeRequest`
- ResponseClass：`ItemConsumeResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetItemServerId` | `long` | 目标道具服务器 ID。 |
| `ConsumeCount` | `int` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `UsedItemDB` | `ItemDB?` | Used道具数据。 |
| `NewParcelResultDB` | `ParcelResultDB?` | New奖励包结果数据。 |

### Item_Lock

- 协议号：`4003`
- 作用：物品：执行 Lock 流程
- RequestClass：`ItemLockRequest`
- ResponseClass：`ItemLockResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetServerId` | `long` | 目标服务器 ID。 |
| `IsLocked` | `bool` | 布尔状态。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ItemDB` | `ItemDB?` | 道具数据。 |

### Item_BulkConsume

- 协议号：`4004`
- 作用：物品：执行 BulkConsume 流程
- RequestClass：`ItemBulkConsumeRequest`
- ResponseClass：`ItemBulkConsumeResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetItemServerId` | `long` | 目标道具服务器 ID。 |
| `ConsumeCount` | `int` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `UsedItemDB` | `ItemDB?` | Used道具数据。 |
| `ParcelInfosInMailBox` | `List<ParcelInfo>?` | 奖励包InfosIn邮件Box数据列表。 |

### Item_SelectTicket

- 协议号：`4005`
- 作用：物品：Select票据
- RequestClass：`ItemSelectTicketRequest`
- ResponseClass：`ItemSelectTicketResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TicketItemServerId` | `long` | 票券道具服务器 ID。 |
| `SelectItemUniqueId` | `long` | Select道具唯一 ID。 |
| `ConsumeCount` | `int` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `UsedItemDB` | `ItemDB?` | Used道具数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Item_AutoSynth

- 协议号：`4006`
- 作用：物品：执行 AutoSynth 流程
- RequestClass：`ItemAutoSynthRequest`
- ResponseClass：`ItemAutoSynthResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetParcels` | `List<ParcelKeyPair>?` | 目标Parcels数据列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
