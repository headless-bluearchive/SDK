# Account 协议

账号与登录模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Account_Create` | `1000` | 账号与登录：创建账号数据 | `AccountCreateRequest` | `AccountCreateResponse` |
| `Account_Nickname` | `1001` | 账号与登录：设置昵称 | `AccountNicknameRequest` | `AccountNicknameResponse` |
| `Account_Auth` | `1002` | 账号与登录：账号认证并进入主网关会话 | `AccountAuthRequest` | `AccountAuthResponse` |
| `Account_CurrencySync` | `1003` | 账号与登录：同步货币数据 | `AccountCurrencySyncRequest` | `AccountCurrencySyncResponse` |
| `Account_SetRepresentCharacterAndComment` | `1004` | 账号与登录：设置代表学生和个人简介 | `AccountSetRepresentCharacterAndCommentRequest` | `AccountSetRepresentCharacterAndCommentResponse` |
| `Account_GetTutorial` | `1005` | 账号与登录：获取教程进度 | `AccountGetTutorialRequest` | `AccountGetTutorialResponse` |
| `Account_SetTutorial` | `1006` | 账号与登录：更新教程进度 | `AccountSetTutorialRequest` | `AccountSetTutorialResponse` |
| `Account_PassCheck` | `1007` | 账号与登录：通行/状态检查 | `AccountPassCheckRequest` | `AccountPassCheckResponse` |
| `Account_VerifyForYostar` | `1008` | 账号与登录：Yostar 登录验证 | `` | `` |
| `Account_CheckYostar` | `1009` | 账号与登录：校验 Yostar 登录态 | `AccountCheckYostarRequest` | `AccountCheckYostarResponse` |
| `Account_CallName` | `1010` | 账号与登录：设置老师称呼 | `AccountCallNameRequest` | `AccountCallNameResponse` |
| `Account_BirthDay` | `1011` | 账号与登录：设置或提交生日信息 | `AccountBirthDayRequest` | `AccountBirthDayResponse` |
| `Account_Auth2` | `1012` | 账号与登录：账号认证备用流程 | `AccountAuth2Request` | `AccountAuth2Response` |
| `Account_LinkReward` | `1013` | 账号与登录：领取账号绑定奖励 | `AccountLinkRewardRequest` | `AccountLinkRewardResponse` |
| `Account_CheckNexon` | `1014` | 账号与登录：校验 Nexon 登录态并下发 1014 会话密钥 | `AccountCheckNexonRequest` | `AccountCheckNexonResponse` |
| `Account_DetachNexon` | `1015` | 账号与登录：解除 Nexon 绑定 | `AccountDetachNexonRequest` | `AccountDetachNexonResponse` |
| `Account_ReportXignCodeCheater` | `1016` | 账号与登录：上报 XignCode 风控结果 | `AccountReportXignCodeCheaterRequest` | `AccountReportXignCodeCheaterResponse` |
| `Account_DismissRepurchasablePopup` | `1017` | 账号与登录：关闭可重复购买弹窗 | `AccountDismissRepurchasablePopupRequest` | `AccountDismissRepurchasablePopupResponse` |
| `Account_InvalidateToken` | `1018` | 账号与登录：使当前登录 token 失效 | `AccountInvalidateTokenRequest` | `AccountInvalidateTokenResponse` |
| `Account_LoginSync` | `1019` | 账号与登录：登录后同步大厅与各模块基础数据 | `AccountLoginSyncRequest` | `AccountLoginSyncResponse` |
| `Account_VerifyCheckAdultAgree` | `1020` | 账号与登录：验证成人确认状态 | `AccountVerifyAdultCheckRequest` | `AccountVerifyAdultCheckResponse` |
| `Account_SetCheckAdultAgree` | `1021` | 账号与登录：设置成人确认同意状态 | `AccountSetAdultCheckRequest` | `AccountSetAdultCheckResponse` |
| `Account_Reset` | `1022` | 账号与登录：重置账号相关状态 | `AccountResetRequest` | `AccountResetResponse` |
| `Account_RequestBirthdayMail` | `1023` | 账号与登录：请求生日邮件 | `AccountRequestBirthdayMailRequest` | `AccountRequestBirthdayMailResponse` |
| `Account_CheckAccountLevelReward` | `1024` | 账号与登录：检查账号等级奖励状态 | `CheckAccountLevelRewardRequest` | `CheckAccountLevelRewardResponse` |
| `Account_ReceiveAccountLevelReward` | `1025` | 账号与登录：领取AccountLevel奖励 | `ReceiveAccountLevelRewardRequest` | `ReceiveAccountLevelRewardResponse` |

## 字段结构参考

### Account_Create

- 协议号：`1000`
- 作用：账号与登录：创建账号数据
- RequestClass：`AccountCreateRequest`
- ResponseClass：`AccountCreateResponse`
- 状态：已封装为 `client.account.currency()`，live 验证通过。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `DevId` | `string?` | 设备 ID。 |
| `Version` | `long` | 客户端版本数值。 |
| `IMEI` | `long` | 设备 IMEI 或兼容占位值。 |
| `AccessIP` | `string?` | 出口 IP。 |
| `MarketId` | `string?` | 市场渠道。 |
| `UserType` | `string?` | 用户类型。 |
| `AdvertisementId` | `string?` | 广告 ID。 |
| `OSType` | `string?` | 系统类型。 |
| `OSVersion` | `string?` | 系统版本。 |
| `CountryCode` | `string?` | 国家或地区代码。 |

#### Response 字段

无字段或未匹配到结构。

### Account_Nickname

- 协议号：`1001`
- 作用：账号与登录：设置昵称
- RequestClass：`AccountNicknameRequest`
- ResponseClass：`AccountNicknameResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Nickname` | `string?` | 昵称。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountDB` | `AccountDB?` | 账号数据。 |

### Account_Auth

- 协议号：`1002`
- 作用：账号与登录：账号认证并进入主网关会话
- RequestClass：`AccountAuthRequest`
- ResponseClass：`AccountAuthResponse`
- 状态：字段结构已接入登录链路，具体字段取值以真实 replay 为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Version` | `long` | 客户端版本数值。 |
| `DevId` | `string?` | 设备 ID。 |
| `IMEI` | `long` | 设备 IMEI 或兼容占位值。 |
| `AccessIP` | `string?` | 出口 IP。 |
| `MarketId` | `string?` | 市场渠道。 |
| `UserType` | `string?` | 用户类型。 |
| `AdvertisementId` | `string?` | 广告 ID。 |
| `OSType` | `string?` | 系统类型。 |
| `OSVersion` | `string?` | 系统版本。 |
| `DeviceUniqueId` | `string?` | 设备唯一 ID。 |
| `DeviceModel` | `string?` | 设备型号。 |
| `DeviceSystemMemorySize` | `int` | 设备内存大小。 |
| `CountryCode` | `string?` | 国家或地区代码。 |
| `Idfv` | `string?` | Vendor ID。 |
| `IsTeenVersion` | `bool` | 是否青少年版本。 |
| `DeviceLocaleCode` | `string?` | 设备语言区域。 |
| `GameOptionLanguage` | `string?` | 游戏语言选项。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CurrentVersion` | `long` | 当前客户端版本。 |
| `MinimumVersion` | `long` | 最低可用客户端版本。 |
| `IsDevelopment` | `bool` | 布尔状态。 |
| `BattleValidation` | `bool` | 战斗校验开关。 |
| `UpdateRequired` | `bool` | 是否需要客户端更新。 |
| `TTSCdnUri` | `string?` | TTS CDN 地址。 |
| `AccountDB` | `AccountDB?` | 账号数据。 |
| `AttendanceBookRewards` | `IEnumerable<AttendanceBookReward>?` | 签到簿奖励。 |
| `AttendanceHistoryDBs` | `IEnumerable<AttendanceHistoryDB>?` | 签到历史数据。 |
| `RepurchasableMonthlyProductCountDBs` | `IEnumerable<PurchaseCountDB>?` | 可重复购买月卡商品次数数据。 |
| `MonthlyProductParcel` | `IEnumerable<ParcelInfo>?` | 月度商品道具奖励。 |
| `MonthlyProductMail` | `IEnumerable<ParcelInfo>?` | 月度商品邮件奖励。 |
| `BiweeklyProductParcel` | `IEnumerable<ParcelInfo>?` | 双周商品道具奖励。 |
| `BiweeklyProductMail` | `IEnumerable<ParcelInfo>?` | 双周商品邮件奖励。 |
| `WeeklyProductParcel` | `IEnumerable<ParcelInfo>?` | 每周商品道具奖励。 |
| `WeeklyProductMail` | `IEnumerable<ParcelInfo>?` | 每周商品邮件奖励。 |
| `EncryptedUID` | `string?` | 加密后的用户 ID。 |
| `AccountRestrictionsDB` | `AccountRestrictionsDB?` | 账号限制状态。 |
| `IssueAlertInfos` | `IEnumerable<IssueAlertInfoDB>?` | 公告或告警信息。 |
| `accountBanByNexonDBs` | `IEnumerable<AccountBanByNexonDB>?` | Nexon 账号封禁信息。 |

SDK 会把 `AttendanceBookRewards` 和 `AttendanceHistoryDBs` 写入登录结果的 Attendance 缓存，供 `client.attendance.status()` 使用。

### Account_CurrencySync

- 协议号：`1003`
- 作用：账号与登录：同步货币数据
- RequestClass：`AccountCurrencySyncRequest`
- ResponseClass：`AccountCurrencySyncResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `ExpiredCurrency` | `Dictionary<CurrencyTypes, long>?` | 已过期货币信息。 |

### Account_SetRepresentCharacterAndComment

- 协议号：`1004`
- 作用：账号与登录：设置代表学生和个人简介
- RequestClass：`AccountSetRepresentCharacterAndCommentRequest`
- ResponseClass：`AccountSetRepresentCharacterAndCommentResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RepresentCharacterServerId` | `long` | 代表角色服务器 ID。 |
| `Comment` | `string?` | 个人简介。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountDB` | `AccountDB?` | 账号数据。 |
| `RepresentCharacterDB` | `CharacterDB?` | 代表角色数据。 |

### Account_GetTutorial

- 协议号：`1005`
- 作用：账号与登录：获取教程进度
- RequestClass：`AccountGetTutorialRequest`
- ResponseClass：`AccountGetTutorialResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TutorialIds` | `List<long>?` | 教程 ID 列表。 |

### Account_SetTutorial

- 协议号：`1006`
- 作用：账号与登录：更新教程进度
- RequestClass：`AccountSetTutorialRequest`
- ResponseClass：`AccountSetTutorialResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TutorialIds` | `long[]?` | 教程 ID 列表。 |

#### Response 字段

无字段或未匹配到结构。

### Account_PassCheck

- 协议号：`1007`
- 作用：账号与登录：通行/状态检查
- RequestClass：`AccountPassCheckRequest`
- ResponseClass：`AccountPassCheckResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `DevId` | `string?` | 设备 ID。 |
| `OnlyAccountId` | `bool` | 是否只返回账号 ID。 |
| `ClientGeneratedKey` | `string?` | 客户端生成 key。 |
| `ClientGeneratedIV` | `string?` | 客户端生成 IV。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EncryptedKey` | `string?` | EncryptedKey。 |
| `SignedKey` | `string?` | SignedKey。 |
| `EncryptedIV` | `string?` | EncryptedIV。 |
| `SignedIV` | `string?` | SignedIV。 |

### Account_VerifyForYostar

- 协议号：`1008`
- 作用：账号与登录：Yostar 登录验证
- RequestClass：``
- ResponseClass：``
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Account_CheckYostar

- 协议号：`1009`
- 作用：账号与登录：校验 Yostar 登录态
- RequestClass：`AccountCheckYostarRequest`
- ResponseClass：`AccountCheckYostarResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `UID` | `long` | 用户 ID。 |
| `YostarToken` | `string?` | Yostar 登录 token。 |
| `EnterTicket` | `string?` | 进入主网关前置票据。 |
| `PassCookieResult` | `bool` | Cookie 通行校验结果。 |
| `Cookie` | `string?` | 登录 Cookie。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ResultState` | `int` | 结果状态。 |
| `ResultMessag` | `string?` | 结果信息。 |
| `Birth` | `string?` | Birth。 |
| `EncryptedKey` | `string?` | EncryptedKey。 |
| `SignedKey` | `string?` | SignedKey。 |
| `EncryptedIV` | `string?` | EncryptedIV。 |
| `SignedIV` | `string?` | SignedIV。 |

### Account_CallName

- 协议号：`1010`
- 作用：账号与登录：设置老师称呼
- RequestClass：`AccountCallNameRequest`
- ResponseClass：`AccountCallNameResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CallName` | `string?` | 老师称呼。 |
| `CallNameKatakana` | `string?` | 片假名老师称呼。 |
| `CallNameKorean` | `string?` | 韩文老师称呼。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountDB` | `AccountDB?` | 账号数据。 |

### Account_BirthDay

- 协议号：`1011`
- 作用：账号与登录：设置或提交生日信息
- RequestClass：`AccountBirthDayRequest`
- ResponseClass：`AccountBirthDayResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `BirthDay` | `DateTime` | 生日。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountDB` | `AccountDB?` | 账号数据。 |

### Account_Auth2

- 协议号：`1012`
- 作用：账号与登录：账号认证备用流程
- RequestClass：`AccountAuth2Request`
- ResponseClass：`AccountAuth2Response`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Account_LinkReward

- 协议号：`1013`
- 作用：账号与登录：领取账号绑定奖励
- RequestClass：`AccountLinkRewardRequest`
- ResponseClass：`AccountLinkRewardResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Account_CheckNexon

- 协议号：`1014`
- 作用：账号与登录：校验 Nexon 登录态并下发 1014 会话密钥
- RequestClass：`AccountCheckNexonRequest`
- ResponseClass：`AccountCheckNexonResponse`
- 状态：字段结构已接入登录链路，具体字段取值以真实 replay 为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `NpSN` | `long` | Nexon publisher account id / guid。 |
| `NpToken` | `string?` | Nexon / TOYSDK token。 |
| `PassCheckNexonServer` | `bool` | Nexon server check 状态。 |
| `EnterTicket` | `string?` | 进入主网关前置票据。 |
| `ClientGeneratedKey` | `string?` | 客户端生成 key。 |
| `ClientGeneratedIV` | `string?` | 客户端生成 IV。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ResultState` | `int` | 结果状态。 |
| `ResultMessage` | `string?` | 结果信息。 |
| `Birth` | `string?` | Birth。 |
| `EncryptedKey` | `string?` | EncryptedKey。 |
| `SignedKey` | `string?` | SignedKey。 |
| `EncryptedIV` | `string?` | EncryptedIV。 |
| `SignedIV` | `string?` | SignedIV。 |
| `SessionKey` | `new SessionKey?` | 主网关会话凭证。 |

### Account_DetachNexon

- 协议号：`1015`
- 作用：账号与登录：解除 Nexon 绑定
- RequestClass：`AccountDetachNexonRequest`
- ResponseClass：`AccountDetachNexonResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ResultState` | `int` | 结果状态。 |
| `ResultMessage` | `string?` | 结果信息。 |

### Account_ReportXignCodeCheater

- 协议号：`1016`
- 作用：账号与登录：上报 XignCode 风控结果
- RequestClass：`AccountReportXignCodeCheaterRequest`
- ResponseClass：`AccountReportXignCodeCheaterResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ErrorCode` | `string?` | 错误码。 |

#### Response 字段

无字段或未匹配到结构。

### Account_DismissRepurchasablePopup

- 协议号：`1017`
- 作用：账号与登录：关闭可重复购买弹窗
- RequestClass：`AccountDismissRepurchasablePopupRequest`
- ResponseClass：`AccountDismissRepurchasablePopupResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ProductIds` | `List<long>?` | 商品 ID 列表。 |

#### Response 字段

无字段或未匹配到结构。

### Account_InvalidateToken

- 协议号：`1018`
- 作用：账号与登录：使当前登录 token 失效
- RequestClass：`AccountInvalidateTokenRequest`
- ResponseClass：`AccountInvalidateTokenResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Account_LoginSync

- 协议号：`1019`
- 作用：账号与登录：登录后同步大厅与各模块基础数据
- RequestClass：`AccountLoginSyncRequest`
- ResponseClass：`AccountLoginSyncResponse`
- 状态：字段结构已接入登录链路，具体字段取值以真实 replay 为准。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SyncProtocols` | `List<Protocol>?` | 登录后需要同步的协议列表。 |
| `SkillCutInOption` | `string?` | 技能 cut-in 选项。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Responses` | `ResponsePacket?` | 聚合响应对象。 |
| `CafeGetInfoResponse` | `CafeGetInfoResponse?` | CafeGetInfoResponse 子响应。 |
| `AccountCurrencySyncResponse` | `AccountCurrencySyncResponse?` | AccountCurrencySyncResponse 子响应。 |
| `CharacterListResponse` | `CharacterListResponse?` | CharacterListResponse 子响应。 |
| `EquipmentItemListResponse` | `EquipmentItemListResponse?` | EquipmentItemListResponse 子响应。 |
| `CharacterGearListResponse` | `CharacterGearListResponse?` | CharacterGearListResponse 子响应。 |
| `ItemListResponse` | `ItemListResponse?` | ItemListResponse 子响应。 |
| `EchelonListResponse` | `EchelonListResponse?` | EchelonListResponse 子响应。 |
| `MemoryLobbyListResponse` | `MemoryLobbyListResponse?` | MemoryLobbyListResponse 子响应。 |
| `CampaignListResponse` | `CampaignListResponse?` | CampaignListResponse 子响应。 |
| `RaidLoginResponse` | `RaidLoginResponse?` | RaidLoginResponse 子响应。 |
| `EliminateRaidLoginResponse` | `EliminateRaidLoginResponse?` | EliminateRaidLoginResponse 子响应。 |
| `CraftInfoListResponse` | `CraftInfoListResponse?` | CraftInfoListResponse 子响应。 |
| `ClanLoginResponse` | `ClanLoginResponse?` | ClanLoginResponse 子响应。 |
| `MomotalkOutlineResponse` | `MomoTalkOutLineResponse?` | MomotalkOutlineResponse 子响应。 |
| `ScenarioListResponse` | `ScenarioListResponse?` | ScenarioListResponse 子响应。 |
| `ShopGachaRecruitListResponse` | `ShopGachaRecruitListResponse?` | ShopGachaRecruitListResponse 子响应。 |
| `TimeAttackDungeonLoginResponse` | `TimeAttackDungeonLoginResponse?` | TimeAttackDungeonLoginResponse 子响应。 |
| `BillingPurchaseListByYostarResponse` | `BillingPurchaseListByYostarResponse` | 充值与购买状态页里的购买列表同步响应。 |
| `EventContentPermanentListResponse` | `EventContentPermanentListResponse?` | EventContentPermanentListResponse 子响应。 |
| `AttachmentGetResponse` | `AttachmentGetResponse?` | AttachmentGetResponse 子响应。 |
| `AttachmentEmblemListResponse` | `AttachmentEmblemListResponse?` | AttachmentEmblemListResponse 子响应。 |
| `ContentSweepMultiSweepPresetListResponse` | `ContentSweepMultiSweepPresetListResponse?` | ContentSweepMultiSweepPresetListResponse 子响应。 |
| `StickerListResponse` | `StickerLoginResponse?` | StickerListResponse 子响应。 |
| `MultiFloorRaidSyncResponse` | `MultiFloorRaidSyncResponse?` | MultiFloorRaidSyncResponse 子响应。 |
| `FriendCount` | `long` | 好友数量。 |
| `FriendCode` | `string?` | 好友码。 |
| `BillingPurchaseListByNexonResponse` | `BillingPurchaseListByNexonResponse?` | 充值与购买状态页里的 Nexon 购买列表同步响应。 |
| `PickupFirstGetHistoryDBs` | `List<PickupFirstGetHistoryDB>?` | Pickup 首次获取历史。 |
| `AccountLevelRewardIds` | `List<long>?` | 账号等级奖励页里已领取的奖励 ID。 |

### Account_VerifyCheckAdultAgree

- 协议号：`1020`
- 作用：账号与登录：验证成人确认状态
- RequestClass：`AccountVerifyAdultCheckRequest`
- ResponseClass：`AccountVerifyAdultCheckResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CheckAdultAgree` | `bool` | 成人确认同意状态。 |

### Account_SetCheckAdultAgree

- 协议号：`1021`
- 作用：账号与登录：设置成人确认同意状态
- RequestClass：`AccountSetAdultCheckRequest`
- ResponseClass：`AccountSetAdultCheckResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CheckAdultAgree` | `bool` | 成人确认同意状态。 |

#### Response 字段

无字段或未匹配到结构。

### Account_Reset

- 协议号：`1022`
- 作用：账号与登录：重置账号相关状态
- RequestClass：`AccountResetRequest`
- ResponseClass：`AccountResetResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `DevId` | `string?` | 设备 ID。 |

#### Response 字段

无字段或未匹配到结构。

### Account_RequestBirthdayMail

- 协议号：`1023`
- 作用：账号与登录：请求生日邮件
- RequestClass：`AccountRequestBirthdayMailRequest`
- ResponseClass：`AccountRequestBirthdayMailResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Birthday` | `DateTime` | 生日日期。 |

#### Response 字段

无字段或未匹配到结构。

### Account_CheckAccountLevelReward

- 协议号：`1024`
- 作用：账号与登录：检查账号等级奖励状态
- RequestClass：`CheckAccountLevelRewardRequest`
- ResponseClass：`CheckAccountLevelRewardResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountLevelRewardIds` | `List<long>?` | 账号等级奖励页里已领取的奖励 ID。 |

### Account_ReceiveAccountLevelReward

- 协议号：`1025`
- 作用：账号与登录：领取AccountLevel奖励
- RequestClass：`ReceiveAccountLevelRewardRequest`
- ResponseClass：`ReceiveAccountLevelRewardResponse`
- 状态：SDK 已封装为账号等级奖励页的领取入口；调用前应先读取状态并显式确认。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ReceivedAccountLevelRewardIds` | `List<long>?` | 本次领取到的账号等级奖励 ID 列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
