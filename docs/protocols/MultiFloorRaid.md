# MultiFloorRaid 协议

多层 raid 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `MultiFloorRaid_Sync` | `49000` | 多层总力战：同步模块状态 | `MultiFloorRaidSyncRequest` | `MultiFloorRaidSyncResponse` |
| `MultiFloorRaid_ReceiveReward` | `49003` | 多层总力战：领取奖励 | `MultiFloorRaidReceiveRewardRequest` | `MultiFloorRaidReceiveRewardResponse` |
| `MultiFloorRaid_Login` | `49004` | 多层总力战：进入模块并同步基础数据 | `MultiFloorRaidLoginRequest` | `MultiFloorRaidLoginResponse` |

## 字段结构参考

### MultiFloorRaid_Sync

- 协议号：`49000`
- 作用：多层总力战：同步模块状态
- RequestClass：`MultiFloorRaidSyncRequest`
- ResponseClass：`MultiFloorRaidSyncResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SeasonId` | `Nullable<long>` | 赛季 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MultiFloorRaidDBs` | `List<MultiFloorRaidDB>?` | MultiFloorRaid 数据列表。 |

### MultiFloorRaid_ReceiveReward

- 协议号：`49003`
- 作用：多层总力战：领取奖励
- RequestClass：`MultiFloorRaidReceiveRewardRequest`
- ResponseClass：`MultiFloorRaidReceiveRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SeasonId` | `long` | 赛季 ID。 |
| `RewardDifficulty` | `int` | 奖励Difficulty奖励信息。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MultiFloorRaidDB` | `MultiFloorRaidDB?` | MultiFloor总力战数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### MultiFloorRaid_Login

- 协议号：`49004`
- 作用：多层总力战：进入模块并同步基础数据
- RequestClass：`MultiFloorRaidLoginRequest`
- ResponseClass：`MultiFloorRaidLoginResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
