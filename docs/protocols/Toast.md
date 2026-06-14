# Toast 协议

Toast 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Toast_List` | `16000` | Toast 提示：获取列表数据 | `ToastListRequest` | `ToastListResponse` |

## 字段结构参考

### Toast_List

- 协议号：`16000`
- 作用：Toast 提示：获取列表数据
- RequestClass：`ToastListRequest`
- ResponseClass：`ToastListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ToastDBs` | `List<ToastDB>?` | Toast 数据列表。 |
