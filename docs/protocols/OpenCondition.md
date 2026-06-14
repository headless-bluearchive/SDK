# OpenCondition 协议

OpenCondition 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `OpenCondition_List` | `15000` | 开放条件：获取列表数据 | `OpenConditionListRequest` | `OpenConditionListResponse` |
| `OpenCondition_Set` | `15001` | 开放条件：设置 | `OpenConditionSetRequest` | `OpenConditionSetResponse` |
| `OpenCondition_EventList` | `15002` | 开放条件：活动列表 | `OpenConditionEventListRequest` | `OpenConditionEventListResponse` |

## 字段结构参考

### OpenCondition_List

- 协议号：`15000`
- 作用：开放条件：获取列表数据
- RequestClass：`OpenConditionListRequest`
- ResponseClass：`OpenConditionListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ConditionContents` | `List<OpenConditionContent>?` | ConditionContents数据列表。 |

### OpenCondition_Set

- 协议号：`15001`
- 作用：开放条件：设置
- RequestClass：`OpenConditionSetRequest`
- ResponseClass：`OpenConditionSetResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ConditionDB` | `OpenConditionDB?` | Condition数据。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ConditionDBs` | `List<OpenConditionDB>?` | Condition 数据列表。 |

### OpenCondition_EventList

- 协议号：`15002`
- 作用：开放条件：活动列表
- RequestClass：`OpenConditionEventListRequest`
- ResponseClass：`OpenConditionEventListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ConquestEventIds` | `List<long>?` | ID 列表。 |
| `WorldRaidSeasonAndGroupIds` | `Dictionary<long, long>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ConquestTiles` | `Dictionary<long, List<ConquestTileDB>>?` | 制约解除决战格子映射。 |
| `WorldRaidLocalBossDBs` | `Dictionary<long, List<WorldRaidLocalBossDB>>?` | WorldRaidLocalBoss 数据列表。 |
