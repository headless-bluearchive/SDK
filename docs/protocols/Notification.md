# Notification 协议

Notification 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Notification_LobbyCheck` | `36000` | 通知：大厅检查 | `NotificationLobbyCheckRequest` | `NotificationLobbyCheckResponse` |
| `Notification_EventContentReddotCheck` | `36001` | 通知：活动内容Reddot检查 | `NotificationEventContentReddotRequest` | `NotificationEventContentReddotResponse` |

## 字段结构参考

### Notification_LobbyCheck

- 协议号：`36000`
- 作用：通知：大厅检查
- RequestClass：`NotificationLobbyCheckRequest`
- ResponseClass：`NotificationLobbyCheckResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `UnreadMailCount` | `long` | 数量。 |
| `EventRewardIncreaseDBs` | `List<EventRewardIncreaseDB>?` | EventRewardIncrease 数据列表。 |

### Notification_EventContentReddotCheck

- 协议号：`36001`
- 作用：通知：活动内容Reddot检查
- RequestClass：`NotificationEventContentReddotRequest`
- ResponseClass：`NotificationEventContentReddotResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Reddots` | `Dictionary<long, List<NotificationEventReddot>>?` | 红点通知映射。 |
| `EventContentUnlockCGDBs` | `Dictionary<long, List<EventContentCollectionDB>>?` | EventContentUnlockCG 数据列表。 |
