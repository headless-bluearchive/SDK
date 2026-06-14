# Minigame_protocols 协议

Minigame_protocols 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Minigame_CCGReplaceCharacter` | `35040` | 小游戏：CCGReplace角色 | `MiniGameCCGReplaceCharacterRequest` | `MiniGameCCGReplaceCharacterResponse` |

## 字段结构参考

### Minigame_CCGReplaceCharacter

- 协议号：`35040`
- 作用：小游戏：CCGReplace角色
- RequestClass：`MiniGameCCGReplaceCharacterRequest`
- ResponseClass：`MiniGameCCGReplaceCharacterResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventContentId` | `long` | EventContent ID。 |
| `SlotIndex` | `int` | 槽位索引索引。 |
| `CharacterId` | `long` | 角色模板 ID。 |
| `IsStriker` | `bool` | 布尔状态。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SaveDB` | `MiniGameCCGSaveDB?` | Save数据。 |
| `CCGCharacterDB` | `MiniGameCCGCharacterDB?` | CCG角色数据。 |
