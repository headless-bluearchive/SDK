# MemoryLobby 协议

记忆大厅模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `MemoryLobby_List` | `12000` | 回忆大厅：获取列表数据 | `MemoryLobbyListRequest` | `MemoryLobbyListResponse` |
| `MemoryLobby_SetMain` | `12001` | 回忆大厅：设置Main | `MemoryLobbySetMainRequest` | `MemoryLobbySetMainResponse` |
| `MemoryLobby_UpdateLobbyMode` | `12002` | 回忆大厅：更新大厅Mode | `MemoryLobbyUpdateLobbyModeRequest` | `MemoryLobbyUpdateLobbyModeResponse` |
| `MemoryLobby_Interact` | `12003` | 回忆大厅：与咖啡厅内角色互动/摸头 | `MemoryLobbyInteractRequest` | `MemoryLobbyInteractResponse` |

## 字段结构参考

### MemoryLobby_List

- 协议号：`12000`
- 作用：回忆大厅：获取列表数据
- RequestClass：`MemoryLobbyListRequest`
- ResponseClass：`MemoryLobbyListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MemoryLobbyDBs` | `List<MemoryLobbyDB>?` | MemoryLobby 数据列表。 |

### MemoryLobby_SetMain

- 协议号：`12001`
- 作用：回忆大厅：设置Main
- RequestClass：`MemoryLobbySetMainRequest`
- ResponseClass：`MemoryLobbySetMainResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MemoryLobbyId` | `long` | MemoryLobby ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountDB` | `AccountDB?` | 账号数据。 |

### MemoryLobby_UpdateLobbyMode

- 协议号：`12002`
- 作用：回忆大厅：更新大厅Mode
- RequestClass：`MemoryLobbyUpdateLobbyModeRequest`
- ResponseClass：`MemoryLobbyUpdateLobbyModeResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `IsMemoryLobbyMode` | `bool` | 布尔状态。 |

#### Response 字段

无字段或未匹配到结构。

### MemoryLobby_Interact

- 协议号：`12003`
- 作用：回忆大厅：与咖啡厅内角色互动/摸头
- RequestClass：`MemoryLobbyInteractRequest`
- ResponseClass：`MemoryLobbyInteractResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
