# Friend 协议

好友模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Friend_List` | `43000` | 好友：获取列表数据 | `FriendListRequest` | `FriendListResponse` |
| `Friend_Remove` | `43001` | 好友：移除咖啡厅家具 | `FriendRemoveRequest` | `FriendRemoveResponse` |
| `Friend_GetFriendDetailedInfo` | `43002` | 好友：获取FriendDetailed信息 | `FriendGetFriendDetailedInfoRequest` | `FriendGetFriendDetailedInfoResponse` |
| `Friend_GetIdCard` | `43003` | 好友：获取IdCard | `FriendGetIdCardRequest` | `FriendGetIdCardResponse` |
| `Friend_SetIdCard` | `43004` | 好友：设置IdCard | `FriendSetIdCardRequest` | `FriendSetIdCardResponse` |
| `Friend_Search` | `43005` | 好友：搜索 | `FriendSearchRequest` | `FriendSearchResponse` |
| `Friend_SendFriendRequest` | `43006` | 好友：SendFriend请求 | `FriendSendFriendRequestRequest` | `FriendSendFriendRequestResponse` |
| `Friend_AcceptFriendRequest` | `43007` | 好友：AcceptFriend请求 | `FriendAcceptFriendRequestRequest` | `FriendAcceptFriendRequestResponse` |
| `Friend_DeclineFriendRequest` | `43008` | 好友：DeclineFriend请求 | `FriendDeclineFriendRequestRequest` | `FriendDeclineFriendRequestResponse` |
| `Friend_CancelFriendRequest` | `43009` | 好友：取消Friend请求 | `FriendCancelFriendRequestRequest` | `FriendCancelFriendRequestResponse` |
| `Friend_Check` | `43010` | 好友：检查状态 | `FriendCheckRequest` | `FriendCheckResponse` |
| `Friend_ListByIds` | `43011` | 好友：列表ByIds | `FriendListByIdsRequest` | `FriendListByIdsResponse` |
| `Friend_Block` | `43012` | 好友：执行 Block 流程 | `FriendBlockRequest` | `FriendBlockResponse` |
| `Friend_Unblock` | `43013` | 好友：执行 Unblock 流程 | `FriendUnblockRequest` | `FriendUnblockResponse` |

## 字段结构参考

### Friend_List

- 协议号：`43000`
- 作用：好友：获取列表数据
- RequestClass：`FriendListRequest`
- ResponseClass：`FriendListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `IdCardBackgroundDBs` | `IdCardBackgroundDB[]?` | IdCardBackground 数据列表。 |
| `FriendDBs` | `FriendDB[]?` | Friend 数据列表。 |
| `SentRequestFriendDBs` | `FriendDB[]?` | SentRequestFriend 数据列表。 |
| `ReceivedRequestFriendDBs` | `FriendDB[]?` | ReceivedRequestFriend 数据列表。 |
| `BlockedUserDBs` | `FriendDB[]?` | BlockedUser 数据列表。 |
| `FriendIdCardDB` | `FriendIdCardDB?` | 好友IdCard数据。 |

### Friend_Remove

- 协议号：`43001`
- 作用：好友：移除咖啡厅家具
- RequestClass：`FriendRemoveRequest`
- ResponseClass：`FriendRemoveResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetAccountId` | `long` | 目标账号 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `FriendDBs` | `FriendDB[]?` | Friend 数据列表。 |
| `SentRequestFriendDBs` | `FriendDB[]?` | SentRequestFriend 数据列表。 |
| `ReceivedRequestFriendDBs` | `FriendDB[]?` | ReceivedRequestFriend 数据列表。 |
| `BlockedUserDBs` | `FriendDB[]?` | BlockedUser 数据列表。 |

### Friend_GetFriendDetailedInfo

- 协议号：`43002`
- 作用：好友：获取FriendDetailed信息
- RequestClass：`FriendGetFriendDetailedInfoRequest`
- ResponseClass：`FriendGetFriendDetailedInfoResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `FriendAccountId` | `long` | 好友账号 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Nickname` | `string?` | 昵称。 |
| `Level` | `long` | 等级。 |
| `ClanName` | `string?` | 社团名称。 |
| `Comment` | `string?` | 个人简介。 |
| `FriendCount` | `long` | 好友数量。 |
| `FriendCode` | `string?` | 好友码。 |
| `RepresentCharacterUniqueId` | `long` | Represent角色唯一 ID。 |
| `RepresentCharacterCostumeId` | `long` | Represent角色服装 ID。 |
| `CharacterCount` | `long` | 数量。 |
| `LastNormalCampaignClearStageId` | `Nullable<long>` | LastNormal战役Clear关卡 ID。 |
| `LastHardCampaignClearStageId` | `Nullable<long>` | LastHard战役Clear关卡 ID。 |
| `RaidRanking` | `Nullable<long>` | 总力战排名。 |
| `RaidTier` | `Nullable<int>` | 总力战档位。 |
| `DetailedAccountInfoDB` | `DetailedAccountInfoDB?` | Detailed账号信息数据。 |
| `AttachmentDB` | `AccountAttachmentDB?` | 附件数据。 |
| `AssistCharacterDBs` | `AssistCharacterDB[]?` | AssistCharacter 数据列表。 |

### Friend_GetIdCard

- 协议号：`43003`
- 作用：好友：获取IdCard
- RequestClass：`FriendGetIdCardRequest`
- ResponseClass：`FriendGetIdCardResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `FriendIdCardDB` | `FriendIdCardDB?` | 好友IdCard数据。 |

### Friend_SetIdCard

- 协议号：`43004`
- 作用：好友：设置IdCard
- RequestClass：`FriendSetIdCardRequest`
- ResponseClass：`FriendSetIdCardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Comment` | `string?` | 个人简介。 |
| `RepresentCharacterUniqueId` | `long` | Represent角色唯一 ID。 |
| `EmblemId` | `long` | Emblem ID。 |
| `SearchPermission` | `bool` | 是否允许搜索。 |
| `AutoAcceptFriendRequest` | `bool` | AutoAcceptFriendRequest 子请求。 |
| `ShowAccountLevel` | `bool` | 是否显示账号等级。 |
| `ShowFriendCode` | `bool` | 是否显示好友码。 |
| `ShowRaidRanking` | `bool` | 是否显示总力战排名。 |
| `ShowEliminateRaidRanking` | `bool` | 是否显示综合战术考试排名。 |
| `BackgroundId` | `long` | Background ID。 |

#### Response 字段

无字段或未匹配到结构。

### Friend_Search

- 协议号：`43005`
- 作用：好友：搜索
- RequestClass：`FriendSearchRequest`
- ResponseClass：`FriendSearchResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `FriendCode` | `string?` | 好友码。 |
| `LevelOption` | `FriendSearchLevelOption` | 等级选项选项。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SearchResult` | `FriendDB[]?` | 搜索结果。 |

### Friend_SendFriendRequest

- 协议号：`43006`
- 作用：好友：SendFriend请求
- RequestClass：`FriendSendFriendRequestRequest`
- ResponseClass：`FriendSendFriendRequestResponse`
- 状态：SDK 已封装为好友页发送申请方法 `client.friend.send_request(target_account_id, confirm=True)`；默认先校验好友/已发送/已收到/屏蔽列表，本地协议调用测试通过，真实执行会发送好友申请。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetAccountId` | `long` | 目标账号 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `FriendDBs` | `FriendDB[]?` | Friend 数据列表。 |
| `SentRequestFriendDBs` | `FriendDB[]?` | SentRequestFriend 数据列表。 |
| `ReceivedRequestFriendDBs` | `FriendDB[]?` | ReceivedRequestFriend 数据列表。 |
| `BlockedUserDBs` | `FriendDB[]?` | BlockedUser 数据列表。 |

### Friend_AcceptFriendRequest

- 协议号：`43007`
- 作用：好友：AcceptFriend请求
- RequestClass：`FriendAcceptFriendRequestRequest`
- ResponseClass：`FriendAcceptFriendRequestResponse`
- 状态：SDK 已封装为好友页接受申请方法 `client.friend.accept_request(target_account_id, confirm=True)`；默认先校验收到的好友申请列表，本地协议调用测试通过，真实执行会接受好友申请。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetAccountId` | `long` | 目标账号 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `FriendDBs` | `FriendDB[]?` | Friend 数据列表。 |
| `SentRequestFriendDBs` | `FriendDB[]?` | SentRequestFriend 数据列表。 |
| `ReceivedRequestFriendDBs` | `FriendDB[]?` | ReceivedRequestFriend 数据列表。 |
| `BlockedUserDBs` | `FriendDB[]?` | BlockedUser 数据列表。 |

### Friend_DeclineFriendRequest

- 协议号：`43008`
- 作用：好友：DeclineFriend请求
- RequestClass：`FriendDeclineFriendRequestRequest`
- ResponseClass：`FriendDeclineFriendRequestResponse`
- 状态：SDK 已封装为好友页拒绝申请方法 `client.friend.decline_request(target_account_id, confirm=True)`；默认先校验收到的好友申请列表，本地协议调用测试通过，真实执行会拒绝好友申请。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetAccountId` | `long` | 目标账号 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `FriendDBs` | `FriendDB[]?` | Friend 数据列表。 |
| `SentRequestFriendDBs` | `FriendDB[]?` | SentRequestFriend 数据列表。 |
| `ReceivedRequestFriendDBs` | `FriendDB[]?` | ReceivedRequestFriend 数据列表。 |
| `BlockedUserDBs` | `FriendDB[]?` | BlockedUser 数据列表。 |

### Friend_CancelFriendRequest

- 协议号：`43009`
- 作用：好友：取消Friend请求
- RequestClass：`FriendCancelFriendRequestRequest`
- ResponseClass：`FriendCancelFriendRequestResponse`
- 状态：SDK 已封装为好友页取消申请方法 `client.friend.cancel_request(target_account_id, confirm=True)`；默认先校验已发送的好友申请列表，本地协议调用测试通过，真实执行会取消好友申请。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetAccountId` | `long` | 目标账号 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `FriendDBs` | `FriendDB[]?` | Friend 数据列表。 |
| `SentRequestFriendDBs` | `FriendDB[]?` | SentRequestFriend 数据列表。 |
| `ReceivedRequestFriendDBs` | `FriendDB[]?` | ReceivedRequestFriend 数据列表。 |
| `BlockedUserDBs` | `FriendDB[]?` | BlockedUser 数据列表。 |

### Friend_Check

- 协议号：`43010`
- 作用：好友：检查状态
- RequestClass：`FriendCheckRequest`
- ResponseClass：`FriendCheckResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Friend_ListByIds

- 协议号：`43011`
- 作用：好友：列表ByIds
- RequestClass：`FriendListByIdsRequest`
- ResponseClass：`FriendListByIdsResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetAccountIds` | `long[]?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ListResult` | `FriendDB[]?` | 列表结果。 |

### Friend_Block

- 协议号：`43012`
- 作用：好友：执行 Block 流程
- RequestClass：`FriendBlockRequest`
- ResponseClass：`FriendBlockResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetAccountId` | `long` | 目标账号 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `FriendDBs` | `FriendDB[]?` | Friend 数据列表。 |
| `SentRequestFriendDBs` | `FriendDB[]?` | SentRequestFriend 数据列表。 |
| `ReceivedRequestFriendDBs` | `FriendDB[]?` | ReceivedRequestFriend 数据列表。 |
| `BlockedUserDBs` | `FriendDB[]?` | BlockedUser 数据列表。 |

### Friend_Unblock

- 协议号：`43013`
- 作用：好友：执行 Unblock 流程
- RequestClass：`FriendUnblockRequest`
- ResponseClass：`FriendUnblockResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetAccountId` | `long` | 目标账号 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `FriendDBs` | `FriendDB[]?` | Friend 数据列表。 |
| `SentRequestFriendDBs` | `FriendDB[]?` | SentRequestFriend 数据列表。 |
| `ReceivedRequestFriendDBs` | `FriendDB[]?` | ReceivedRequestFriend 数据列表。 |
| `BlockedUserDBs` | `FriendDB[]?` | BlockedUser 数据列表。 |
