# CharacterGear 协议

角色装备模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `CharacterGear_List` | `44000` | 爱用品/角色装备：获取列表数据 | `CharacterGearListRequest` | `CharacterGearListResponse` |
| `CharacterGear_Unlock` | `44001` | 爱用品/角色装备：执行 Unlock 流程 | `CharacterGearUnlockRequest` | `CharacterGearUnlockResponse` |
| `CharacterGear_TierUp` | `44002` | 爱用品/角色装备：Tier提升 | `CharacterGearTierUpRequest` | `CharacterGearTierUpResponse` |

## 字段结构参考

### CharacterGear_List

- 协议号：`44000`
- 作用：爱用品/角色装备：获取列表数据
- RequestClass：`CharacterGearListRequest`
- ResponseClass：`CharacterGearListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `GearDBs` | `List<GearDB>?` | Gear 数据列表。 |

### CharacterGear_Unlock

- 协议号：`44001`
- 作用：爱用品/角色装备：执行 Unlock 流程
- RequestClass：`CharacterGearUnlockRequest`
- ResponseClass：`CharacterGearUnlockResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterServerId` | `long` | 角色服务器 ID。 |
| `SlotIndex` | `int` | 槽位索引索引。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `GearDB` | `GearDB?` | 装备数据。 |
| `CharacterDB` | `CharacterDB?` | 角色数据。 |

### CharacterGear_TierUp

- 协议号：`44002`
- 作用：爱用品/角色装备：Tier提升
- RequestClass：`CharacterGearTierUpRequest`
- ResponseClass：`CharacterGearTierUpResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `GearServerId` | `long` | 装备服务器 ID。 |
| `ReplaceInfos` | `List<SelectTicketReplaceInfo>?` | 替换信息列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `GearDB` | `GearDB?` | 装备数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |
