# System 协议

System 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `System_Version` | `1` | 系统：获取系统版本 | `SystemVersionRequest` | `SystemVersionResponse` |

## 字段结构参考

### System_Version

- 协议号：`1`
- 作用：系统：获取系统版本
- RequestClass：`SystemVersionRequest`
- ResponseClass：`SystemVersionResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CurrentVersion` | `long` | 当前客户端版本。 |
| `MinimumVersion` | `long` | 最低可用客户端版本。 |
| `IsDevelopment` | `bool` | 布尔状态。 |
