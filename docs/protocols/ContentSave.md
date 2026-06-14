# ContentSave 协议

内容存档模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `ContentSave_Get` | `26000` | 内容存档：获取数据 | `ContentSaveGetRequest` | `ContentSaveGetResponse` |
| `ContentSave_Discard` | `26001` | 内容存档：执行 Discard 流程 | `ContentSaveDiscardRequest` | `ContentSaveDiscardResponse` |

## 字段结构参考

### ContentSave_Get

- 协议号：`26000`
- 作用：内容存档：获取数据
- RequestClass：`ContentSaveGetRequest`
- ResponseClass：`ContentSaveGetResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `HasValidData` | `bool` | 是否已有ValidData。 |
| `ContentSaveDB` | `ContentSaveDB?` | ContentSave数据。 |
| `EventContentChangeDB` | `EventContentChangeDB?` | EventContentChange数据。 |

### ContentSave_Discard

- 协议号：`26001`
- 作用：内容存档：执行 Discard 流程
- RequestClass：`ContentSaveDiscardRequest`
- ResponseClass：`ContentSaveDiscardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ContentType` | `ContentType` | 内容类型。 |
| `StageUniqueId` | `long` | 关卡唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
