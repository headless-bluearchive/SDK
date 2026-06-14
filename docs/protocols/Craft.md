# Craft 协议

制造模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Craft_List` | `21000` | 制造：获取列表数据 | `CraftInfoListRequest` | `CraftInfoListResponse` |
| `Craft_SelectNode` | `21001` | 制造：执行 SelectNode 流程 | `CraftSelectNodeRequest` | `CraftSelectNodeResponse` |
| `Craft_UpdateNodeLevel` | `21002` | 制造：更新NodeLevel | `CraftUpdateNodeLevelRequest` | `CraftUpdateNodeLevelResponse` |
| `Craft_BeginProcess` | `21003` | 制造：执行 BeginProcess 流程 | `CraftBeginProcessRequest` | `CraftBeginProcessResponse` |
| `Craft_CompleteProcess` | `21004` | 制造：执行 CompleteProcess 流程 | `CraftCompleteProcessRequest` | `CraftCompleteProcessResponse` |
| `Craft_Reward` | `21005` | 制造：奖励 | `CraftRewardRequest` | `CraftRewardResponse` |
| `Craft_HistoryList` | `21006` | 制造：历史记录列表 | `` | `` |
| `Craft_ShiftingBeginProcess` | `21007` | 制造：执行 ShiftingBeginProcess 流程 | `CraftShiftingBeginProcessRequest` | `CraftShiftingBeginProcessResponse` |
| `Craft_ShiftingCompleteProcess` | `21008` | 制造：执行 ShiftingCompleteProcess 流程 | `CraftShiftingCompleteProcessRequest` | `CraftShiftingCompleteProcessResponse` |
| `Craft_ShiftingReward` | `21009` | 制造：Shifting奖励 | `CraftShiftingRewardRequest` | `CraftShiftingRewardResponse` |
| `Craft_AutoBeginProcess` | `21010` | 制造：执行 AutoBeginProcess 流程 | `CraftAutoBeginProcessRequest` | `CraftAutoBeginProcessResponse` |
| `Craft_CompleteProcessAll` | `21011` | 制造：CompleteProcess全部 | `CraftCompleteProcessAllRequest` | `CraftCompleteProcessAllResponse` |
| `Craft_RewardAll` | `21012` | 制造：奖励全部 | `CraftRewardAllRequest` | `CraftRewardAllResponse` |
| `Craft_ShiftingCompleteProcessAll` | `21013` | 制造：ShiftingCompleteProcess全部 | `CraftShiftingCompleteProcessAllRequest` | `CraftShiftingCompleteProcessAllResponse` |
| `Craft_ShiftingRewardAll` | `21014` | 制造：Shifting奖励全部 | `CraftShiftingRewardAllRequest` | `CraftShiftingRewardAllResponse` |
| `Craft_SavePreset` | `21015` | 制造：保存预设 | `CraftSavePresetRequest` | `CraftSavePresetResponse` |
| `Craft_SavePresetName` | `21016` | 制造：保存预设Name | `CraftSavePresetNameRequest` | `CraftSavePresetNameResponse` |

## 字段结构参考

### Craft_List

- 协议号：`21000`
- 作用：制造：获取列表数据
- RequestClass：`CraftInfoListRequest`
- ResponseClass：`CraftInfoListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CraftInfos` | `List<CraftInfoDB>?` | CraftInfos数据列表。 |
| `ShiftingCraftInfos` | `List<ShiftingCraftInfoDB>?` | ShiftingCraftInfos数据列表。 |

### Craft_SelectNode

- 协议号：`21001`
- 作用：制造：执行 SelectNode 流程
- RequestClass：`CraftSelectNodeRequest`
- ResponseClass：`CraftSelectNodeResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SlotId` | `long` | 槽位 ID。 |
| `LeafNodeIndex` | `long` | LeafNode索引索引。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SelectedNodeDB` | `CraftNodeDB?` | SelectedNode数据。 |

### Craft_UpdateNodeLevel

- 协议号：`21002`
- 作用：制造：更新NodeLevel
- RequestClass：`CraftUpdateNodeLevelRequest`
- ResponseClass：`CraftUpdateNodeLevelResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ConsumeRequestDB` | `ConsumeRequestDB?` | 消耗请求。 |
| `ConsumeGoldAmount` | `long` | 消耗Gold数量数量。 |
| `SlotId` | `long` | 槽位 ID。 |
| `CraftNodeType` | `CraftNodeTier` | 制造节点类型。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CraftInfoDB` | `CraftInfoDB?` | Craft信息数据。 |
| `CraftNodeDB` | `CraftNodeDB?` | CraftNode数据。 |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |

### Craft_BeginProcess

- 协议号：`21003`
- 作用：制造：执行 BeginProcess 流程
- RequestClass：`CraftBeginProcessRequest`
- ResponseClass：`CraftBeginProcessResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SlotId` | `long` | 槽位 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CraftInfoDB` | `CraftInfoDB?` | Craft信息数据。 |

### Craft_CompleteProcess

- 协议号：`21004`
- 作用：制造：执行 CompleteProcess 流程
- RequestClass：`CraftCompleteProcessRequest`
- ResponseClass：`CraftCompleteProcessResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SlotId` | `long` | 槽位 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `CraftInfoDB` | `CraftInfoDB?` | Craft信息数据。 |
| `TicketItemDB` | `ItemDB?` | 票券道具数据。 |

### Craft_Reward

- 协议号：`21005`
- 作用：制造：奖励
- RequestClass：`CraftRewardRequest`
- ResponseClass：`CraftRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SlotId` | `long` | 槽位 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `CraftInfos` | `List<CraftInfoDB>?` | CraftInfos数据列表。 |

### Craft_HistoryList

- 协议号：`21006`
- 作用：制造：历史记录列表
- RequestClass：``
- ResponseClass：``
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Craft_ShiftingBeginProcess

- 协议号：`21007`
- 作用：制造：执行 ShiftingBeginProcess 流程
- RequestClass：`CraftShiftingBeginProcessRequest`
- ResponseClass：`CraftShiftingBeginProcessResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SlotId` | `long` | 槽位 ID。 |
| `RecipeId` | `long` | Recipe ID。 |
| `ConsumeRequestDB` | `ConsumeRequestDB?` | 消耗请求。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CraftInfoDB` | `ShiftingCraftInfoDB?` | Craft信息数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Craft_ShiftingCompleteProcess

- 协议号：`21008`
- 作用：制造：执行 ShiftingCompleteProcess 流程
- RequestClass：`CraftShiftingCompleteProcessRequest`
- ResponseClass：`CraftShiftingCompleteProcessResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SlotId` | `long` | 槽位 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CraftInfoDB` | `ShiftingCraftInfoDB?` | Craft信息数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Craft_ShiftingReward

- 协议号：`21009`
- 作用：制造：Shifting奖励
- RequestClass：`CraftShiftingRewardRequest`
- ResponseClass：`CraftShiftingRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SlotId` | `long` | 槽位 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `TargetCraftInfos` | `List<ShiftingCraftInfoDB>?` | 目标CraftInfos数据列表。 |

### Craft_AutoBeginProcess

- 协议号：`21010`
- 作用：制造：执行 AutoBeginProcess 流程
- RequestClass：`CraftAutoBeginProcessRequest`
- ResponseClass：`CraftAutoBeginProcessResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PresetSlotDB` | `CraftPresetSlotDB?` | 预设槽位数据。 |
| `Count` | `long` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CraftInfoDBs` | `List<CraftInfoDB>?` | CraftInfo 数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Craft_CompleteProcessAll

- 协议号：`21011`
- 作用：制造：CompleteProcess全部
- RequestClass：`CraftCompleteProcessAllRequest`
- ResponseClass：`CraftCompleteProcessAllResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CraftInfoDBs` | `List<CraftInfoDB>?` | CraftInfo 数据列表。 |
| `TicketItemDB` | `ItemDB?` | 票券道具数据。 |

### Craft_RewardAll

- 协议号：`21012`
- 作用：制造：奖励全部
- RequestClass：`CraftRewardAllRequest`
- ResponseClass：`CraftRewardAllResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `CraftInfos` | `List<CraftInfoDB>?` | CraftInfos数据列表。 |

### Craft_ShiftingCompleteProcessAll

- 协议号：`21013`
- 作用：制造：ShiftingCompleteProcess全部
- RequestClass：`CraftShiftingCompleteProcessAllRequest`
- ResponseClass：`CraftShiftingCompleteProcessAllResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CraftInfoDBs` | `List<ShiftingCraftInfoDB>?` | CraftInfo 数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Craft_ShiftingRewardAll

- 协议号：`21014`
- 作用：制造：Shifting奖励全部
- RequestClass：`CraftShiftingRewardAllRequest`
- ResponseClass：`CraftShiftingRewardAllResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `CraftInfoDBs` | `List<ShiftingCraftInfoDB>?` | CraftInfo 数据列表。 |

### Craft_SavePreset

- 协议号：`21015`
- 作用：制造：保存预设
- RequestClass：`CraftSavePresetRequest`
- ResponseClass：`CraftSavePresetResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Craft_SavePresetName

- 协议号：`21016`
- 作用：制造：保存预设Name
- RequestClass：`CraftSavePresetNameRequest`
- ResponseClass：`CraftSavePresetNameResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
