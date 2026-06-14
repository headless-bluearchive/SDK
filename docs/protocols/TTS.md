# TTS 协议

TTS 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `TTS_GetFile` | `31000` | 语音/假名：获取文件 | `TTSGetFileRequest` | `TTSGetFileResponse` |
| `TTS_GetKana` | `31001` | 语音/假名：获取假名/读音数据 | `TTSGetKanaRequest` | `TTSGetKanaResponse` |

## 字段结构参考

### TTS_GetFile

- 协议号：`31000`
- 作用：语音/假名：获取文件
- RequestClass：`TTSGetFileRequest`
- ResponseClass：`TTSGetFileResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `IsFileReady` | `bool` | 布尔状态。 |
| `TTSFileS3Uri` | `string?` | TTS 文件 S3 地址。 |

### TTS_GetKana

- 协议号：`31001`
- 作用：语音/假名：获取假名/读音数据
- RequestClass：`TTSGetKanaRequest`
- ResponseClass：`TTSGetKanaResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CallName` | `string?` | 老师称呼。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CallName` | `string?` | 老师称呼。 |
| `ActualCallName` | `string?` | 实际老师称呼。 |
| `CallNameKatakana` | `string?` | 片假名老师称呼。 |
| `CallNameKorean` | `string?` | 韩文老师称呼。 |
| `ActualCallNameKorean` | `string?` | 实际韩文老师称呼。 |
