# Raid 协议

总力战模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Raid_List` | `17000` | 总力战：获取列表数据 | `RaidListRequest` | `RaidListResponse` |
| `Raid_CompleteList` | `17001` | 总力战：Complete列表 | `RaidCompleteListRequest` | `RaidCompleteListResponse` |
| `Raid_Detail` | `17002` | 总力战：执行 Detail 流程 | `RaidDetailRequest` | `RaidDetailResponse` |
| `Raid_Search` | `17003` | 总力战：搜索 | `RaidSearchRequest` | `RaidSearchResponse` |
| `Raid_BattleUpdate` | `17006` | 总力战：战斗更新 | `RaidBattleUpdateRequest` | `RaidBattleUpdateResponse` |
| `Raid_Reward` | `17008` | 总力战：奖励 | `RaidRewardRequest` | `RaidRewardResponse` |
| `Raid_RewardAll` | `17009` | 总力战：奖励全部 | `RaidRewardAllRequest` | `RaidRewardAllResponse` |
| `Raid_Revive` | `17010` | 总力战：执行 Revive 流程 | `` | `` |
| `Raid_Share` | `17011` | 总力战：执行 Share 流程 | `RaidShareRequest` | `RaidShareResponse` |
| `Raid_SeasonInfo` | `17012` | 总力战：赛季信息 | `` | `` |
| `Raid_SeasonReward` | `17013` | 总力战：领取赛季奖励 | `RaidSeasonRewardRequest` | `RaidSeasonRewardResponse` |
| `Raid_Lobby` | `17014` | 总力战：获取或进入模块大厅 | `RaidLobbyRequest` | `RaidLobbyResponse` |
| `Raid_OpponentList` | `17016` | 总力战：获取对手列表 | `RaidOpponentListRequest` | `RaidOpponentListResponse` |
| `Raid_RankingReward` | `17017` | 总力战：排行奖励 | `RaidRankingRewardRequest` | `RaidRankingRewardResponse` |
| `Raid_Login` | `17018` | 总力战：进入模块并同步基础数据 | `RaidLoginRequest` | `RaidLoginResponse` |
| `Raid_Sweep` | `17019` | 总力战：执行扫荡 | `RaidSweepRequest` | `RaidSweepResponse` |
| `Raid_GetBestTeam` | `17020` | 总力战：获取BestTeam | `RaidGetBestTeamRequest` | `RaidGetBestTeamResponse` |
| `Raid_RankingIndex` | `17021` | 总力战：排行Index | `RaidRankingIndexRequest` | `RaidRankingIndexResponse` |

## 字段结构参考

### Raid_List

- 协议号：`17000`
- 作用：总力战：获取列表数据
- RequestClass：`RaidListRequest`
- ResponseClass：`RaidListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidBossGroup` | `string?` | 总力战 Boss 分组。 |
| `RaidDifficulty` | `Difficulty` | 总力战难度。 |
| `RaidRoomSortOption` | `RaidRoomSortOption` | 总力战RoomSort选项选项。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CreateRaidDBs` | `List<RaidDB>?` | CreateRaid 数据列表。 |
| `EnterRaidDBs` | `List<RaidDB>?` | EnterRaid 数据列表。 |
| `ListRaidDBs` | `List<RaidDB>?` | ListRaid 数据列表。 |

### Raid_CompleteList

- 协议号：`17001`
- 作用：总力战：Complete列表
- RequestClass：`RaidCompleteListRequest`
- ResponseClass：`RaidCompleteListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidDBs` | `List<RaidDB>?` | Raid 数据列表。 |
| `StackedDamage` | `long` | 累计伤害。 |
| `ReceiveRewardId` | `List<long>?` | Receive奖励 ID。 |
| `CurSeasonUniqueId` | `long` | Cur赛季唯一 ID。 |

### Raid_Detail

- 协议号：`17002`
- 作用：总力战：执行 Detail 流程
- RequestClass：`RaidDetailRequest`
- ResponseClass：`RaidDetailResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidServerId` | `long` | 总力战服务器 ID。 |
| `RaidUniqueId` | `long` | 总力战唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidDetailDB` | `RaidDetailDB?` | 总力战Detail数据。 |
| `ParticipateCharacterServerIds` | `List<long>?` | ID 列表。 |

### Raid_Search

- 协议号：`17003`
- 作用：总力战：搜索
- RequestClass：`RaidSearchRequest`
- ResponseClass：`RaidSearchResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SecretCode` | `string?` | 秘密代码。 |
| `Tags` | `List<string>?` | Tags数据列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidDBs` | `List<RaidDB>?` | Raid 数据列表。 |

### Raid_BattleUpdate

- 协议号：`17006`
- 作用：总力战：战斗更新
- RequestClass：`RaidBattleUpdateRequest`
- ResponseClass：`RaidBattleUpdateResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidServerId` | `long` | 总力战服务器 ID。 |
| `RaidBossIndex` | `int` | 总力战Boss索引索引。 |
| `CumulativeDamage` | `long` | 累计伤害。 |
| `CumulativeGroggyPoint` | `long` | 累计 groggy 点数。 |
| `Debuffs` | `list[DebuffDescription]` | Debuffs数据列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidBattleDB` | `RaidBattleDB?` | 总力战战斗数据。 |

### Raid_Reward

- 协议号：`17008`
- 作用：总力战：奖励
- RequestClass：`RaidRewardRequest`
- ResponseClass：`RaidRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidServerId` | `long` | 总力战服务器 ID。 |
| `IsPractice` | `bool` | 布尔状态。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RankingPoint` | `long` | 排名分数。 |
| `BestRankingPoint` | `long` | 最高排名分数。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Raid_RewardAll

- 协议号：`17009`
- 作用：总力战：奖励全部
- RequestClass：`RaidRewardAllRequest`
- ResponseClass：`RaidRewardAllResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Raid_Revive

- 协议号：`17010`
- 作用：总力战：执行 Revive 流程
- RequestClass：``
- ResponseClass：``
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Raid_Share

- 协议号：`17011`
- 作用：总力战：执行 Share 流程
- RequestClass：`RaidShareRequest`
- ResponseClass：`RaidShareResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidServerId` | `long` | 总力战服务器 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidDB` | `RaidDB?` | 总力战数据。 |

### Raid_SeasonInfo

- 协议号：`17012`
- 作用：总力战：赛季信息
- RequestClass：``
- ResponseClass：``
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Raid_SeasonReward

- 协议号：`17013`
- 作用：总力战：领取赛季奖励
- RequestClass：`RaidSeasonRewardRequest`
- ResponseClass：`RaidSeasonRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ReceiveRewardIds` | `List<long>?` | ID 列表。 |

### Raid_Lobby

- 协议号：`17014`
- 作用：总力战：获取或进入模块大厅
- RequestClass：`RaidLobbyRequest`
- ResponseClass：`RaidLobbyResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SeasonType` | `RaidSeasonType` | 赛季类型。 |
| `RaidGiveUpDB` | `RaidGiveUpDB?` | 总力战GiveUp数据。 |
| `RaidLobbyInfoDB` | `SingleRaidLobbyInfoDB?` | 总力战Lobby信息数据。 |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Raid_OpponentList

- 协议号：`17016`
- 作用：总力战：获取对手列表
- RequestClass：`RaidOpponentListRequest`
- ResponseClass：`RaidOpponentListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Rank` | `Nullable<long>` | 排名排名。 |
| `Score` | `Nullable<long>` | 分数。 |
| `IsUpper` | `bool` | 布尔状态。 |
| `IsFirstRequest` | `bool` | IsFirstRequest 子请求。 |
| `SearchType` | `RankingSearchType` | 搜索类型。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `OpponentUserDBs` | `List<SingleRaidUserDB>?` | OpponentUser 数据列表。 |

### Raid_RankingReward

- 协议号：`17017`
- 作用：总力战：排行奖励
- RequestClass：`RaidRankingRewardRequest`
- ResponseClass：`RaidRankingRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ReceivedRankingRewardId` | `long` | ReceivedRanking奖励 ID。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Raid_Login

- 协议号：`17018`
- 作用：总力战：进入模块并同步基础数据
- RequestClass：`RaidLoginRequest`
- ResponseClass：`RaidLoginResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SeasonType` | `RaidSeasonType` | 赛季类型。 |
| `CanReceiveRankingReward` | `bool` | CanReceiveRanking奖励奖励信息。 |
| `LastSettledRanking` | `long` | 上次结算排名。 |
| `LastSettledTier` | `Nullable<int>` | 上次结算档位。 |

### Raid_Sweep

- 协议号：`17019`
- 作用：总力战：执行扫荡
- RequestClass：`RaidSweepRequest`
- ResponseClass：`RaidSweepResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `UniqueId` | `long` | 唯一 ID。 |
| `SweepCount` | `long` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TotalSeasonPoint` | `long` | 赛季总分。 |
| `Rewards` | `List<List<ParcelInfo>>?` | 奖励数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Raid_GetBestTeam

- 协议号：`17020`
- 作用：总力战：获取BestTeam
- RequestClass：`RaidGetBestTeamRequest`
- ResponseClass：`RaidGetBestTeamResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SearchAccountId` | `long` | Search账号 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidTeamSettingDBs` | `List<RaidTeamSettingDB>?` | RaidTeamSetting 数据列表。 |

### Raid_RankingIndex

- 协议号：`17021`
- 作用：总力战：排行Index
- RequestClass：`RaidRankingIndexRequest`
- ResponseClass：`RaidRankingIndexResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RankBrackets` | `List<RaidRankBracket>?` | 排名Brackets数据列表。 |
