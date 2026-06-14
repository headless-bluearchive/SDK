# Queuing 协议

排队模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Queuing_GetTicket` | `50000` | 排队/网关票据：获取进入游戏网关所需票据 | `QueuingGetTicketRequest` | `QueuingGetTicketResponse` |
| `Queuing_GetCryptoKeys` | `50001` | 排队/网关票据：获取CryptoKeys | `QueuingGetCryptoKeysRequest` | `QueuingGetCryptoKeysResponse` |
| `Queuing_GetAuthTicket` | `50002` | 排队/网关票据：获取Auth票据 | `QueuingGetAuthTicketRequest` | `QueuingGetAuthTicketResponse` |
| `Queuing_ProcessWaitingQueue` | `50003` | 排队/网关票据：执行 ProcessWaitingQueue 流程 | `QueuingProcessWaitingQueueRequest` | `QueuingProcessWaitingQueueResponse` |

## 字段结构参考

### Queuing_GetTicket

- 协议号：`50000`
- 作用：排队/网关票据：获取进入游戏网关所需票据
- RequestClass：`QueuingGetTicketRequest`
- ResponseClass：`QueuingGetTicketResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `YostarUID` | `int64` | Yostar 用户 ID。 |
| `YostarToken` | `string` | Yostar 登录 token。 |
| `MakeStandby` | `bool` | 是否进入等待队列。 |
| `PassCheck` | `bool` | 基础通行检查状态。 |
| `PassCheckYostar` | `bool` | Yostar 通行检查状态。 |
| `WaitingTicket` | `string?` | 排队等待票据。 |
| `ClientVersion` | `string?` | 客户端版本字符串。 |
| `NpSN` | `long` | Nexon publisher account id / guid。 |
| `NpToken` | `string?` | Nexon / TOYSDK token。 |
| `Npacode` | `string?` | Nexon npaCode。 |
| `OSType` | `string?` | 系统类型。 |
| `AccessIP` | `string?` | 出口 IP。 |
| `PassCheckNexon` | `bool` | Nexon 通行检查状态。 |
| `NgsmToken` | `string?` | NGS-X / NGSM token。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `WaitingTicket` | `string?` | 排队等待票据。 |
| `EnterTicket` | `string?` | 进入主网关前置票据。 |
| `TicketSequence` | `long` | 票据序号。 |
| `AllowedSequence` | `long` | 允许进入的序号。 |
| `RequiredSecondsPerUser` | `double` | 每名用户预计等待秒数。 |
| `Birth` | `string?` | Birth。 |
| `ServerSeed` | `string?` | 服务器随机种子。 |

### Queuing_GetCryptoKeys

- 协议号：`50001`
- 作用：排队/网关票据：获取CryptoKeys
- RequestClass：`QueuingGetCryptoKeysRequest`
- ResponseClass：`QueuingGetCryptoKeysResponse`
- 状态：登录链路已接入。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClientGeneratedKey` | `string` | 客户端生成的 16 bytes key，base64 后发送。 |
| `ClientGeneratedIV` | `string` | 客户端生成的 16 bytes IV，base64 后发送。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EncryptedKey` | `string` | 网关请求加密 key material。 |
| `SignedKey` | `string` | 网关签名 key material。 |
| `EncryptedIV` | `string` | 网关请求加密 IV material。 |
| `SignedIV` | `string` | 网关签名 IV material。 |
| `EncryptedSqlCipherKey` | `string` | 历史/逆向字段观察，当前 `ExcelDB.db` 解析不依赖此字段。 |
| `EncryptedSqlCipherLicense` | `string` | 历史/逆向字段观察，当前 `ExcelDB.db` 解析不依赖此字段。 |

当前 `ExcelDB.db` SQLCipher key/license 使用 `config/official_data.py` 中的固定配置；日志、文档和测试输出不得回显 key/license 明文。

### Queuing_GetAuthTicket

- 协议号：`50002`
- 作用：排队/网关票据：获取Auth票据
- RequestClass：`QueuingGetAuthTicketRequest`
- ResponseClass：`QueuingGetAuthTicketResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Queuing_ProcessWaitingQueue

- 协议号：`50003`
- 作用：排队/网关票据：执行 ProcessWaitingQueue 流程
- RequestClass：`QueuingProcessWaitingQueueRequest`
- ResponseClass：`QueuingProcessWaitingQueueResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
