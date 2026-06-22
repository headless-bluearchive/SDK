# EventContent 协议

EventContent 是限时活动的主协议集合。SDK 文档只保留活动状态、活动商店、常驻列表、扫荡相关和普通资料查询类协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 接入原则

- 先通过登录同步、活动列表或活动大厅方法确认活动是否开放。
- 不写死 `EventContentId`、关卡 ID、商店 ID、活动货币或轮次。
- 只读查询和扫荡类协议可以优先接入。
- 会直接影响公平性的活动协议不在 SDK 文档中提供字段结构。
- 已删除活动翻卡开奖、Treasure 翻牌、Concentration 翻卡、Box/Fortune 招募购买或刷新等会影响游戏公平性的部分。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `EventContent_AdventureList` | `30000` | 活动内容：Adventure列表 | `EventContentAdventureListRequest` | `EventContentAdventureListResponse` |
| `EventContent_EnterMainStage` | `30001` | 活动内容：进入Main关卡 | `EventContentEnterMainStageRequest` | `EventContentEnterMainStageResponse` |
| `EventContent_ConfirmMainStage` | `30002` | 活动内容：ConfirmMain关卡 | `EventContentConfirmMainStageRequest` | `EventContentConfirmMainStageResponse` |
| `EventContent_EnterSubStage` | `30005` | 活动内容：进入Sub关卡 | `EventContentEnterSubStageRequest` | `EventContentEnterSubStageResponse` |
| `EventContent_DeployEchelon` | `30007` | 活动内容：布置Echelon | `EventContentDeployEchelonRequest` | `EventContentDeployEchelonResponse` |
| `EventContent_WithdrawEchelon` | `30008` | 活动内容：执行 WithdrawEchelon 流程 | `EventContentWithdrawEchelonRequest` | `EventContentWithdrawEchelonResponse` |
| `EventContent_MapMove` | `30009` | 活动内容：执行 MapMove 流程 | `EventContentMapMoveRequest` | `EventContentMapMoveResponse` |
| `EventContent_EndTurn` | `30010` | 活动内容：执行 EndTurn 流程 | `EventContentEndTurnRequest` | `EventContentEndTurnResponse` |
| `EventContent_Portal` | `30012` | 活动内容：执行 Portal 流程 | `EventContentPortalRequest` | `EventContentPortalResponse` |
| `EventContent_PurchasePlayCountHardStage` | `30013` | 活动内容：PurchasePlayCountHard关卡 | `EventContentPurchasePlayCountHardStageRequest` | `EventContentPurchasePlayCountHardStageResponse` |
| `EventContent_ShopList` | `30014` | 活动内容：商店列表 | `EventContentShopListRequest` | `EventContentShopListResponse` |
| `EventContent_ShopRefresh` | `30015` | 活动内容：商店刷新 | `EventContentShopRefreshRequest` | `EventContentShopRefreshResponse` |
| `EventContent_ReceiveStageTotalReward` | `30016` | 活动内容：领取关卡Total奖励 | `EventContentReceiveStageTotalRewardRequest` | `EventContentReceiveStageTotalRewardResponse` |
| `EventContent_EnterMainGroundStage` | `30017` | 活动内容：进入MainGround关卡 | `EventContentEnterMainGroundStageRequest` | `EventContentEnterMainGroundStageResponse` |
| `EventContent_ShopBuyMerchandise` | `30019` | 活动内容：商店购买Merchandise | `EventContentShopBuyMerchandiseRequest` | `EventContentShopBuyMerchandiseResponse` |
| `EventContent_ShopBuyRefreshMerchandise` | `30020` | 活动内容：商店购买刷新Merchandise | `EventContentShopBuyRefreshMerchandiseRequest` | `EventContentShopBuyRefreshMerchandiseResponse` |
| `EventContent_SelectBuff` | `30021` | 活动内容：执行 SelectBuff 流程 | `EventContentSelectBuffRequest` | `EventContentSelectBuffResponse` |
| `EventContent_BoxGachaShopList` | `30022` | 活动内容：Box招募商店列表 | `EventContentBoxGachaShopListRequest` | `EventContentBoxGachaShopListResponse` |
| `EventContent_CollectionList` | `30025` | 活动内容：Collection列表 | `EventContentCollectionListRequest` | `EventContentCollectionListResponse` |
| `EventContent_CollectionForMission` | `30026` | 活动内容：CollectionFor任务 | `EventContentCollectionForMissionRequest` | `EventContentCollectionForMissionResponse` |
| `EventContent_ScenarioGroupHistoryUpdate` | `30027` | 活动内容：剧情Group历史记录更新 | `EventContentScenarioGroupHistoryUpdateRequest` | `EventContentScenarioGroupHistoryUpdateResponse` |
| `EventContent_RestartMainStage` | `30031` | 活动内容：RestartMain关卡 | `EventContentRestartMainStageRequest` | `EventContentRestartMainStageResponse` |
| `EventContent_LocationGetInfo` | `30032` | 活动内容：Location获取信息 | `EventContentLocationGetInfoRequest` | `EventContentLocationGetInfoResponse` |
| `EventContent_LocationAttendSchedule` | `30033` | 活动内容：执行 LocationAttendSchedule 流程 | `EventContentLocationAttendScheduleRequest` | `EventContentLocationAttendScheduleResponse` |
| `EventContent_SubEventLobby` | `30035` | 活动内容：Sub活动大厅 | `EventContentSubEventLobbyRequest` | `EventContentSubEventLobbyResponse` |
| `EventContent_EnterStoryStage` | `30036` | 活动内容：进入Story关卡 | `EventContentEnterStoryStageRequest` | `EventContentEnterStoryStageResponse` |
| `EventContent_DiceRaceLobby` | `30038` | 活动内容：DiceRace大厅 | `EventContentDiceRaceLobbyRequest` | `EventContentDiceRaceLobbyResponse` |
| `EventContent_DiceRaceRoll` | `30039` | 活动内容：执行 DiceRaceRoll 流程 | `EventContentDiceRaceRollRequest` | `EventContentDiceRaceRollResponse` |
| `EventContent_DiceRaceLapReward` | `30040` | 活动内容：DiceRaceLap奖励 | `EventContentDiceRaceLapRewardRequest` | `EventContentDiceRaceLapRewardResponse` |
| `EventContent_PermanentList` | `30041` | 活动内容：常驻列表 | `EventContentPermanentListRequest` | `EventContentPermanentListResponse` |
| `EventContent_DiceRaceUseItem` | `30042` | 活动内容：DiceRace使用Item | `EventContentDiceRaceUseItemRequest` | `EventContentDiceRaceUseItemResponse` |
| `EventContent_TreasureLobby` | `30044` | 活动内容：Treasure大厅 | `EventContentTreasureLobbyRequest` | `EventContentTreasureLobbyResponse` |
| `EventContent_TreasureNextRound` | `30046` | 活动内容：执行 TreasureNextRound 流程 | `EventContentTreasureNextRoundRequest` | `EventContentTreasureNextRoundResponse` |
| `EventContent_ClueSearchGetInfo` | `30051` | 活动内容：Clue搜索获取信息 | `EventContentClueSearchGetInfoRequest` | `EventContentClueSearchGetInfoResponse` |
| `EventContent_ClueSearchSubmit` | `30052` | 活动内容：Clue搜索提交 | `EventContentClueSearchSubmitRequest` | `EventContentClueSearchSubmitResponse` |
| `EventContent_ClueSearchRoundComplete` | `30053` | 活动内容：Clue搜索RoundComplete | `EventContentClueSearchRoundCompleteRequest` | `EventContentClueSearchRoundCompleteResponse` |

## 字段结构参考

### EventContent_AdventureList

- 协议号：`30000`
- 作用：活动内容：Adventure列表
- RequestClass：`EventContentAdventureListRequest`
- ResponseClass：`EventContentAdventureListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageHistoryDBs` | `List<CampaignStageHistoryDB>?` | StageHistory 数据列表。 |
| `StrategyObjecthistoryDBs` | `List<StrategyObjectHistoryDB>?` | StrategyObjecthistory 数据列表。 |
| `EventContentBonusRewardDBs` | `List<EventContentBonusRewardDB>?` | EventContentBonusReward 数据列表。 |
| `AlreadyReceiveRewardId` | `List<long>?` | AlreadyReceive奖励 ID。 |
| `StagePoint` | `long` | 关卡点数。 |

### EventContent_EnterMainStage

- 协议号：`30001`
- 作用：活动内容：进入Main关卡
- RequestClass：`EventContentEnterMainStageRequest`
- ResponseClass：`EventContentEnterMainStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `EventContentMainStageSaveDB?` | SaveData数据。 |
| `IsOnSubEvent` | `bool` | 布尔状态。 |

### EventContent_ConfirmMainStage

- 协议号：`30002`
- 作用：活动内容：ConfirmMain关卡
- RequestClass：`EventContentConfirmMainStageRequest`
- ResponseClass：`EventContentConfirmMainStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `SaveDataDB` | `EventContentMainStageSaveDB?` | SaveData数据。 |

### EventContent_EnterSubStage

- 协议号：`30005`
- 作用：活动内容：进入Sub关卡
- RequestClass：`EventContentEnterSubStageRequest`
- ResponseClass：`EventContentEnterSubStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `LastEnterStageEchelonNumber` | `long` | 上次进入关卡的编队编号。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `SaveDataDB` | `EventContentSubStageSaveDB?` | SaveData数据。 |
| `CampaignStageHistoryDB` | `CampaignStageHistoryDB?` | 战役关卡历史数据。 |

### EventContent_DeployEchelon

- 协议号：`30007`
- 作用：活动内容：布置Echelon
- RequestClass：`EventContentDeployEchelonRequest`
- ResponseClass：`EventContentDeployEchelonResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `DeployedEchelons` | `List<HexaUnit>?` | DeployedEchelons数据列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `EventContentMainStageSaveDB?` | SaveData数据。 |

### EventContent_WithdrawEchelon

- 协议号：`30008`
- 作用：活动内容：执行 WithdrawEchelon 流程
- RequestClass：`EventContentWithdrawEchelonRequest`
- ResponseClass：`EventContentWithdrawEchelonResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `WithdrawEchelonEntityId` | `List<long>?` | Withdraw编队Entity ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `EventContentMainStageSaveDB?` | SaveData数据。 |
| `WithdrawEchelonDBs` | `List<EchelonDB>?` | WithdrawEchelon 数据列表。 |

### EventContent_MapMove

- 协议号：`30009`
- 作用：活动内容：执行 MapMove 流程
- RequestClass：`EventContentMapMoveRequest`
- ResponseClass：`EventContentMapMoveResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `EchelonEntityId` | `long` | 编队Entity ID。 |
| `DestPosition` | `HexLocation` | 目标位置。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `EventContentMainStageSaveDB?` | SaveData数据。 |
| `EchelonEntityId` | `long` | 编队Entity ID。 |
| `StrategyObject` | `Strategy?` | 策略地图对象。 |
| `StrategyObjectParcelInfos` | `List<ParcelInfo>?` | StrategyObject奖励包Infos数据列表。 |

### EventContent_EndTurn

- 协议号：`30010`
- 作用：活动内容：执行 EndTurn 流程
- RequestClass：`EventContentEndTurnRequest`
- ResponseClass：`EventContentEndTurnResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `EventContentMainStageSaveDB?` | SaveData数据。 |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |

### EventContent_Portal

- 协议号：`30012`
- 作用：活动内容：执行 Portal 流程
- RequestClass：`EventContentPortalRequest`
- ResponseClass：`EventContentPortalResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `EchelonEntityId` | `long` | 编队Entity ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `EventContentMainStageSaveDB?` | SaveData数据。 |

### EventContent_PurchasePlayCountHardStage

- 协议号：`30013`
- 作用：活动内容：PurchasePlayCountHard关卡
- RequestClass：`EventContentPurchasePlayCountHardStageRequest`
- ResponseClass：`EventContentPurchasePlayCountHardStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `CampaignStageHistoryDB` | `CampaignStageHistoryDB?` | 战役关卡历史数据。 |

### EventContent_ShopList

- 协议号：`30014`
- 作用：活动内容：商店列表
- RequestClass：`EventContentShopListRequest`
- ResponseClass：`EventContentShopListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `CategoryList` | `List<ShopCategoryType>?` | CategoryList数据列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ShopInfos` | `List<ShopInfoDB>?` | 商店Infos数据列表。 |
| `ShopEligmaHistoryDBs` | `List<ShopEligmaHistoryDB>?` | ShopEligmaHistory 数据列表。 |

### EventContent_ShopRefresh

- 协议号：`30015`
- 作用：活动内容：商店刷新
- RequestClass：`EventContentShopRefreshRequest`
- ResponseClass：`EventContentShopRefreshResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `ShopCategoryType` | `ShopCategoryType` | 商店分类类型。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ShopInfoDB` | `ShopInfoDB?` | 商店信息数据。 |

### EventContent_ReceiveStageTotalReward

- 协议号：`30016`
- 作用：活动内容：领取关卡Total奖励
- RequestClass：`EventContentReceiveStageTotalRewardRequest`
- ResponseClass：`EventContentReceiveStageTotalRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `AlreadyReceiveRewardId` | `List<long>?` | AlreadyReceive奖励 ID。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### EventContent_EnterMainGroundStage

- 协议号：`30017`
- 作用：活动内容：进入MainGround关卡
- RequestClass：`EventContentEnterMainGroundStageRequest`
- ResponseClass：`EventContentEnterMainGroundStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `LastEnterStageEchelonNumber` | `long` | 上次进入关卡的编队编号。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `SaveDataDB` | `EventContentMainGroundStageSaveDB?` | SaveData数据。 |
| `CampaignStageHistoryDB` | `CampaignStageHistoryDB?` | 战役关卡历史数据。 |

### EventContent_ShopBuyMerchandise

- 协议号：`30019`
- 作用：活动内容：商店购买Merchandise
- RequestClass：`EventContentShopBuyMerchandiseRequest`
- ResponseClass：`EventContentShopBuyMerchandiseResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `IsRefreshMerchandise` | `bool` | 布尔状态。 |
| `ShopUniqueId` | `long` | 商店唯一 ID。 |
| `GoodsUniqueId` | `long` | Goods唯一 ID。 |
| `PurchaseCount` | `long` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `MailDB` | `MailDB?` | 邮件数据。 |
| `ShopProductDB` | `ShopProductDB?` | 商店商品数据。 |
| `EventContentCollectionDBs` | `List<EventContentCollectionDB>?` | EventContentCollection 数据列表。 |

### EventContent_ShopBuyRefreshMerchandise

- 协议号：`30020`
- 作用：活动内容：商店购买刷新Merchandise
- RequestClass：`EventContentShopBuyRefreshMerchandiseRequest`
- ResponseClass：`EventContentShopBuyRefreshMerchandiseResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `ShopUniqueIds` | `List<long>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `MailDB` | `MailDB?` | 邮件数据。 |
| `ShopProductDB` | `List<ShopProductDB>?` | 商店商品数据列表。 |
| `EventContentCollectionDBs` | `List<EventContentCollectionDB>?` | EventContentCollection 数据列表。 |

### EventContent_SelectBuff

- 协议号：`30021`
- 作用：活动内容：执行 SelectBuff 流程
- RequestClass：`EventContentSelectBuffRequest`
- ResponseClass：`EventContentSelectBuffResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SelectedBuffId` | `long` | SelectedBuff ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `EventContentMainStageSaveDB?` | SaveData数据。 |

### EventContent_BoxGachaShopList

- 协议号：`30022`
- 作用：活动内容：Box招募商店列表
- RequestClass：`EventContentBoxGachaShopListRequest`
- ResponseClass：`EventContentBoxGachaShopListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BoxGachaDB` | `EventContentBoxGachaDB?` | Box招募数据。 |
| `BoxGachaGroupIdByCount` | `Dictionary<long, long>?` | 数量。 |

### EventContent_CollectionList

- 协议号：`30025`
- 作用：活动内容：Collection列表
- RequestClass：`EventContentCollectionListRequest`
- ResponseClass：`EventContentCollectionListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `GroupId` | `Nullable<long>` | Group ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentUnlockCGDBs` | `List<EventContentCollectionDB>?` | EventContentUnlockCG 数据列表。 |

### EventContent_CollectionForMission

- 协议号：`30026`
- 作用：活动内容：CollectionFor任务
- RequestClass：`EventContentCollectionForMissionRequest`
- ResponseClass：`EventContentCollectionForMissionResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentCollectionDBs` | `List<EventContentCollectionDB>?` | EventContentCollection 数据列表。 |

### EventContent_ScenarioGroupHistoryUpdate

- 协议号：`30027`
- 作用：活动内容：剧情Group历史记录更新
- RequestClass：`EventContentScenarioGroupHistoryUpdateRequest`
- ResponseClass：`EventContentScenarioGroupHistoryUpdateResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ScenarioGroupUniqueId` | `long` | 剧情Group唯一 ID。 |
| `ScenarioType` | `long` | 剧情类型。 |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ScenarioGroupHistoryDBs` | `List<ScenarioGroupHistoryDB>?` | ScenarioGroupHistory 数据列表。 |
| `EventContentCollectionDBs` | `List<EventContentCollectionDB>?` | EventContentCollection 数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### EventContent_RestartMainStage

- 协议号：`30031`
- 作用：活动内容：RestartMain关卡
- RequestClass：`EventContentRestartMainStageRequest`
- ResponseClass：`EventContentRestartMainStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `SaveDataDB` | `EventContentMainStageSaveDB?` | SaveData数据。 |

### EventContent_LocationGetInfo

- 协议号：`30032`
- 作用：活动内容：Location获取信息
- RequestClass：`EventContentLocationGetInfoRequest`
- ResponseClass：`EventContentLocationGetInfoResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentLocationDB` | `EventContentLocationDB?` | EventContent地点数据。 |

### EventContent_LocationAttendSchedule

- 协议号：`30033`
- 作用：活动内容：执行 LocationAttendSchedule 流程
- RequestClass：`EventContentLocationAttendScheduleRequest`
- ResponseClass：`EventContentLocationAttendScheduleResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `ZoneId` | `long` | 区域 ID。 |
| `Count` | `long` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentLocationDB` | `EventContentLocationDB?` | EventContent地点数据。 |
| `EventContentCollectionDBs` | `IEnumerable<EventContentCollectionDB>?` | EventContentCollection 数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ExtraRewards` | `List<ParcelInfo>?` | 额外奖励列表。 |

### EventContent_SubEventLobby

- 协议号：`30035`
- 作用：活动内容：Sub活动大厅
- RequestClass：`EventContentSubEventLobbyRequest`
- ResponseClass：`EventContentSubEventLobbyResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentChangeDB` | `EventContentChangeDB?` | EventContentChange数据。 |
| `IsOnSubEvent` | `bool` | 布尔状态。 |

### EventContent_EnterStoryStage

- 协议号：`30036`
- 作用：活动内容：进入Story关卡
- RequestClass：`EventContentEnterStoryStageRequest`
- ResponseClass：`EventContentEnterStoryStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `SaveDataDB` | `EventContentStoryStageSaveDB?` | SaveData数据。 |

### EventContent_DiceRaceLobby

- 协议号：`30038`
- 作用：活动内容：DiceRace大厅
- RequestClass：`EventContentDiceRaceLobbyRequest`
- ResponseClass：`EventContentDiceRaceLobbyResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `DiceRaceDB` | `EventContentDiceRaceDB?` | DiceRace数据。 |

### EventContent_DiceRaceRoll

- 协议号：`30039`
- 作用：活动内容：执行 DiceRaceRoll 流程
- RequestClass：`EventContentDiceRaceRollRequest`
- ResponseClass：`EventContentDiceRaceRollResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `DiceRaceDB` | `EventContentDiceRaceDB?` | DiceRace数据。 |
| `DiceResults` | `List<EventContentDiceResult>?` | DiceResults数据列表。 |
| `EventContentCollectionDBs` | `List<EventContentCollectionDB>?` | EventContentCollection 数据列表。 |

### EventContent_DiceRaceLapReward

- 协议号：`30040`
- 作用：活动内容：DiceRaceLap奖励
- RequestClass：`EventContentDiceRaceLapRewardRequest`
- ResponseClass：`EventContentDiceRaceLapRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `DiceRaceDB` | `EventContentDiceRaceDB?` | DiceRace数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### EventContent_PermanentList

- 协议号：`30041`
- 作用：活动内容：常驻列表
- RequestClass：`EventContentPermanentListRequest`
- ResponseClass：`EventContentPermanentListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PermanentDBs` | `List<EventContentPermanentDB>?` | Permanent 数据列表。 |

### EventContent_DiceRaceUseItem

- 协议号：`30042`
- 作用：活动内容：DiceRace使用Item
- RequestClass：`EventContentDiceRaceUseItemRequest`
- ResponseClass：`EventContentDiceRaceUseItemResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `DiceRaceResultType` | `EventContentDiceRaceResultType` | 骰子赛跑结果类型。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `DiceRaceDB` | `EventContentDiceRaceDB?` | DiceRace数据。 |
| `DiceResults` | `List<EventContentDiceResult>?` | DiceResults数据列表。 |
| `EventContentCollectionDBs` | `List<EventContentCollectionDB>?` | EventContentCollection 数据列表。 |

### EventContent_TreasureLobby

- 协议号：`30044`
- 作用：活动内容：Treasure大厅
- RequestClass：`EventContentTreasureLobbyRequest`
- ResponseClass：`EventContentTreasureLobbyResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BoardHistoryDB` | `EventContentTreasureHistoryDB?` | Board历史数据。 |
| `HiddenImage` | `EventContentTreasureCell?` | 隐藏图片格子。 |
| `VariationId` | `long` | Variation ID。 |

### EventContent_TreasureNextRound

- 协议号：`30046`
- 作用：活动内容：执行 TreasureNextRound 流程
- RequestClass：`EventContentTreasureNextRoundRequest`
- ResponseClass：`EventContentTreasureNextRoundResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `Round` | `int` | 轮次。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BoardHistoryDB` | `EventContentTreasureHistoryDB?` | Board历史数据。 |
| `HiddenImage` | `EventContentTreasureCell?` | 隐藏图片格子。 |

### EventContent_ClueSearchGetInfo

- 协议号：`30051`
- 作用：活动内容：Clue搜索获取信息
- RequestClass：`EventContentClueSearchGetInfoRequest`
- ResponseClass：`EventContentClueSearchGetInfoResponse`
- 状态：SDK 已封装为活动页面状态读取方法；返回的是可直接用于页面展示的整理后数据，不输出原始响应包。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | 当前 ClueSearch 活动内容 ID。必须是当前账号可见的活动。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `clue_search` | `EventContentClueSearchDB?` | ClueSearch 页面主状态。 |
| `round` | `EventContentClueSearchRoundDB?` | 当前轮次/回合状态。 |
| `progress` | `EventContentClueSearchProgressDB?` | 搜索进度与完成状态。 |
| `collections` | `List<EventContentCollectionDB>?` | 线索相关集合/条目列表。 |
| `already_receive_reward_ids` | `List<long>?` | 已领取奖励 ID 列表。 |
| `event_content_id` | `long?` | 回传的活动内容 ID。 |
| `collection_count` | `int` | `collections` 数量。 |

#### 返回示例

```python
{
    "clue_search": {...},
    "round": {...},
    "progress": {...},
    "collections": [{...}],
    "already_receive_reward_ids": [1, 2],
    "event_content_id": 30051,
    "collection_count": 1,
    "extra": {},
}
```

```python
clue = await client.event_content.clue_search_get_info(event_content_id)
print(clue["collection_count"], clue["already_receive_reward_ids"])
```

### EventContent_ClueSearchSubmit

- 协议号：`30052`
- 作用：活动内容：Clue搜索提交
- RequestClass：`EventContentClueSearchSubmitRequest`
- ResponseClass：`EventContentClueSearchSubmitResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### EventContent_ClueSearchRoundComplete

- 协议号：`30053`
- 作用：活动内容：Clue搜索RoundComplete
- RequestClass：`EventContentClueSearchRoundCompleteRequest`
- ResponseClass：`EventContentClueSearchRoundCompleteResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
