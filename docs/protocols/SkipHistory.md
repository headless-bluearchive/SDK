# SkipHistory 协议

扫荡历史模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `SkipHistory_List` | `18000` | 扫荡历史：获取列表数据 | `SkipHistoryListRequest` | `SkipHistoryListResponse` |
| `SkipHistory_Save` | `18001` | 扫荡历史：保存状态 | `SkipHistorySaveRequest` | `SkipHistorySaveResponse` |

## 字段结构参考

### SkipHistory_List

- 协议号：`18000`
- 作用：查看扫荡历史列表。对应游戏里扫荡页保存的历史记录入口，主要用于回看已经扫过哪些关卡。
- RequestClass：`SkipHistoryListRequest`
- ResponseClass：`SkipHistoryListResponse`
- 状态：SDK 已封装为扫荡历史读取方法；当前 live 探针返回过 `Protocol=-1 / ErrorCode=500`，说明它更依赖服务端状态，不适合作为稳定轮询页。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SkipHistoryDB` | `SkipHistoryDB?` | 单个扫荡历史数据。 |
| `SkipHistoryDBs` | `List<SkipHistoryDB>?` | 扫荡历史数据列表。 |

### SkipHistory_Save

- 协议号：`18001`
- 作用：保存扫荡历史状态。对应游戏里刷新或写回扫荡页历史记录的动作。
- RequestClass：`SkipHistorySaveRequest`
- ResponseClass：`SkipHistorySaveResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SkipHistoryDB` | `SkipHistoryDB?` | 要保存的扫荡历史数据。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SkipHistoryDB` | `SkipHistoryDB?` | 保存后的扫荡历史数据。 |

## SDK 侧对应

`client.sweep.skip_history_list()` 会返回：

```python
{
    "skip_history": [...],
    "count": 0,
    "extra": {},
}
```

`count` 表示当前解析到的扫荡历史条目数。`extra` 保留未显式映射的原始字段。

如果 live 探针返回 `Protocol=-1 / ErrorCode=500`，先把它当成服务端状态/开放条件问题，而不是参数拼错。
