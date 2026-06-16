# MiniGame 协议

MiniGame 是限时活动附带的小玩法协议集合，不是固定常驻入口。SDK 文档只保留状态查询、任务列表、扫荡和基础状态类协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 接入原则

- 先从活动状态中读取 `EventContentId`、关卡、任务进度和可扫荡状态。
- `Sweep` 相关协议可以保留为自动化入口，但仍需要校验次数、票券和开放条件。
- 会直接影响公平性的小游戏协议不在 SDK 文档中提供字段结构。
- 已删除小游戏战斗进入、小游戏战斗结算、小游戏成绩提交、小游戏翻牌开奖、奖励卡选择、奖励重掷、购买 Perk、完成游戏等会影响游戏公平性的部分。
- SDK 侧后续按玩法拆模块，避免做一个脱离游戏页面语义的万能低层请求入口。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `MiniGame_StageList` | `35000` | 小游戏：关卡列表 | `MiniGameStageListRequest` | `MiniGameStageListResponse` |
| `MiniGame_EnterStage` | `35001` | 小游戏：进入关卡 | `MiniGameEnterStageRequest` | `MiniGameEnterStageResponse` |
| `MiniGame_MissionList` | `35003` | 小游戏：任务列表 | `MiniGameMissionListRequest` | `MiniGameMissionListResponse` |
| `MiniGame_MissionReward` | `35004` | 小游戏：任务奖励 | `MiniGameMissionRewardRequest` | `MiniGameMissionRewardResponse` |
| `MiniGame_MissionMultipleReward` | `35005` | 小游戏：任务Multiple奖励 | `MiniGameMissionMultipleRewardRequest` | `MiniGameMissionMultipleRewardResponse` |
| `MiniGame_ShootingLobby` | `35006` | 小游戏：Shooting大厅 | `MiniGameShootingLobbyRequest` | `MiniGameShootingLobbyResponse` |
| `MiniGame_ShootingSweep` | `35009` | 小游戏：执行 ShootingSweep 流程 | `MiniGameShootingSweepRequest` | `MiniGameShootingSweepResponse` |
| `MiniGame_TableBoardSync` | `35010` | 小游戏：TableBoard同步 | `MiniGameTableBoardSyncRequest` | `MiniGameTableBoardSyncResponse` |
| `MiniGame_TableBoardMove` | `35011` | 小游戏：执行 TableBoardMove 流程 | `MiniGameTableBoardMoveRequest` | `MiniGameTableBoardMoveResponse` |
| `MiniGame_TableBoardEncounterInput` | `35012` | 小游戏：执行 TableBoardEncounterInput 流程 | `MiniGameTableBoardEncounterInputRequest` | `MiniGameTableBoardEncounterInputResponse` |
| `MiniGame_TableBoardClearThema` | `35015` | 小游戏：TableBoard清空Thema | `MiniGameTableBoardClearThemaRequest` | `MiniGameTableBoardClearThemaResponse` |
| `MiniGame_TableBoardUseItem` | `35016` | 小游戏：TableBoard使用Item | `MiniGameTableBoardUseItemRequest` | `MiniGameTableBoardUseItemResponse` |
| `MiniGame_TableBoardResurrect` | `35017` | 小游戏：执行 TableBoardResurrect 流程 | `MiniGameTableBoardResurrectRequest` | `MiniGameTableBoardResurrectResponse` |
| `MiniGame_TableBoardSweep` | `35018` | 小游戏：执行 TableBoardSweep 流程 | `MiniGameTableBoardSweepRequest` | `MiniGameTableBoardSweepResponse` |
| `MiniGame_TableBoardMoveThema` | `35019` | 小游戏：执行 TableBoardMoveThema 流程 | `MiniGameTableBoardMoveThemaRequest` | `MiniGameTableBoardMoveThemaResponse` |
| `MiniGame_DreamMakerGetInfo` | `35020` | 小游戏：DreamMaker获取信息 | `MiniGameDreamMakerGetInfoRequest` | `MiniGameDreamMakerGetInfoResponse` |
| `MiniGame_DreamMakerNewGame` | `35021` | 小游戏：DreamMakerNew游戏 | `MiniGameDreamMakerNewGameRequest` | `MiniGameDreamMakerNewGameResponse` |
| `MiniGame_DreamMakerRestart` | `35022` | 小游戏：执行 DreamMakerRestart 流程 | `MiniGameDreamMakerResetRequest` | `MiniGameDreamMakerResetResponse` |
| `MiniGame_DreamMakerAttendSchedule` | `35023` | 小游戏：执行 DreamMakerAttendSchedule 流程 | `MiniGameDreamMakerAttendScheduleRequest` | `MiniGameDreamMakerAttendScheduleResponse` |
| `MiniGame_DreamMakerDailyClosing` | `35024` | 小游戏：执行 DreamMakerDailyClosing 流程 | `MiniGameDreamMakerDailyClosingRequest` | `MiniGameDreamMakerDailyClosingResponse` |
| `MiniGame_DreamMakerEnding` | `35025` | 小游戏：执行 DreamMakerEnding 流程 | `MiniGameDreamMakerEndingRequest` | `MiniGameDreamMakerEndingResponse` |
| `MiniGame_DefenseGetInfo` | `35026` | 小游戏：Defense获取信息 | `MiniGameDefenseGetInfoRequest` | `MiniGameDefenseGetInfoResponse` |
| `MiniGame_RoadPuzzleGetInfo` | `35029` | 小游戏：RoadPuzzle获取信息 | `MiniGameRoadPuzzleGetInfoRequest` | `MiniGameRoadPuzzleGetInfoResponse` |
| `MiniGame_RoadPuzzleTilePlace` | `35030` | 小游戏：执行 RoadPuzzleTilePlace 流程 | `MiniGameRoadPuzzleTilePlaceRequest` | `MiniGameRoadPuzzleTilePlaceResponse` |
| `MiniGame_RoadPuzzleSaveStage` | `35031` | 小游戏：RoadPuzzle保存关卡 | `MiniGameRoadPuzzleSaveStageRequest` | `MiniGameRoadPuzzleSaveStageResponse` |
| `MiniGame_RoadPuzzleClearStage` | `35032` | 小游戏：RoadPuzzle清空关卡 | `MiniGameRoadPuzzleClearStageRequest` | `MiniGameRoadPuzzleClearStageResponse` |
| `MiniGame_CCGLobby` | `35033` | 小游戏：CCG大厅 | `MiniGameCCGLobbyRequest` | `MiniGameCCGLobbyResponse` |
| `MiniGame_CCGCreateGame` | `35034` | 小游戏：CCG创建游戏 | `MiniGameCCGCreateGameRequest` | `MiniGameCCGCreateGameResponse` |
| `MiniGame_CCGSweep` | `35035` | 小游戏：执行 CCGSweep 流程 | `MiniGameCCGSweepRequest` | `MiniGameCCGSweepResponse` |
| `MiniGame_CCGEnterStage` | `35036` | 小游戏：CCG进入关卡 | `MiniGameCCGEnterStageRequest` | `MiniGameCCGEnterStageResponse` |
| `MiniGame_CCGSelectCampAction` | `35041` | 小游戏：执行 CCGSelectCampAction 流程 | `MiniGameCCGSelectCampActionRequest` | `MiniGameCCGSelectCampActionResponse` |
| `MiniGame_CCGGiveupGame` | `35043` | 小游戏：CCGGiveup游戏 | `MiniGameCCGGiveupGameRequest` | `MiniGameCCGGiveupGameResponse` |

## 字段结构参考

### MiniGame_StageList

- 协议号：`35000`
- 作用：小游戏：关卡列表
- RequestClass：`MiniGameStageListRequest`
- ResponseClass：`MiniGameStageListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MiniGameHistoryDBs` | `List<MiniGameHistoryDB>?` | MiniGameHistory 数据列表。 |

### MiniGame_EnterStage

- 协议号：`35001`
- 作用：小游戏：进入关卡
- RequestClass：`MiniGameEnterStageRequest`
- ResponseClass：`MiniGameEnterStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `UniqueId` | `long` | 唯一 ID。 |

#### Response 字段

无字段或未匹配到结构。

### MiniGame_MissionList

- 协议号：`35003`
- 作用：小游戏：任务列表
- RequestClass：`MiniGameMissionListRequest`
- ResponseClass：`MiniGameMissionListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MissionHistoryUniqueIds` | `List<long>?` | ID 列表。 |
| `ProgressDBs` | `List<MissionProgressDB>?` | Progress 数据列表。 |
| `ClearedOrignalMissionIds` | `List<long>?` | ID 列表。 |

### MiniGame_MissionReward

- 协议号：`35004`
- 作用：小游戏：任务奖励
- RequestClass：`MiniGameMissionRewardRequest`
- ResponseClass：`MiniGameMissionRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MissionUniqueId` | `long` | 任务唯一 ID。 |
| `ProgressServerId` | `long` | Progress服务器 ID。 |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AddedHistoryDB` | `MissionHistoryDB?` | Added历史数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### MiniGame_MissionMultipleReward

- 协议号：`35005`
- 作用：小游戏：任务Multiple奖励
- RequestClass：`MiniGameMissionMultipleRewardRequest`
- ResponseClass：`MiniGameMissionMultipleRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MissionCategory` | `MissionCategory` | 任务分类。 |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AddedHistoryDBs` | `List<MissionHistoryDB>?` | AddedHistory 数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### MiniGame_ShootingLobby

- 协议号：`35006`
- 作用：小游戏：Shooting大厅
- RequestClass：`MiniGameShootingLobbyRequest`
- ResponseClass：`MiniGameShootingLobbyResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `HistoryDBs` | `List<MiniGameShootingHistoryDB>?` | History 数据列表。 |

### MiniGame_ShootingSweep

- 协议号：`35009`
- 作用：小游戏：执行 ShootingSweep 流程
- RequestClass：`MiniGameShootingSweepRequest`
- ResponseClass：`MiniGameShootingSweepResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `UniqueId` | `long` | 唯一 ID。 |
| `SweepCount` | `long` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Rewards` | `List<List<ParcelInfo>>?` | 奖励数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### MiniGame_TableBoardSync

- 协议号：`35010`
- 作用：小游戏：TableBoard同步
- RequestClass：`MiniGameTableBoardSyncRequest`
- ResponseClass：`MiniGameTableBoardSyncResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDB` | `TBGBoardSaveDB` | Save数据。 |

### MiniGame_TableBoardMove

- 协议号：`35011`
- 作用：小游戏：执行 TableBoardMove 流程
- RequestClass：`MiniGameTableBoardMoveRequest`
- ResponseClass：`MiniGameTableBoardMoveResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `Steps` | `List<HexLocation>?` | Steps数据列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PlayerDB` | `TBGPlayerDB?` | 玩家数据。 |
| `SaveDB` | `TBGBoardSaveDB` | Save数据。 |
| `EncounterDB` | `TBGEncounterDB` | Encounter数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### MiniGame_TableBoardEncounterInput

- 协议号：`35012`
- 作用：小游戏：执行 TableBoardEncounterInput 流程
- RequestClass：`MiniGameTableBoardEncounterInputRequest`
- ResponseClass：`MiniGameTableBoardEncounterInputResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `ObjectServerId` | `long` | Object服务器 ID。 |
| `EncounterStage` | `int` | 遭遇关卡。 |
| `SelectedIndex` | `int` | Selected索引索引。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDB` | `TBGBoardSaveDB` | Save数据。 |
| `EncounterDB` | `TBGEncounterDB` | Encounter数据。 |
| `PlayerDiceResult` | `List<int>?` | 玩家Dice结果数据列表。 |
| `PlayerAddDotEffectResult` | `Nullable<int>` | 玩家 DOT 效果追加结果。 |
| `PlayerDicePlayResult` | `Nullable<TBGDiceRollResult>` | 玩家骰子行动结果。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `EventContentCollectionDBs` | `List<EventContentCollectionDB>?` | EventContentCollection 数据列表。 |

### MiniGame_TableBoardClearThema

- 协议号：`35015`
- 作用：小游戏：TableBoard清空Thema
- RequestClass：`MiniGameTableBoardClearThemaRequest`
- ResponseClass：`MiniGameTableBoardClearThemaResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `PreserveItemEffectUniqueIds` | `List<long>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDB` | `TBGBoardSaveDB` | Save数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### MiniGame_TableBoardUseItem

- 协议号：`35016`
- 作用：小游戏：TableBoard使用Item
- RequestClass：`MiniGameTableBoardUseItemRequest`
- ResponseClass：`MiniGameTableBoardUseItemResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `ItemSlotIndex` | `int` | 道具槽位索引索引。 |
| `UsedItemId` | `long` | Used道具 ID。 |
| `IsDiscard` | `bool` | 布尔状态。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PlayerDB` | `TBGPlayerDB?` | 玩家数据。 |

### MiniGame_TableBoardResurrect

- 协议号：`35017`
- 作用：小游戏：执行 TableBoardResurrect 流程
- RequestClass：`MiniGameTableBoardResurrectRequest`
- ResponseClass：`MiniGameTableBoardResurrectResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PlayerDB` | `TBGPlayerDB?` | 玩家数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### MiniGame_TableBoardSweep

- 协议号：`35018`
- 作用：小游戏：执行 TableBoardSweep 流程
- RequestClass：`MiniGameTableBoardSweepRequest`
- ResponseClass：`MiniGameTableBoardSweepResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `PreserveItemEffectUniqueIds` | `List<long>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDB` | `TBGBoardSaveDB` | Save数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### MiniGame_TableBoardMoveThema

- 协议号：`35019`
- 作用：小游戏：执行 TableBoardMoveThema 流程
- RequestClass：`MiniGameTableBoardMoveThemaRequest`
- ResponseClass：`MiniGameTableBoardMoveThemaResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDB` | `TBGBoardSaveDB` | Save数据。 |

### MiniGame_DreamMakerGetInfo

- 协议号：`35020`
- 作用：小游戏：DreamMaker获取信息
- RequestClass：`MiniGameDreamMakerGetInfoRequest`
- ResponseClass：`MiniGameDreamMakerGetInfoResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `InfoDB` | `MiniGameDreamMakerInfoDB?` | 信息数据。 |
| `ParameterDBs` | `List<MiniGameDreamMakerParameterDB>?` | Parameter 数据列表。 |
| `EndingDBs` | `List<MiniGameDreamMakerEndingDB>?` | Ending 数据列表。 |
| `EventContentCollectionDBs` | `List<EventContentCollectionDB>?` | EventContentCollection 数据列表。 |
| `EventPointAmount` | `long` | EventPoint数量数量。 |
| `AlreadyReceivePointRewardIds` | `List<long>?` | ID 列表。 |

### MiniGame_DreamMakerNewGame

- 协议号：`35021`
- 作用：小游戏：DreamMakerNew游戏
- RequestClass：`MiniGameDreamMakerNewGameRequest`
- ResponseClass：`MiniGameDreamMakerNewGameResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `Multiplier` | `long` | 倍率。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `InfoDB` | `MiniGameDreamMakerInfoDB?` | 信息数据。 |
| `ParameterDBs` | `List<MiniGameDreamMakerParameterDB>?` | Parameter 数据列表。 |

### MiniGame_DreamMakerRestart

- 协议号：`35022`
- 作用：小游戏：执行 DreamMakerRestart 流程
- RequestClass：`MiniGameDreamMakerResetRequest`
- ResponseClass：`MiniGameDreamMakerResetResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `InfoDB` | `MiniGameDreamMakerInfoDB?` | 信息数据。 |
| `ParameterDBs` | `List<MiniGameDreamMakerParameterDB>?` | Parameter 数据列表。 |

### MiniGame_DreamMakerAttendSchedule

- 协议号：`35023`
- 作用：小游戏：执行 DreamMakerAttendSchedule 流程
- RequestClass：`MiniGameDreamMakerAttendScheduleRequest`
- ResponseClass：`MiniGameDreamMakerAttendScheduleResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `ScheduleGroupId` | `long` | ScheduleGroup ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `InfoDB` | `MiniGameDreamMakerInfoDB?` | 信息数据。 |
| `ParameterDBs` | `List<MiniGameDreamMakerParameterDB>?` | Parameter 数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ScheduleResultId` | `long` | Schedule结果 ID。 |
| `EventContentCollectionDBs` | `List<EventContentCollectionDB>?` | EventContentCollection 数据列表。 |

### MiniGame_DreamMakerDailyClosing

- 协议号：`35024`
- 作用：小游戏：执行 DreamMakerDailyClosing 流程
- RequestClass：`MiniGameDreamMakerDailyClosingRequest`
- ResponseClass：`MiniGameDreamMakerDailyClosingResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `InfoDB` | `MiniGameDreamMakerInfoDB?` | 信息数据。 |
| `ParameterDBs` | `List<MiniGameDreamMakerParameterDB>?` | Parameter 数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `EventPointAmount` | `long` | EventPoint数量数量。 |
| `AlreadyReceivePointRewardIds` | `List<long>?` | ID 列表。 |

### MiniGame_DreamMakerEnding

- 协议号：`35025`
- 作用：小游戏：执行 DreamMakerEnding 流程
- RequestClass：`MiniGameDreamMakerEndingRequest`
- ResponseClass：`MiniGameDreamMakerEndingResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `InfoDB` | `MiniGameDreamMakerInfoDB?` | 信息数据。 |
| `ParameterDBs` | `List<MiniGameDreamMakerParameterDB>?` | Parameter 数据列表。 |
| `EndingDB` | `MiniGameDreamMakerEndingDB?` | Ending数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### MiniGame_DefenseGetInfo

- 协议号：`35026`
- 作用：小游戏：Defense获取信息
- RequestClass：`MiniGameDefenseGetInfoRequest`
- ResponseClass：`MiniGameDefenseGetInfoResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventPointAmount` | `long` | EventPoint数量数量。 |
| `DefenseStageHistoryDBs` | `List<MiniGameDefenseStageHistoryDB>?` | DefenseStageHistory 数据列表。 |

### MiniGame_RoadPuzzleGetInfo

- 协议号：`35029`
- 作用：小游戏：RoadPuzzle获取信息
- RequestClass：`MiniGameRoadPuzzleGetInfoRequest`
- ResponseClass：`MiniGameRoadPuzzleGetInfoResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDB` | `RoadPuzzleBoardSaveDB` | Save数据。 |

### MiniGame_RoadPuzzleTilePlace

- 协议号：`35030`
- 作用：小游戏：执行 RoadPuzzleTilePlace 流程
- RequestClass：`MiniGameRoadPuzzleTilePlaceRequest`
- ResponseClass：`MiniGameRoadPuzzleTilePlaceResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `UniqueId` | `long` | 唯一 ID。 |
| `Round` | `long` | 轮次。 |
| `RailTileToPlace` | `RoadPuzzleRailTileData` | 要放置的轨道格。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RailTileToPlace` | `RoadPuzzleRailTileData` | 要放置的轨道格。 |
| `SaveDB` | `RoadPuzzleBoardSaveDB` | Save数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### MiniGame_RoadPuzzleSaveStage

- 协议号：`35031`
- 作用：小游戏：RoadPuzzle保存关卡
- RequestClass：`MiniGameRoadPuzzleSaveStageRequest`
- ResponseClass：`MiniGameRoadPuzzleSaveStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `UniqueId` | `long` | 唯一 ID。 |
| `Round` | `long` | 轮次。 |
| `placeRailTiles` | `List<RoadPuzzleRailTileData>` | placeRailTiles数据列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDB` | `RoadPuzzleBoardSaveDB` | Save数据。 |

### MiniGame_RoadPuzzleClearStage

- 协议号：`35032`
- 作用：小游戏：RoadPuzzle清空关卡
- RequestClass：`MiniGameRoadPuzzleClearStageRequest`
- ResponseClass：`MiniGameRoadPuzzleClearStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `UniqueId` | `long` | 唯一 ID。 |
| `Round` | `long` | 轮次。 |
| `IsSkip` | `bool` | 布尔状态。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `IsSkip` | `bool` | 布尔状态。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### MiniGame_CCGLobby

- 协议号：`35033`
- 作用：小游戏：CCG大厅
- RequestClass：`MiniGameCCGLobbyRequest`
- ResponseClass：`MiniGameCCGLobbyResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CCGSaveDB` | `MiniGameCCGSaveDB?` | CCGSave数据。 |
| `Perks` | `List<long>?` | Perks数据列表。 |
| `RewardPoint` | `int` | 奖励Point奖励信息。 |
| `CanSweep` | `bool` | 是否可以Sweep。 |

### MiniGame_CCGCreateGame

- 协议号：`35034`
- 作用：小游戏：CCG创建游戏
- RequestClass：`MiniGameCCGCreateGameRequest`
- ResponseClass：`MiniGameCCGCreateGameResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `ForceDiscardSave` | `bool` | 是否强制丢弃存档。 |
| `DisablePerk` | `bool` | 是否禁用增益。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CCGSaveDB` | `MiniGameCCGSaveDB?` | CCGSave数据。 |

### MiniGame_CCGSweep

- 协议号：`35035`
- 作用：小游戏：执行 CCGSweep 流程
- RequestClass：`MiniGameCCGSweepRequest`
- ResponseClass：`MiniGameCCGSweepResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `SweepCount` | `int` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Rewards` | `List<List<ParcelInfo>>?` | 奖励数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### MiniGame_CCGEnterStage

- 协议号：`35036`
- 作用：小游戏：CCG进入关卡
- RequestClass：`MiniGameCCGEnterStageRequest`
- ResponseClass：`MiniGameCCGEnterStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `NodeId` | `long` | Node ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageDB` | `MiniGameCCGStagePlayDB?` | 关卡数据。 |

### MiniGame_CCGSelectCampAction

- 协议号：`35041`
- 作用：小游戏：执行 CCGSelectCampAction 流程
- RequestClass：`MiniGameCCGSelectCampActionRequest`
- ResponseClass：`MiniGameCCGSelectCampActionResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `SelectedOption` | `MiniGameCCGCampOption` | Selected选项选项。 |
| `RemoveCardDBIds` | `List<int>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageDB` | `MiniGameCCGStagePlayDB?` | 关卡数据。 |
| `SaveDB` | `MiniGameCCGSaveDB?` | Save数据。 |

### MiniGame_CCGGiveupGame

- 协议号：`35043`
- 作用：小游戏：CCGGiveup游戏
- RequestClass：`MiniGameCCGGiveupGameRequest`
- ResponseClass：`MiniGameCCGGiveupGameResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDB` | `MiniGameCCGSaveDB?` | Save数据。 |
