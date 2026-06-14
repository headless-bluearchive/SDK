# ResetableContent 协议

ResetableContent 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `ResetableContent_Get` | `41000` | 可重置内容：获取数据 | `ResetableContentGetRequest` | `ResetableContentGetResponse` |

## 字段结构参考

### ResetableContent_Get

- 协议号：`41000`
- 作用：可重置内容：获取数据
- RequestClass：`ResetableContentGetRequest`
- ResponseClass：`ResetableContentGetResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ResetableContentValueDBs` | `List<ResetableContentValueDB>?` | ResetableContentValue 数据列表。 |
