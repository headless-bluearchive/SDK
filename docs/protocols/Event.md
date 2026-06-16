# Event 协议

Event 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Event_GetList` | `25000` | 活动：获取列表 | `EventListRequest` | `EventListResponse` |
| `Event_GetImage` | `25001` | 活动：获取Image | `EventImageRequest` | `EventImageResponse` |
| `Event_UseCoupon` | `25002` | 活动：使用Coupon | `UseCouponRequest` | `UseCouponResponse` |
| `Event_RewardIncrease` | `25003` | 活动：奖励Increase | `EventRewardIncreaseRequest` | `EventRewardIncreaseResponse` |

## 字段结构参考

### Event_GetList

- 协议号：`25000`
- 作用：活动：获取列表
- RequestClass：`EventListRequest`
- ResponseClass：`EventListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventInfoDBs` | `List<EventInfoDB>?` | EventInfo 数据列表。 |

### Event_GetImage

- 协议号：`25001`
- 作用：活动：获取Image
- RequestClass：`EventImageRequest`
- ResponseClass：`EventImageResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventId` | `long` | Event ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ImageBytes` | `byte[]?` | 图片字节数据。 |

### Event_UseCoupon

- 协议号：`25002`
- 作用：活动：使用Coupon
- RequestClass：`UseCouponRequest`
- ResponseClass：`UseCouponResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CouponSerial` | `string?` | 兑换码序列号。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CouponCompleteRewardReceived` | `bool` | CouponComplete奖励Received奖励信息。 |

### Event_RewardIncrease

- 协议号：`25003`
- 作用：活动：奖励Increase
- RequestClass：`EventRewardIncreaseRequest`
- ResponseClass：`EventRewardIncreaseResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EventRewardIncreaseDBs` | `List<EventRewardIncreaseDB>?` | EventRewardIncrease 数据列表。 |
