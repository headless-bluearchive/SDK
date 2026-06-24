# Attachment 协议

附件与头像框模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Attachment_Get` | `46000` | 附件与头像框：获取数据 | `AttachmentGetRequest` | `AttachmentGetResponse` |
| `Attachment_EmblemList` | `46001` | 附件与头像框：Emblem列表 | `AttachmentEmblemListRequest` | `AttachmentEmblemListResponse` |
| `Attachment_EmblemAcquire` | `46002` | 附件与头像框：领取已解锁 Emblem | `AttachmentEmblemAcquireRequest` | `AttachmentEmblemAcquireResponse` |
| `Attachment_EmblemAttach` | `46003` | 附件与头像框：装配 Emblem 到资料页 | `AttachmentEmblemAttachRequest` | `AttachmentEmblemAttachResponse` |

## 字段结构参考

### Attachment_Get

- 协议号：`46000`
- 作用：附件与头像框：获取数据
- RequestClass：`AttachmentGetRequest`
- ResponseClass：`AttachmentGetResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountAttachmentDB` | `AccountAttachmentDB?` | 账号附件数据。 |

### Attachment_EmblemList

- 协议号：`46001`
- 作用：附件与头像框：Emblem列表
- RequestClass：`AttachmentEmblemListRequest`
- ResponseClass：`AttachmentEmblemListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EmblemDBs` | `List<EmblemDB>?` | Emblem 数据列表。 |

### Attachment_EmblemAcquire

- 协议号：`46002`
- 作用：附件与头像框：执行 EmblemAcquire 流程
- RequestClass：`AttachmentEmblemAcquireRequest`
- ResponseClass：`AttachmentEmblemAcquireResponse`
- 状态：SDK 已封装为头像框/Emblem 页的领取入口；调用前应先从 `Attachment_EmblemList` 确认当前可用 ID。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `UniqueIds` | `List<long>?` | 要领取的 Emblem 唯一 ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EmblemDBs` | `List<EmblemDB>?` | Emblem 数据列表。 |

### Attachment_EmblemAttach

- 协议号：`46003`
- 作用：附件与头像框：执行 EmblemAttach 流程
- RequestClass：`AttachmentEmblemAttachRequest`
- ResponseClass：`AttachmentEmblemAttachResponse`
- 状态：SDK 已封装为头像框/Emblem 页的装配入口；调用前应先从 `Attachment_EmblemList` 确认当前可用 ID。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `UniqueId` | `long` | 要装配的 Emblem 唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AttachmentDB` | `AccountAttachmentDB?` | 附件数据。 |
