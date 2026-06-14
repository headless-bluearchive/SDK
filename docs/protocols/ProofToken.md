# ProofToken 协议

ProofToken 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `ProofToken_RequestQuestion` | `37000` | ProofToken 验证：请求 ProofToken 问题 | `ProofTokenRequestQuestionRequest` | `ProofTokenRequestQuestionResponse` |
| `ProofToken_Submit` | `37001` | ProofToken 验证：提交 ProofToken 答案 | `ProofTokenSubmitRequest` | `ProofTokenSubmitResponse` |

## 字段结构参考

### ProofToken_RequestQuestion

- 协议号：`37000`
- 作用：ProofToken 验证：请求 ProofToken 问题
- RequestClass：`ProofTokenRequestQuestionRequest`
- ResponseClass：`ProofTokenRequestQuestionResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Hint` | `long` | 提示值。 |
| `Question` | `string?` | 问题内容。 |

### ProofToken_Submit

- 协议号：`37001`
- 作用：ProofToken 验证：提交 ProofToken 答案
- RequestClass：`ProofTokenSubmitRequest`
- ResponseClass：`ProofTokenSubmitResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Answer` | `long` | 答案。 |

#### Response 字段

无字段或未匹配到结构。
