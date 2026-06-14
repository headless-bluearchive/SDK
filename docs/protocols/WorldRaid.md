# WorldRaid 协议

WorldRaid 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `WorldRaid_Lobby` | `40000` | 世界 Raid：获取或进入模块大厅 | `WorldRaidLobbyRequest` | `WorldRaidLobbyResponse` |
| `WorldRaid_BossList` | `40001` | 世界 Raid：Boss列表 | `WorldRaidBossListRequest` | `WorldRaidBossListResponse` |
| `WorldRaid_ReceiveReward` | `40004` | 世界 Raid：领取奖励 | `WorldRaidReceiveRewardRequest` | `WorldRaidReceiveRewardResponse` |
| `WorldRaid_UpdateCarrierSkill` | `40005` | 世界 Raid：更新CarrierSkill | `WorldRaidUpdateCarrierSkillRequest` | `WorldRaidUpdateCarrierSkillResponse` |

## 字段结构参考

### WorldRaid_Lobby

- 协议号：`40000`
- 作用：世界 Raid：获取或进入模块大厅
- RequestClass：`WorldRaidLobbyRequest`
- ResponseClass：`WorldRaidLobbyResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SeasonId` | `long` | 赛季 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClearHistoryDBs` | `List<WorldRaidClearHistoryDB>?` | ClearHistory 数据列表。 |
| `LocalBossDBs` | `List<WorldRaidLocalBossDB>?` | LocalBoss 数据列表。 |
| `BossGroups` | `List<WorldRaidBossGroup>?` | BossGroups数据列表。 |

### WorldRaid_BossList

- 协议号：`40001`
- 作用：世界 Raid：Boss列表
- RequestClass：`WorldRaidBossListRequest`
- ResponseClass：`WorldRaidBossListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SeasonId` | `long` | 赛季 ID。 |
| `RequestOnlyWorldBossData` | `bool` | 是否只请求世界 Boss 数据。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BossListInfoDBs` | `List<WorldRaidBossListInfoDB>?` | BossListInfo 数据列表。 |

### WorldRaid_ReceiveReward

- 协议号：`40004`
- 作用：世界 Raid：领取奖励
- RequestClass：`WorldRaidReceiveRewardRequest`
- ResponseClass：`WorldRaidReceiveRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SeasonId` | `long` | 赛季 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### WorldRaid_UpdateCarrierSkill

- 协议号：`40005`
- 作用：世界 Raid：更新CarrierSkill
- RequestClass：`WorldRaidUpdateCarrierSkillRequest`
- ResponseClass：`WorldRaidUpdateCarrierSkillResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
