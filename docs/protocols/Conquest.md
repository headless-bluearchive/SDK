# Conquest 协议

制约解除决战模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Conquest_GetInfo` | `42000` | 占领战：获取模块信息 | `ConquestGetInfoRequest` | `ConquestGetInfoResponse` |
| `Conquest_Conquer` | `42001` | 占领战：执行 Conquer 流程 | `ConquestConquerRequest` | `ConquestConquerResponse` |
| `Conquest_DeployEchelon` | `42004` | 占领战：布置Echelon | `ConquestConquerDeployEchelonRequest` | `ConquestConquerDeployEchelonResponse` |
| `Conquest_ManageBase` | `42005` | 占领战：执行 ManageBase 流程 | `ConquestManageBaseRequest` | `ConquestManageBaseResponse` |
| `Conquest_UpgradeBase` | `42006` | 占领战：执行 UpgradeBase 流程 | `ConquestUpgradeBaseRequest` | `ConquestUpgradeBaseResponse` |
| `Conquest_TakeEventObject` | `42007` | 占领战：Take活动Object | `ConquestTakeEventObjectRequest` | `ConquestTakeEventObjectResponse` |
| `Conquest_ReceiveCalculateRewards` | `42010` | 占领战：领取CalculateRewards | `ConquestReceiveRewardsRequest` | `ConquestReceiveRewardsResponse` |
| `Conquest_NormalizeEchelon` | `42011` | 占领战：执行 NormalizeEchelon 流程 | `ConquestNormalizeEchelonRequest` | `ConquestNormalizeEchelonResponse` |
| `Conquest_Check` | `42012` | 占领战：检查状态 | `ConquestCheckRequest` | `ConquestCheckResponse` |
| `Conquest_MainStoryGetInfo` | `42015` | 占领战：MainStory获取信息 | `ConquestMainStoryGetInfoRequest` | `ConquestMainStoryGetInfoResponse` |
| `Conquest_MainStoryConquer` | `42016` | 占领战：执行 MainStoryConquer 流程 | `ConquestMainStoryConquerRequest` | `ConquestMainStoryConquerResponse` |
| `Conquest_MainStoryCheck` | `42019` | 占领战：MainStory检查 | `ConquestMainStoryCheckRequest` | `ConquestMainStoryCheckResponse` |

## 字段结构参考

### Conquest_GetInfo

- 协议号：`42000`
- 作用：占领战：获取模块信息
- RequestClass：`ConquestGetInfoRequest`
- ResponseClass：`ConquestGetInfoResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ConquestInfoDB` | `ConquestInfoDB?` | Conquest信息数据。 |
| `ConquestedTileDBs` | `List<ConquestTileDB>?` | ConquestedTile 数据列表。 |
| `ConquestObjectDBsWrapper` | `TypedJsonWrapper<List<ConquestEventObjectDB>>?` | 制约解除决战对象DBs包装对象。 |
| `ConquestEchelonDBs` | `List<ConquestEchelonDB>?` | ConquestEchelon 数据列表。 |
| `DifficultyToStepDict` | `Dictionary<StageDifficulty, int>?` | 难度To阶段映射映射。 |
| `IsFirstEnter` | `bool` | 布尔状态。 |
| `DisplayInfos` | `IEnumerable<ConquestDisplayInfo>?` | 显示Infos列表。 |

### Conquest_Conquer

- 协议号：`42001`
- 作用：占领战：执行 Conquer 流程
- RequestClass：`ConquestConquerRequest`
- ResponseClass：`ConquestConquerResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `Difficulty` | `StageDifficulty` | 难度。 |
| `TileUniqueId` | `long` | Tile唯一 ID。 |
| `TileRewardId` | `long` | Tile奖励 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ConquestTileDB` | `ConquestTileDB?` | ConquestTile数据。 |
| `ConquestInfoDB` | `ConquestInfoDB?` | Conquest信息数据。 |
| `ConquestEventObjectDBWrapper` | `TypedJsonWrapper<List<ConquestEventObjectDB>>?` | 制约解除决战Event对象DB包装对象。 |
| `DisplayInfos` | `IEnumerable<ConquestDisplayInfo>?` | 显示Infos列表。 |

### Conquest_DeployEchelon

- 协议号：`42004`
- 作用：占领战：布置Echelon
- RequestClass：`ConquestConquerDeployEchelonRequest`
- ResponseClass：`ConquestConquerDeployEchelonResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `Difficulty` | `StageDifficulty` | 难度。 |
| `TileUniqueId` | `long` | Tile唯一 ID。 |
| `EchelonDB` | `EchelonDB?` | 编队数据。 |
| `ClanAssistUseInfo` | `ClanAssistUseInfo?` | 社团助战使用信息。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ConquestEchelonDBs` | `IEnumerable<ConquestEchelonDB>?` | ConquestEchelon 数据列表。 |
| `ConquestInfoDB` | `ConquestInfoDB?` | Conquest信息数据。 |

### Conquest_ManageBase

- 协议号：`42005`
- 作用：占领战：执行 ManageBase 流程
- RequestClass：`ConquestManageBaseRequest`
- ResponseClass：`ConquestManageBaseResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `Difficulty` | `StageDifficulty` | 难度。 |
| `TileUniqueId` | `long` | Tile唯一 ID。 |
| `ManageCount` | `int` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClearParcels` | `List<List<ParcelInfo>>?` | ClearParcels数据列表。 |
| `ConquerBonusParcels` | `List<List<ParcelInfo>>?` | ConquerBonusParcels数据列表。 |
| `BonusParcels` | `List<ParcelInfo>?` | BonusParcels数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ConquestInfoDB` | `ConquestInfoDB?` | Conquest信息数据。 |
| `ConquestEventObjectDBWrapper` | `TypedJsonWrapper<List<ConquestEventObjectDB>>?` | 制约解除决战Event对象DB包装对象。 |
| `DisplayInfos` | `IEnumerable<ConquestDisplayInfo>?` | 显示Infos列表。 |

### Conquest_UpgradeBase

- 协议号：`42006`
- 作用：占领战：执行 UpgradeBase 流程
- RequestClass：`ConquestUpgradeBaseRequest`
- ResponseClass：`ConquestUpgradeBaseResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `Difficulty` | `StageDifficulty` | 难度。 |
| `TileUniqueId` | `long` | Tile唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `UpgradeRewards` | `List<ParcelInfo>?` | Upgrade奖励数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ConquestTileDB` | `ConquestTileDB?` | ConquestTile数据。 |
| `ConquestInfoDB` | `ConquestInfoDB?` | Conquest信息数据。 |
| `ConquestEventObjectDBWrapper` | `TypedJsonWrapper<List<ConquestEventObjectDB>>?` | 制约解除决战Event对象DB包装对象。 |
| `DisplayInfos` | `IEnumerable<ConquestDisplayInfo>?` | 显示Infos列表。 |

### Conquest_TakeEventObject

- 协议号：`42007`
- 作用：占领战：Take活动Object
- RequestClass：`ConquestTakeEventObjectRequest`
- ResponseClass：`ConquestTakeEventObjectResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `ConquestObjectDBId` | `long` | ConquestObjectDB ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ConquestEventObjectDBWrapper` | `TypedJsonWrapper<ConquestEventObjectDB>?` | 制约解除决战Event对象DB包装对象。 |

### Conquest_ReceiveCalculateRewards

- 协议号：`42010`
- 作用：占领战：领取CalculateRewards
- RequestClass：`ConquestReceiveRewardsRequest`
- ResponseClass：`ConquestReceiveRewardsResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `Difficulty` | `StageDifficulty` | 难度。 |
| `Step` | `int` | 阶段。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ConquestInfoDB` | `ConquestInfoDB?` | Conquest信息数据。 |
| `ConquestTileDBs` | `List<ConquestTileDB>?` | ConquestTile 数据列表。 |

### Conquest_NormalizeEchelon

- 协议号：`42011`
- 作用：占领战：执行 NormalizeEchelon 流程
- RequestClass：`ConquestNormalizeEchelonRequest`
- ResponseClass：`ConquestNormalizeEchelonResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `Difficulty` | `StageDifficulty` | 难度。 |
| `TileUniqueId` | `long` | Tile唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ConquestEchelonDB` | `ConquestEchelonDB?` | Conquest编队数据。 |

### Conquest_Check

- 协议号：`42012`
- 作用：占领战：检查状态
- RequestClass：`ConquestCheckRequest`
- ResponseClass：`ConquestCheckResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CanReceiveCalculateReward` | `bool` | CanReceiveCalculate奖励奖励信息。 |
| `AlarmPhaseToShow` | `Nullable<int>` | 提醒阶段ToShow。 |
| `ParcelConsumeCumulatedAmount` | `long` | 奖励包消耗Cumulated数量数量。 |
| `ConquestSummary` | `ConquestSummary?` | 制约解除决战摘要。 |

### Conquest_MainStoryGetInfo

- 协议号：`42015`
- 作用：占领战：MainStory获取信息
- RequestClass：`ConquestMainStoryGetInfoRequest`
- ResponseClass：`ConquestMainStoryGetInfoResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ConquestInfoDB` | `ConquestInfoDB?` | Conquest信息数据。 |
| `ConquestedTileDBs` | `List<ConquestTileDB>?` | ConquestedTile 数据列表。 |
| `DifficultyToStepDict` | `Dictionary<StageDifficulty, int>?` | 难度To阶段映射映射。 |
| `IsFirstEnter` | `bool` | 布尔状态。 |

### Conquest_MainStoryConquer

- 协议号：`42016`
- 作用：占领战：执行 MainStoryConquer 流程
- RequestClass：`ConquestMainStoryConquerRequest`
- ResponseClass：`ConquestMainStoryConquerResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `Difficulty` | `StageDifficulty` | 难度。 |
| `TileUniqueId` | `long` | Tile唯一 ID。 |
| `TileRewardId` | `long` | Tile奖励 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ConquestTileDB` | `ConquestTileDB?` | ConquestTile数据。 |
| `ConquestInfoDB` | `ConquestInfoDB?` | Conquest信息数据。 |
| `DisplayInfos` | `IEnumerable<ConquestDisplayInfo>?` | 显示Infos列表。 |

### Conquest_MainStoryCheck

- 协议号：`42019`
- 作用：占领战：MainStory检查
- RequestClass：`ConquestMainStoryCheckRequest`
- ResponseClass：`ConquestMainStoryCheckResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ConquestMainStorySummary` | `ConquestMainStorySummary?` | 制约解除决战MainStory摘要。 |
