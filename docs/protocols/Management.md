# Management 协议

运营管理模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Management_BannerList` | `100000` | 经营/管理玩法：Banner列表 | `ManagementBannerListRequest` | `ManagementBannerListResponse` |
| `Management_ProtocolLockList` | `100001` | 经营/管理玩法：ProtocolLock列表 | `ManagementProtocolLockListRequest` | `ManagementProtocolLockListResponse` |

## 字段结构参考

### Management_BannerList

- 协议号：`100000`
- 作用：经营/管理玩法：Banner列表
- RequestClass：`ManagementBannerListRequest`
- ResponseClass：`ManagementBannerListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BannerDBs` | `List<BannerDB>?` | Banner 数据列表。 |

### Management_ProtocolLockList

- 协议号：`100001`
- 作用：经营/管理玩法：ProtocolLock列表
- RequestClass：`ManagementProtocolLockListRequest`
- ResponseClass：`ManagementProtocolLockListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ProtocolLockDBs` | `List<ProtocolLockDB>?` | ProtocolLock 数据列表。 |
