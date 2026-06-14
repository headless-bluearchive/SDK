# Mail 协议

邮件模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Mail_List` | `7000` | 邮件：获取列表数据 | `MailListRequest` | `MailListResponse` |
| `Mail_Check` | `7001` | 邮件：检查状态 | `MailCheckRequest` | `MailCheckResponse` |
| `Mail_Receive` | `7002` | 邮件：领取奖励 | `MailReceiveRequest` | `MailReceiveResponse` |
| `Mail_ListSemiPermanent` | `7003` | 邮件：列表Semi常驻 | `MailListSemiPermanentRequest` | `MailListSemiPermanentResponse` |
| `Mail_ReceiveSemiPermanent` | `7004` | 邮件：领取Semi常驻 | `MailReceiveSemiPermanentRequest` | `MailReceiveSemiPermanentResponse` |

## 字段结构参考

### Mail_List

- 协议号：`7000`
- 作用：邮件：获取列表数据
- RequestClass：`MailListRequest`
- ResponseClass：`MailListResponse`
- 状态：SDK 已封装并通过 live 只读验证。

#### SDK 方法

```python
mails = await client.mail.list()
```

返回结构：

| 字段 | 说明 |
| --- | --- |
| `mails` | 邮件数据列表。 |
| `count` | 服务端返回的邮件数量。 |
| `extra` | 服务端返回中的其他顶层字段。 |

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `IsReadMail` | `bool` | 布尔状态。 |
| `PivotTime` | `DateTime` | 分页基准时间。 |
| `PivotIndex` | `long` | Pivot索引索引。 |
| `IsDescending` | `bool` | 布尔状态。 |
| `mailSortingRule` | `MailSortingRule` | 邮件排序规则。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MailDBs` | `List<MailDB>?` | Mail 数据列表。 |
| `Count` | `long` | 数量。 |

### Mail_Check

- 协议号：`7001`
- 作用：邮件：检查状态
- RequestClass：`MailCheckRequest`
- ResponseClass：`MailCheckResponse`
- 状态：SDK 已封装并通过 live 只读验证。真实返回字段为 `CommonMailCount`，SDK 会统一整理为 `count`。

#### SDK 方法

```python
mail_status = await client.mail.check()
```

返回结构：

| 字段 | 说明 |
| --- | --- |
| `count` | 当前普通邮件数量。 |
| `extra` | 服务端返回中的其他顶层字段。 |

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Count` | `long` | 数量。 |

### Mail_Receive

- 协议号：`7002`
- 作用：邮件：领取奖励
- RequestClass：`MailReceiveRequest`
- ResponseClass：`MailReceiveResponse`
- 状态：SDK 已封装并通过 live 状态变更验证。领取 ID 使用 `Mail_List` 返回的 `ServerId`；小号当前返回 `ErrorCode=1032 NexonNgsmValidateFail`，大号验证成功。

#### SDK 方法

```python
reward = await client.mail.receive([mail_server_id])
```

`receive()` 只领取调用方显式指定的邮件，不会自动领取全部邮件。默认会先调用 `Mail_List` 确认邮件存在，再发送领取请求。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MailServerIds` | `List<long>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MailServerIds` | `List<long>?` | ID 列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `BattlePassInfoDBs` | `List<BattlePassInfoDB>?` | BattlePassInfo 数据列表。 |

### Mail_ListSemiPermanent

- 协议号：`7003`
- 作用：邮件：列表Semi常驻
- RequestClass：`MailListSemiPermanentRequest`
- ResponseClass：`MailListSemiPermanentResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Mail_ReceiveSemiPermanent

- 协议号：`7004`
- 作用：邮件：领取Semi常驻
- RequestClass：`MailReceiveSemiPermanentRequest`
- ResponseClass：`MailReceiveSemiPermanentResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
