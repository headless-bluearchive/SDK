# SkipHistory 协议

SkipHistory 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `SkipHistory_List` | `18000` | 扫荡历史：获取列表数据 | `SkipHistoryListRequest` | `SkipHistoryListResponse` |
| `SkipHistory_Save` | `18001` | 扫荡历史：保存状态 | `SkipHistorySaveRequest` | `SkipHistorySaveResponse` |

## 字段结构参考

### SkipHistory_List

- 协议号：`18000`
- 作用：扫荡历史：获取列表数据
- RequestClass：`SkipHistoryListRequest`
- ResponseClass：`SkipHistoryListResponse`
- 状态：待确认。live 探针返回 `Protocol=-1 / ErrorCode=500`，暂不封装为稳定 SDK API。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SkipHistoryDB` | `SkipHistoryDB?` | Skip历史数据。 |

### SkipHistory_Save

- 协议号：`18001`
- 作用：扫荡历史：保存状态
- RequestClass：`SkipHistorySaveRequest`
- ResponseClass：`SkipHistorySaveResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SkipHistoryDB` | `SkipHistoryDB?` | Skip历史数据。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SkipHistoryDB` | `SkipHistoryDB?` | Skip历史数据。 |
