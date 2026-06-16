# Campaign 协议

普通关卡模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Campaign_List` | `6000` | 主线关卡：获取列表数据 | `CampaignListRequest` | `CampaignListResponse` |
| `Campaign_EnterMainStage` | `6001` | 主线关卡：进入Main关卡 | `CampaignEnterMainStageRequest` | `CampaignEnterMainStageResponse` |
| `Campaign_ConfirmMainStage` | `6002` | 主线关卡：ConfirmMain关卡 | `CampaignConfirmMainStageRequest` | `CampaignConfirmMainStageResponse` |
| `Campaign_DeployEchelon` | `6003` | 主线关卡：布置Echelon | `CampaignDeployEchelonRequest` | `CampaignDeployEchelonResponse` |
| `Campaign_WithdrawEchelon` | `6004` | 主线关卡：执行 WithdrawEchelon 流程 | `CampaignWithdrawEchelonRequest` | `CampaignWithdrawEchelonResponse` |
| `Campaign_MapMove` | `6005` | 主线关卡：执行 MapMove 流程 | `CampaignMapMoveRequest` | `CampaignMapMoveResponse` |
| `Campaign_EndTurn` | `6006` | 主线关卡：执行 EndTurn 流程 | `CampaignEndTurnRequest` | `CampaignEndTurnResponse` |
| `Campaign_ChapterClearReward` | `6010` | 主线关卡：Chapter清空奖励 | `CampaignChapterClearRewardRequest` | `CampaignChapterClearRewardResponse` |
| `Campaign_Heal` | `6011` | 主线关卡：执行 Heal 流程 | `CampaignHealRequest` | `CampaignHealResponse` |
| `Campaign_EnterSubStage` | `6012` | 主线关卡：进入Sub关卡 | `CampaignEnterSubStageRequest` | `CampaignEnterSubStageResponse` |
| `Campaign_Portal` | `6014` | 主线关卡：执行 Portal 流程 | `CampaignPortalRequest` | `CampaignPortalResponse` |
| `Campaign_ConfirmTutorialStage` | `6015` | 主线关卡：ConfirmTutorial关卡 | `CampaignConfirmTutorialStageRequest` | `CampaignConfirmTutorialStageResponse` |
| `Campaign_PurchasePlayCountHardStage` | `6016` | 主线关卡：PurchasePlayCountHard关卡 | `CampaignPurchasePlayCountHardStageRequest` | `CampaignPurchasePlayCountHardStageResponse` |
| `Campaign_EnterTutorialStage` | `6017` | 主线关卡：进入Tutorial关卡 | `CampaignEnterTutorialStageRequest` | `CampaignEnterTutorialStageResponse` |
| `Campaign_RestartMainStage` | `6019` | 主线关卡：RestartMain关卡 | `CampaignRestartMainStageRequest` | `CampaignRestartMainStageResponse` |
| `Campaign_EnterMainStageStrategySkip` | `6020` | 主线关卡：进入Main关卡StrategySkip | `CampaignEnterMainStageStrategySkipRequest` | `CampaignEnterMainStageStrategySkipResponse` |

## 字段结构参考

### Campaign_List

- 协议号：`6000`
- 作用：主线关卡：获取列表数据
- RequestClass：`CampaignListRequest`
- ResponseClass：`CampaignListResponse`
- 状态：已封装为 `client.campaign.list()`，live 验证通过。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CampaignChapterClearRewardHistoryDBs` | `List<CampaignChapterClearRewardHistoryDB>?` | CampaignChapterClearRewardHistory 数据列表。 |
| `StageHistoryDBs` | `List<CampaignStageHistoryDB>?` | StageHistory 数据列表。 |
| `StrategyObjecthistoryDBs` | `List<StrategyObjectHistoryDB>?` | StrategyObjecthistory 数据列表。 |

### Campaign_EnterMainStage

- 协议号：`6001`
- 作用：主线关卡：进入Main关卡
- RequestClass：`CampaignEnterMainStageRequest`
- ResponseClass：`CampaignEnterMainStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `CampaignMainStageSaveDB?` | SaveData数据。 |

### Campaign_ConfirmMainStage

- 协议号：`6002`
- 作用：主线关卡：ConfirmMain关卡
- RequestClass：`CampaignConfirmMainStageRequest`
- ResponseClass：`CampaignConfirmMainStageResponse`
- 状态：SDK 已封装为主线关卡结果确认方法 `client.campaign.confirm_main_stage(stage_unique_id, confirm=True)`；默认 `validate=True` 会本地拦截。live 验证表明 `Campaign_List` 历史关卡 ID 会返回 `ErrorCode=6003 CampaignStageInvalidSaveData`，只有调用方先从活跃主线关卡 SaveData 流程获得目标 `StageUniqueId` 后，才应传 `validate=False` 发送。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `SaveDataDB` | `CampaignMainStageSaveDB?` | SaveData数据。 |
| `StageInfo` | `CampaignStageInfo?` | 关卡信息。 |

### Campaign_DeployEchelon

- 协议号：`6003`
- 作用：主线关卡：布置Echelon
- RequestClass：`CampaignDeployEchelonRequest`
- ResponseClass：`CampaignDeployEchelonResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `DeployedEchelons` | `List<HexaUnit>?` | DeployedEchelons数据列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `CampaignMainStageSaveDB?` | SaveData数据。 |

### Campaign_WithdrawEchelon

- 协议号：`6004`
- 作用：主线关卡：执行 WithdrawEchelon 流程
- RequestClass：`CampaignWithdrawEchelonRequest`
- ResponseClass：`CampaignWithdrawEchelonResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `WithdrawEchelonEntityId` | `List<long>?` | Withdraw编队Entity ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `CampaignMainStageSaveDB?` | SaveData数据。 |
| `WithdrawEchelonDBs` | `List<EchelonDB>?` | WithdrawEchelon 数据列表。 |

### Campaign_MapMove

- 协议号：`6005`
- 作用：主线关卡：执行 MapMove 流程
- RequestClass：`CampaignMapMoveRequest`
- ResponseClass：`CampaignMapMoveResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `EchelonEntityId` | `long` | 编队Entity ID。 |
| `DestPosition` | `HexLocation` | 目标位置。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `CampaignMainStageSaveDB?` | SaveData数据。 |
| `EchelonEntityId` | `long` | 编队Entity ID。 |
| `StrategyObject` | `Strategy?` | 策略地图对象。 |
| `StrategyObjectParcelInfos` | `List<ParcelInfo>?` | StrategyObject奖励包Infos数据列表。 |

### Campaign_EndTurn

- 协议号：`6006`
- 作用：主线关卡：执行 EndTurn 流程
- RequestClass：`CampaignEndTurnRequest`
- ResponseClass：`CampaignEndTurnResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `CampaignMainStageSaveDB?` | SaveData数据。 |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |

### Campaign_ChapterClearReward

- 协议号：`6010`
- 作用：主线关卡：Chapter清空奖励
- RequestClass：`CampaignChapterClearRewardRequest`
- ResponseClass：`CampaignChapterClearRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CampaignChapterUniqueId` | `long` | 战役Chapter唯一 ID。 |
| `StageDifficulty` | `StageDifficulty` | 关卡难度。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CampaignChapterClearRewardHistoryDB` | `CampaignChapterClearRewardHistoryDB?` | 战役ChapterClear奖励历史数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Campaign_Heal

- 协议号：`6011`
- 作用：主线关卡：执行 Heal 流程
- RequestClass：`CampaignHealRequest`
- ResponseClass：`CampaignHealResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CampaignStageUniqueId` | `long` | 战役关卡唯一 ID。 |
| `EchelonIndex` | `long` | 编队索引索引。 |
| `CharacterServerId` | `long` | 角色服务器 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `SaveDataDB` | `CampaignMainStageSaveDB?` | SaveData数据。 |

### Campaign_EnterSubStage

- 协议号：`6012`
- 作用：主线关卡：进入Sub关卡
- RequestClass：`CampaignEnterSubStageRequest`
- ResponseClass：`CampaignEnterSubStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `LastEnterStageEchelonNumber` | `long` | 上次进入关卡的编队编号。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `SaveDataDB` | `CampaignSubStageSaveDB?` | SaveData数据。 |

### Campaign_Portal

- 协议号：`6014`
- 作用：主线关卡：执行 Portal 流程
- RequestClass：`CampaignPortalRequest`
- ResponseClass：`CampaignPortalResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `EchelonEntityId` | `long` | 编队Entity ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CampaignMainStageSaveDB` | `CampaignMainStageSaveDB?` | 战役Main关卡Save数据。 |

### Campaign_ConfirmTutorialStage

- 协议号：`6015`
- 作用：主线关卡：ConfirmTutorial关卡
- RequestClass：`CampaignConfirmTutorialStageRequest`
- ResponseClass：`CampaignConfirmTutorialStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `CampaignMainStageSaveDB?` | SaveData数据。 |

### Campaign_PurchasePlayCountHardStage

- 协议号：`6016`
- 作用：主线关卡：PurchasePlayCountHard关卡
- RequestClass：`CampaignPurchasePlayCountHardStageRequest`
- ResponseClass：`CampaignPurchasePlayCountHardStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `CampaignStageHistoryDB` | `CampaignStageHistoryDB?` | 战役关卡历史数据。 |

### Campaign_EnterTutorialStage

- 协议号：`6017`
- 作用：主线关卡：进入Tutorial关卡
- RequestClass：`CampaignEnterTutorialStageRequest`
- ResponseClass：`CampaignEnterTutorialStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `SaveDataDB` | `CampaignTutorialStageSaveDB?` | SaveData数据。 |

### Campaign_RestartMainStage

- 协议号：`6019`
- 作用：主线关卡：RestartMain关卡
- RequestClass：`CampaignRestartMainStageRequest`
- ResponseClass：`CampaignRestartMainStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `SaveDataDB` | `CampaignMainStageSaveDB?` | SaveData数据。 |

### Campaign_EnterMainStageStrategySkip

- 协议号：`6020`
- 作用：主线关卡：进入Main关卡StrategySkip
- RequestClass：`CampaignEnterMainStageStrategySkipRequest`
- ResponseClass：`CampaignEnterMainStageStrategySkipResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `LastEnterStageEchelonNumber` | `long` | 上次进入关卡的编队编号。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
