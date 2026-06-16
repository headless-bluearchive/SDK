# PermanentRaid 协议

PermanentRaid 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `PermanentRaid_Lobby` | `54000` | 常驻总力战：获取或进入模块大厅 | `PermanentRaidLobbyRequest` | `PermanentRaidLobbyResponse` |

## 字段结构参考

### PermanentRaid_Lobby

- 协议号：`54000`
- 作用：常驻总力战：获取或进入模块大厅
- RequestClass：`PermanentRaidLobbyRequest`
- ResponseClass：`PermanentRaidLobbyResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
