# ClearDeck 协议

通关编队模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `ClearDeck_List` | `34000` | 通关编队记录：获取列表数据 | `ClearDeckListRequest` | `ClearDeckListResponse` |
| `ClearDeck_GroupedList` | `34001` | 通关编队记录：Grouped列表 | `ClearDeckGroupedListRequest` | `ClearDeckGroupedListResponse` |

## 字段结构参考

### ClearDeck_List

- 协议号：`34000`
- 作用：通关编队记录：获取列表数据
- RequestClass：`ClearDeckListRequest`
- ResponseClass：`ClearDeckListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClearDeckKey` | `ClearDeckKey` | 通关DeckKey。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClearDeckDBs` | `List<ClearDeckDB>?` | ClearDeck 数据列表。 |

### ClearDeck_GroupedList

- 协议号：`34001`
- 作用：通关编队记录：Grouped列表
- RequestClass：`ClearDeckGroupedListRequest`
- ResponseClass：`ClearDeckGroupedListResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
