# NetworkTime 协议

网络时间模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `NetworkTime_Sync` | `3` | 网络时间：同步模块状态 | `NetworkTimeSyncRequest` | `NetworkTimeSyncResponse` |
| `NetworkTime_SyncReply` | `4` | 网络时间：同步Reply | `` | `` |

## 字段结构参考

### NetworkTime_Sync

- 协议号：`3`
- 作用：网络时间：同步模块状态
- RequestClass：`NetworkTimeSyncRequest`
- ResponseClass：`NetworkTimeSyncResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ReceiveTick` | `long` | 接收 tick。 |
| `EchoSendTick` | `long` | 回显发送 tick。 |

### NetworkTime_SyncReply

- 协议号：`4`
- 作用：网络时间：同步Reply
- RequestClass：``
- ResponseClass：``
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
