# Scenario 协议

剧情模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Scenario_List` | `19000` | 剧情：获取列表数据 | `ScenarioListRequest` | `ScenarioListResponse` |
| `Scenario_GroupHistoryUpdate` | `19002` | 剧情：Group历史记录更新 | `ScenarioGroupHistoryUpdateRequest` | `ScenarioGroupHistoryUpdateResponse` |
| `Scenario_Skip` | `19003` | 剧情：执行 Skip 流程 | `ScenarioSkipRequest` | `ScenarioSkipResponse` |
| `Scenario_Select` | `19004` | 剧情：执行 Select 流程 | `ScenarioSelectRequest` | `ScenarioSelectResponse` |
| `Scenario_AccountStudentChange` | `19005` | 剧情：执行 AccountStudentChange 流程 | `ScenarioAccountStudentChangeRequest` | `ScenarioAccountStudentChangeResponse` |
| `Scenario_LobbyStudentChange` | `19006` | 剧情：大厅StudentChange | `ScenarioLobbyStudentChangeRequest` | `ScenarioLobbyStudentChangeResponse` |
| `Scenario_SpecialLobbyChange` | `19007` | 剧情：Special大厅Change | `ScenarioSpecialLobbyChangeRequest` | `ScenarioSpecialLobbyChangeResponse` |
| `Scenario_Enter` | `19008` | 剧情：进入对应功能入口 | `ScenarioEnterRequest` | `ScenarioEnterResponse` |
| `Scenario_EnterMainStage` | `19009` | 剧情：进入Main关卡 | `ScenarioEnterMainStageRequest` | `ScenarioEnterMainStageResponse` |
| `Scenario_ConfirmMainStage` | `19010` | 剧情：ConfirmMain关卡 | `ScenarioConfirmMainStageRequest` | `ScenarioConfirmMainStageResponse` |
| `Scenario_DeployEchelon` | `19011` | 剧情：布置Echelon | `ScenarioDeployEchelonRequest` | `ScenarioDeployEchelonResponse` |
| `Scenario_WithdrawEchelon` | `19012` | 剧情：执行 WithdrawEchelon 流程 | `ScenarioWithdrawEchelonRequest` | `ScenarioWithdrawEchelonResponse` |
| `Scenario_MapMove` | `19013` | 剧情：执行 MapMove 流程 | `ScenarioMapMoveRequest` | `ScenarioMapMoveResponse` |
| `Scenario_EndTurn` | `19014` | 剧情：执行 EndTurn 流程 | `ScenarioEndTurnRequest` | `ScenarioEndTurnResponse` |
| `Scenario_Portal` | `19018` | 剧情：执行 Portal 流程 | `ScenarioPortalRequest` | `ScenarioPortalResponse` |
| `Scenario_RestartMainStage` | `19019` | 剧情：RestartMain关卡 | `ScenarioRestartMainStageRequest` | `ScenarioRestartMainStageResponse` |
| `Scenario_SkipMainStage` | `19020` | 剧情：SkipMain关卡 | `ScenarioSkipMainStageRequest` | `ScenarioSkipMainStageResponse` |

## 字段结构参考

### Scenario_List

- 协议号：`19000`
- 作用：剧情：获取列表数据
- RequestClass：`ScenarioListRequest`
- ResponseClass：`ScenarioListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ScenarioHistoryDBs` | `List<ScenarioHistoryDB>?` | ScenarioHistory 数据列表。 |
| `ScenarioGroupHistoryDBs` | `List<ScenarioGroupHistoryDB>?` | ScenarioGroupHistory 数据列表。 |
| `ScenarioCollectionDBs` | `List<ScenarioCollectionDB>?` | ScenarioCollection 数据列表。 |

### Scenario_GroupHistoryUpdate

- 协议号：`19002`
- 作用：剧情：Group历史记录更新
- RequestClass：`ScenarioGroupHistoryUpdateRequest`
- ResponseClass：`ScenarioGroupHistoryUpdateResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ScenarioGroupUniqueId` | `long` | 剧情Group唯一 ID。 |
| `ScenarioType` | `long` | 剧情类型。 |
| `ScenarioGroupHistoryDB` | `ScenarioGroupHistoryDB?` | 剧情Group历史数据。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ScenarioGroupHistoryDB` | `ScenarioGroupHistoryDB?` | 剧情Group历史数据。 |

### Scenario_Skip

- 协议号：`19003`
- 作用：剧情：执行 Skip 流程
- RequestClass：`ScenarioSkipRequest`
- ResponseClass：`ScenarioSkipResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ScriptGroupId` | `long` | ScriptGroup ID。 |
| `SkipPointScriptCount` | `int` | 数量。 |

#### Response 字段

无字段或未匹配到结构。

### Scenario_Select

- 协议号：`19004`
- 作用：剧情：执行 Select 流程
- RequestClass：`ScenarioSelectRequest`
- ResponseClass：`ScenarioSelectResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ScriptGroupId` | `long` | ScriptGroup ID。 |
| `ScriptSelectGroup` | `long` | 脚本选项组。 |

#### Response 字段

无字段或未匹配到结构。

### Scenario_AccountStudentChange

- 协议号：`19005`
- 作用：剧情：执行 AccountStudentChange 流程
- RequestClass：`ScenarioAccountStudentChangeRequest`
- ResponseClass：`ScenarioAccountStudentChangeResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountStudent` | `long` | 账号学生状态。 |
| `AccountStudentBefore` | `long` | 变更前账号学生状态。 |

#### Response 字段

无字段或未匹配到结构。

### Scenario_LobbyStudentChange

- 协议号：`19006`
- 作用：剧情：大厅StudentChange
- RequestClass：`ScenarioLobbyStudentChangeRequest`
- ResponseClass：`ScenarioLobbyStudentChangeResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `LobbyStudents` | `List<long>?` | LobbyStudents数据列表。 |
| `LobbyStudentsBefore` | `List<long>?` | LobbyStudentsBefore数据列表。 |

#### Response 字段

无字段或未匹配到结构。

### Scenario_SpecialLobbyChange

- 协议号：`19007`
- 作用：剧情：Special大厅Change
- RequestClass：`ScenarioSpecialLobbyChangeRequest`
- ResponseClass：`ScenarioSpecialLobbyChangeResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MemoryLobbyId` | `long` | MemoryLobby ID。 |
| `MemoryLobbyIdBefore` | `long` | 变更前记忆大厅 ID。 |

#### Response 字段

无字段或未匹配到结构。

### Scenario_Enter

- 协议号：`19008`
- 作用：剧情：进入对应功能入口
- RequestClass：`ScenarioEnterRequest`
- ResponseClass：`ScenarioEnterResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ScenarioId` | `long` | 剧情 ID。 |

#### Response 字段

无字段或未匹配到结构。

### Scenario_EnterMainStage

- 协议号：`19009`
- 作用：剧情：进入Main关卡
- RequestClass：`ScenarioEnterMainStageRequest`
- ResponseClass：`ScenarioEnterMainStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `StoryStrategyStageSaveDB?` | SaveData数据。 |

### Scenario_ConfirmMainStage

- 协议号：`19010`
- 作用：剧情：ConfirmMain关卡
- RequestClass：`ScenarioConfirmMainStageRequest`
- ResponseClass：`ScenarioConfirmMainStageResponse`
- 状态：SDK 已封装为剧情关卡结果确认方法 `client.scenario.confirm_main_stage(stage_unique_id, confirm=True)`；默认 `validate=True` 会本地拦截。当前 live 账号没有可确认的活跃剧情关卡 SaveData，`Scenario_List` 历史记录不能作为默认前置条件；只有调用方先获得活跃关卡上下文后，才应传 `validate=False` 发送。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `SaveDataDB` | `StoryStrategyStageSaveDB?` | SaveData数据。 |
| `ScenarioIds` | `List<long>?` | ID 列表。 |

### Scenario_DeployEchelon

- 协议号：`19011`
- 作用：剧情：布置Echelon
- RequestClass：`ScenarioDeployEchelonRequest`
- ResponseClass：`ScenarioDeployEchelonResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `DeployedEchelons` | `List<HexaUnit>?` | DeployedEchelons数据列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `StoryStrategyStageSaveDB?` | SaveData数据。 |

### Scenario_WithdrawEchelon

- 协议号：`19012`
- 作用：剧情：执行 WithdrawEchelon 流程
- RequestClass：`ScenarioWithdrawEchelonRequest`
- ResponseClass：`ScenarioWithdrawEchelonResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `WithdrawEchelonEntityId` | `List<long>?` | Withdraw编队Entity ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `StoryStrategyStageSaveDB?` | SaveData数据。 |
| `WithdrawEchelonDBs` | `List<EchelonDB>?` | WithdrawEchelon 数据列表。 |

### Scenario_MapMove

- 协议号：`19013`
- 作用：剧情：执行 MapMove 流程
- RequestClass：`ScenarioMapMoveRequest`
- ResponseClass：`ScenarioMapMoveResponse`
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
| `SaveDataDB` | `StoryStrategyStageSaveDB?` | SaveData数据。 |
| `ScenarioIds` | `List<long>?` | ID 列表。 |
| `EchelonEntityId` | `long` | 编队Entity ID。 |
| `StrategyObject` | `Strategy?` | 策略地图对象。 |
| `StrategyObjectParcelInfos` | `List<ParcelInfo>?` | StrategyObject奖励包Infos数据列表。 |

### Scenario_EndTurn

- 协议号：`19014`
- 作用：剧情：执行 EndTurn 流程
- RequestClass：`ScenarioEndTurnRequest`
- ResponseClass：`ScenarioEndTurnResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDataDB` | `StoryStrategyStageSaveDB?` | SaveData数据。 |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `ScenarioIds` | `List<long>?` | ID 列表。 |

### Scenario_Portal

- 协议号：`19018`
- 作用：剧情：执行 Portal 流程
- RequestClass：`ScenarioPortalRequest`
- ResponseClass：`ScenarioPortalResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |
| `EchelonEntityId` | `long` | 编队Entity ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StoryStrategyStageSaveDB` | `StoryStrategyStageSaveDB?` | StoryStrategy关卡Save数据。 |
| `ScenarioIds` | `List<long>?` | ID 列表。 |

### Scenario_RestartMainStage

- 协议号：`19019`
- 作用：剧情：RestartMain关卡
- RequestClass：`ScenarioRestartMainStageRequest`
- ResponseClass：`ScenarioRestartMainStageResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `SaveDataDB` | `StoryStrategyStageSaveDB?` | SaveData数据。 |

### Scenario_SkipMainStage

- 协议号：`19020`
- 作用：剧情：SkipMain关卡
- RequestClass：`ScenarioSkipMainStageRequest`
- ResponseClass：`ScenarioSkipMainStageResponse`
- 状态：SDK 已封装为剧情关卡跳过方法 `client.scenario.skip_main_stage(stage_unique_id, confirm=True)`；默认 `validate=True` 会本地拦截。当前 live 账号没有可跳过的活跃剧情关卡 SaveData，`Scenario_List` 历史记录不能作为默认前置条件；只有调用方先获得活跃关卡上下文后，才应传 `validate=False` 发送。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

无字段或未匹配到结构。
