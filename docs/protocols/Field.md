# Field 协议

场景探索模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Field_Sync` | `48000` | 场景/地图互动：同步模块状态 | `FieldSyncRequest` | `FieldSyncResponse` |
| `Field_Interaction` | `48001` | 场景/地图互动：执行 Interaction 流程 | `FieldInteractionRequest` | `FieldInteractionResponse` |
| `Field_QuestClear` | `48002` | 场景/地图互动：Quest清空 | `FieldQuestClearRequest` | `FieldQuestClearResponse` |
| `Field_SceneChanged` | `48003` | 场景/地图互动：执行 SceneChanged 流程 | `FieldSceneChangedRequest` | `FieldSceneChangedResponse` |
| `Field_EndDate` | `48004` | 场景/地图互动：执行 EndDate 流程 | `FieldEndDateRequest` | `FieldEndDateResponse` |
| `Field_EnterStage` | `48005` | 场景/地图互动：进入关卡 | `FieldEnterStageRequest` | `FieldEnterStageResponse` |

## 字段结构参考

### Field_Sync

- 协议号：`48000`
- 作用：场景/地图互动：同步模块状态
- RequestClass：`FieldSyncRequest`
- ResponseClass：`FieldSyncResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Field_Interaction

- 协议号：`48001`
- 作用：场景/地图互动：执行 Interaction 流程
- RequestClass：`FieldInteractionRequest`
- ResponseClass：`FieldInteractionResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Field_QuestClear

- 协议号：`48002`
- 作用：场景/地图互动：Quest清空
- RequestClass：`FieldQuestClearRequest`
- ResponseClass：`FieldQuestClearResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Field_SceneChanged

- 协议号：`48003`
- 作用：场景/地图互动：执行 SceneChanged 流程
- RequestClass：`FieldSceneChangedRequest`
- ResponseClass：`FieldSceneChangedResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Field_EndDate

- 协议号：`48004`
- 作用：场景/地图互动：执行 EndDate 流程
- RequestClass：`FieldEndDateRequest`
- ResponseClass：`FieldEndDateResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Field_EnterStage

- 协议号：`48005`
- 作用：场景/地图互动：进入关卡
- RequestClass：`FieldEnterStageRequest`
- ResponseClass：`FieldEnterStageResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
