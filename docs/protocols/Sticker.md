# Sticker 协议

贴纸模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Sticker_Login` | `47000` | 贴纸：进入模块并同步基础数据 | `StickerLoginRequest` | `StickerLoginResponse` |
| `Sticker_Lobby` | `47001` | 贴纸：获取或进入模块大厅 | `StickerLobbyRequest` | `StickerLobbyResponse` |
| `Sticker_UseSticker` | `47002` | 贴纸：使用贴纸 | `StickerUseStickerRequest` | `StickerUseStickerResponse` |

## 字段结构参考

### Sticker_Login

- 协议号：`47000`
- 作用：贴纸：进入模块并同步基础数据
- RequestClass：`StickerLoginRequest`
- ResponseClass：`StickerLoginResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StickerBookDB` | `StickerBookDB?` | StickerBook数据。 |

### Sticker_Lobby

- 协议号：`47001`
- 作用：贴纸：获取或进入模块大厅
- RequestClass：`StickerLobbyRequest`
- ResponseClass：`StickerLobbyResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AcquireStickerUniqueIds` | `IEnumerable<long>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ReceivedStickerDBs` | `IEnumerable<StickerDB>?` | ReceivedSticker 数据列表。 |
| `StickerBookDB` | `StickerBookDB?` | StickerBook数据。 |

### Sticker_UseSticker

- 协议号：`47002`
- 作用：贴纸：使用贴纸
- RequestClass：`StickerUseStickerRequest`
- ResponseClass：`StickerUseStickerResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StickerUniqueId` | `long` | Sticker唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StickerBookDB` | `StickerBookDB?` | StickerBook数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
