# EliminateRaid 协议

综合战术考试模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `EliminateRaid_Login` | `45000` | 制约解除决战：进入模块并同步基础数据 | `EliminateRaidLoginRequest` | `EliminateRaidLoginResponse` |
| `EliminateRaid_Lobby` | `45001` | 制约解除决战：获取或进入模块大厅 | `EliminateRaidLobbyRequest` | `EliminateRaidLobbyResponse` |
| `EliminateRaid_OpponentList` | `45002` | 制约解除决战：获取对手列表 | `EliminateRaidOpponentListRequest` | `EliminateRaidOpponentListResponse` |
| `EliminateRaid_GetBestTeam` | `45003` | 制约解除决战：获取BestTeam | `EliminateRaidGetBestTeamRequest` | `EliminateRaidGetBestTeamResponse` |
| `EliminateRaid_Sweep` | `45008` | 制约解除决战：执行扫荡 | `EliminateRaidSweepRequest` | `EliminateRaidSweepResponse` |
| `EliminateRaid_SeasonReward` | `45009` | 制约解除决战：领取赛季奖励 | `EliminateRaidSeasonRewardRequest` | `EliminateRaidSeasonRewardResponse` |
| `EliminateRaid_RankingReward` | `45010` | 制约解除决战：排行奖励 | `EliminateRaidRankingRewardRequest` | `EliminateRaidRankingRewardResponse` |
| `EliminateRaid_LimitedReward` | `45011` | 制约解除决战：Limited奖励 | `EliminateRaidLimitedRewardRequest` | `EliminateRaidLimitedRewardResponse` |
| `EliminateRaid_RankingIndex` | `45012` | 制约解除决战：排行Index | `EliminateRaidRankingIndexRequest` | `EliminateRaidRankingIndexResponse` |

## 字段结构参考

### EliminateRaid_Login

- 协议号：`45000`
- 作用：制约解除决战：进入模块并同步基础数据
- RequestClass：`EliminateRaidLoginRequest`
- ResponseClass：`EliminateRaidLoginResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SeasonType` | `RaidSeasonType` | 赛季类型。 |
| `CanReceiveRankingReward` | `bool` | CanReceiveRanking奖励奖励信息。 |
| `ReceiveLimitedRewardIds` | `List<long>?` | ID 列表。 |
| `SweepPointByRaidUniqueId` | `Dictionary<long, long>?` | SweepPointBy总力战唯一 ID。 |
| `LastSettledRanking` | `long` | 上次结算排名。 |
| `LastSettledTier` | `Nullable<int>` | 上次结算档位。 |

### EliminateRaid_Lobby

- 协议号：`45001`
- 作用：制约解除决战：获取或进入模块大厅
- RequestClass：`EliminateRaidLobbyRequest`
- ResponseClass：`EliminateRaidLobbyResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SeasonType` | `RaidSeasonType` | 赛季类型。 |
| `RaidGiveUpDB` | `RaidGiveUpDB?` | 总力战GiveUp数据。 |
| `RaidLobbyInfoDB` | `EliminateRaidLobbyInfoDB?` | 总力战Lobby信息数据。 |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### EliminateRaid_OpponentList

- 协议号：`45002`
- 作用：制约解除决战：获取对手列表
- RequestClass：`EliminateRaidOpponentListRequest`
- ResponseClass：`EliminateRaidOpponentListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Rank` | `Nullable<long>` | 排名排名。 |
| `Score` | `Nullable<long>` | 分数。 |
| `BossGroupIndex` | `Nullable<int>` | BossGroup索引索引。 |
| `IsUpper` | `bool` | 布尔状态。 |
| `IsFirstRequest` | `bool` | IsFirstRequest 子请求。 |
| `SearchType` | `RankingSearchType` | 搜索类型。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `OpponentUserDBs` | `List<EliminateRaidUserDB>?` | OpponentUser 数据列表。 |

### EliminateRaid_GetBestTeam

- 协议号：`45003`
- 作用：制约解除决战：获取BestTeam
- RequestClass：`EliminateRaidGetBestTeamRequest`
- ResponseClass：`EliminateRaidGetBestTeamResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SearchAccountId` | `long` | Search账号 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RaidTeamSettingDBsDict` | `Dictionary<string, List<RaidTeamSettingDB>>?` | 总力战队伍设置映射。 |

### EliminateRaid_Sweep

- 协议号：`45008`
- 作用：制约解除决战：执行扫荡
- RequestClass：`EliminateRaidSweepRequest`
- ResponseClass：`EliminateRaidSweepResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `UniqueId` | `long` | 唯一 ID。 |
| `SweepCount` | `int` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TotalSeasonPoint` | `long` | 赛季总分。 |
| `Rewards` | `List<List<ParcelInfo>>?` | 奖励数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### EliminateRaid_SeasonReward

- 协议号：`45009`
- 作用：制约解除决战：领取赛季奖励
- RequestClass：`EliminateRaidSeasonRewardRequest`
- ResponseClass：`EliminateRaidSeasonRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ReceiveRewardIds` | `List<long>?` | ID 列表。 |

### EliminateRaid_RankingReward

- 协议号：`45010`
- 作用：制约解除决战：排行奖励
- RequestClass：`EliminateRaidRankingRewardRequest`
- ResponseClass：`EliminateRaidRankingRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ReceivedRankingRewardId` | `long` | ReceivedRanking奖励 ID。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### EliminateRaid_LimitedReward

- 协议号：`45011`
- 作用：制约解除决战：Limited奖励
- RequestClass：`EliminateRaidLimitedRewardRequest`
- ResponseClass：`EliminateRaidLimitedRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ReceiveRewardIds` | `List<long>?` | ID 列表。 |

### EliminateRaid_RankingIndex

- 协议号：`45012`
- 作用：制约解除决战：排行Index
- RequestClass：`EliminateRaidRankingIndexRequest`
- ResponseClass：`EliminateRaidRankingIndexResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RankBrackets` | `List<RaidRankBracket>?` | 排名Brackets数据列表。 |
