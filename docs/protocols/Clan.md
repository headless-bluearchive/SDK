# Clan 协议

社团模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Clan_Lobby` | `28000` | 社团：获取或进入模块大厅 | `ClanLobbyRequest` | `ClanLobbyResponse` |
| `Clan_Login` | `28001` | 社团：进入模块并同步基础数据 | `ClanLoginRequest` | `ClanLoginResponse` |
| `Clan_Search` | `28002` | 社团：搜索 | `ClanSearchRequest` | `ClanSearchResponse` |
| `Clan_Create` | `28003` | 社团：创建账号数据 | `ClanCreateRequest` | `ClanCreateResponse` |
| `Clan_Member` | `28004` | 社团：成员 | `ClanMemberRequest` | `ClanMemberResponse` |
| `Clan_Applicant` | `28005` | 社团：执行 Applicant 流程 | `ClanApplicantRequest` | `ClanApplicantResponse` |
| `Clan_Join` | `28006` | 社团：加入 | `ClanJoinRequest` | `ClanJoinResponse` |
| `Clan_Quit` | `28007` | 社团：执行 Quit 流程 | `ClanQuitRequest` | `ClanQuitResponse` |
| `Clan_Permit` | `28008` | 社团：执行 Permit 流程 | `ClanPermitRequest` | `ClanPermitResponse` |
| `Clan_Kick` | `28009` | 社团：执行 Kick 流程 | `ClanKickRequest` | `ClanKickResponse` |
| `Clan_Setting` | `28010` | 社团：执行 Setting 流程 | `ClanSettingRequest` | `ClanSettingResponse` |
| `Clan_Confer` | `28011` | 社团：执行 Confer 流程 | `ClanConferRequest` | `ClanConferResponse` |
| `Clan_Dismiss` | `28012` | 社团：解散或关闭 | `ClanDismissRequest` | `ClanDismissResponse` |
| `Clan_AutoJoin` | `28013` | 社团：执行 AutoJoin 流程 | `ClanAutoJoinRequest` | `ClanAutoJoinResponse` |
| `Clan_MemberList` | `28014` | 社团：获取成员列表 | `ClanMemberListRequest` | `ClanMemberListResponse` |
| `Clan_CancelApply` | `28015` | 社团：取消申请 | `ClanCancelApplyRequest` | `ClanCancelApplyResponse` |
| `Clan_MyAssistList` | `28016` | 社团：My助战列表 | `ClanMyAssistListRequest` | `ClanMyAssistListResponse` |
| `Clan_SetAssist` | `28017` | 社团：设置助战 | `ClanSetAssistRequest` | `ClanSetAssistResponse` |
| `Clan_ChatLog` | `28018` | 社团：执行 ChatLog 流程 | `ClanChatLogRequest` | `ClanChatLogResponse` |
| `Clan_Check` | `28019` | 社团：检查状态 | `ClanCheckRequest` | `ClanCheckResponse` |
| `Clan_AllAssistList` | `28020` | 社团：全部助战列表 | `ClanAllAssistListRequest` | `ClanAllAssistListResponse` |

## 字段结构参考

### Clan_Lobby

- 协议号：`28000`
- 作用：社团：获取或进入模块大厅
- RequestClass：`ClanLobbyRequest`
- ResponseClass：`ClanLobbyResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `IrcConfig` | `IrcServerConfig?` | IRC 服务器配置。 |
| `AccountClanDB` | `ClanDB?` | 账号社团数据。 |
| `DefaultExposedClanDBs` | `List<ClanDB>?` | DefaultExposedClan 数据列表。 |
| `AccountClanMemberDB` | `ClanMemberDB?` | 账号社团Member数据。 |
| `ClanMemberDBs` | `List<ClanMemberDB>?` | ClanMember 数据列表。 |

### Clan_Login

- 协议号：`28001`
- 作用：社团：进入模块并同步基础数据
- RequestClass：`ClanLoginRequest`
- ResponseClass：`ClanLoginResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountClanDB` | `ClanDB?` | 账号社团数据。 |
| `AccountClanMemberDB` | `ClanMemberDB?` | 账号社团Member数据。 |
| `ClanAssistSlotDBs` | `List<ClanAssistSlotDB>?` | ClanAssistSlot 数据列表。 |

### Clan_Search

- 协议号：`28002`
- 作用：社团：搜索
- RequestClass：`ClanSearchRequest`
- ResponseClass：`ClanSearchResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SearchString` | `string?` | 搜索文本。 |
| `ClanJoinOption` | `ClanJoinOption` | 社团Join选项选项。 |
| `ClanUniqueCode` | `string?` | 社团唯一代码。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanDBs` | `List<ClanDB>?` | Clan 数据列表。 |

### Clan_Create

- 协议号：`28003`
- 作用：社团：创建账号数据
- RequestClass：`ClanCreateRequest`
- ResponseClass：`ClanCreateResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanNickName` | `string?` | 社团昵称。 |
| `ClanJoinOption` | `ClanJoinOption` | 社团Join选项选项。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanDB` | `ClanDB?` | 社团数据。 |
| `ClanMemberDB` | `ClanMemberDB?` | 社团Member数据。 |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |

### Clan_Member

- 协议号：`28004`
- 作用：社团：成员
- RequestClass：`ClanMemberRequest`
- ResponseClass：`ClanMemberResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanDBId` | `long` | 社团DB ID。 |
| `MemberAccountId` | `long` | 成员账号 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanDB` | `ClanDB?` | 社团数据。 |
| `ClanMemberDB` | `ClanMemberDB?` | 社团Member数据。 |
| `DetailedAccountInfoDB` | `DetailedAccountInfoDB?` | Detailed账号信息数据。 |

### Clan_Applicant

- 协议号：`28005`
- 作用：社团：执行 Applicant 流程
- RequestClass：`ClanApplicantRequest`
- ResponseClass：`ClanApplicantResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `OffSet` | `long` | 分页偏移量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanMemberDBs` | `List<ClanMemberDB>?` | ClanMember 数据列表。 |

### Clan_Join

- 协议号：`28006`
- 作用：社团：加入
- RequestClass：`ClanJoinRequest`
- ResponseClass：`ClanJoinResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanDBId` | `long` | 社团DB ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `IrcConfig` | `IrcServerConfig?` | IRC 服务器配置。 |
| `ClanDB` | `ClanDB?` | 社团数据。 |
| `ClanMemberDB` | `ClanMemberDB?` | 社团Member数据。 |

### Clan_Quit

- 协议号：`28007`
- 作用：社团：执行 Quit 流程
- RequestClass：`ClanQuitRequest`
- ResponseClass：`ClanQuitResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Clan_Permit

- 协议号：`28008`
- 作用：社团：执行 Permit 流程
- RequestClass：`ClanPermitRequest`
- ResponseClass：`ClanPermitResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ApplicantAccountId` | `long` | 申请人账号 ID。 |
| `IsPerMit` | `bool` | 布尔状态。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanDB` | `ClanDB?` | 社团数据。 |
| `ClanMemberDB` | `ClanMemberDB?` | 社团Member数据。 |

### Clan_Kick

- 协议号：`28009`
- 作用：社团：执行 Kick 流程
- RequestClass：`ClanKickRequest`
- ResponseClass：`ClanKickResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MemberAccountId` | `long` | 成员账号 ID。 |

#### Response 字段

无字段或未匹配到结构。

### Clan_Setting

- 协议号：`28010`
- 作用：社团：执行 Setting 流程
- RequestClass：`ClanSettingRequest`
- ResponseClass：`ClanSettingResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ChangedClanName` | `string?` | 变更后的社团名称。 |
| `ChangedNotice` | `string?` | 变更后的公告。 |
| `ClanJoinOption` | `ClanJoinOption` | 社团Join选项选项。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanDB` | `ClanDB?` | 社团数据。 |

### Clan_Confer

- 协议号：`28011`
- 作用：社团：执行 Confer 流程
- RequestClass：`ClanConferRequest`
- ResponseClass：`ClanConferResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MemberAccountId` | `long` | 成员账号 ID。 |
| `ConferingGrade` | `ClanSocialGrade` | 授予的社团权限等级。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanMemberDB` | `ClanMemberDB?` | 社团Member数据。 |
| `AccountClanMemberDB` | `ClanMemberDB?` | 账号社团Member数据。 |
| `ClanDB` | `ClanDB?` | 社团数据。 |
| `ClanMemberDescriptionDB` | `ClanMemberDescriptionDB?` | 社团MemberDescription数据。 |

### Clan_Dismiss

- 协议号：`28012`
- 作用：社团：解散或关闭
- RequestClass：`ClanDismissRequest`
- ResponseClass：`ClanDismissResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Clan_AutoJoin

- 协议号：`28013`
- 作用：社团：执行 AutoJoin 流程
- RequestClass：`ClanAutoJoinRequest`
- ResponseClass：`ClanAutoJoinResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `IrcConfig` | `IrcServerConfig?` | IRC 服务器配置。 |
| `ClanDB` | `ClanDB?` | 社团数据。 |
| `ClanMemberDB` | `ClanMemberDB?` | 社团Member数据。 |

### Clan_MemberList

- 协议号：`28014`
- 作用：社团：获取成员列表
- RequestClass：`ClanMemberListRequest`
- ResponseClass：`ClanMemberListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanDBId` | `long` | 社团DB ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanDB` | `ClanDB?` | 社团数据。 |
| `ClanMemberDBs` | `List<ClanMemberDB>?` | ClanMember 数据列表。 |

### Clan_CancelApply

- 协议号：`28015`
- 作用：社团：取消申请
- RequestClass：`ClanCancelApplyRequest`
- ResponseClass：`ClanCancelApplyResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Clan_MyAssistList

- 协议号：`28016`
- 作用：社团：My助战列表
- RequestClass：`ClanMyAssistListRequest`
- ResponseClass：`ClanMyAssistListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanAssistSlotDBs` | `List<ClanAssistSlotDB>?` | ClanAssistSlot 数据列表。 |

### Clan_SetAssist

- 协议号：`28017`
- 作用：社团：设置助战
- RequestClass：`ClanSetAssistRequest`
- ResponseClass：`ClanSetAssistResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EchelonType` | `EchelonType` | 编队类型。 |
| `SlotNumber` | `int` | 槽位编号。 |
| `CharacterDBId` | `long` | 角色DB ID。 |
| `CombatStyleIndex` | `int` | CombatStyle索引索引。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanAssistSlotDB` | `ClanAssistSlotDB?` | 社团Assist槽位数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `RewardInfo` | `ClanAssistRewardInfo?` | 奖励信息奖励信息。 |

### Clan_ChatLog

- 协议号：`28018`
- 作用：社团：执行 ChatLog 流程
- RequestClass：`ClanChatLogRequest`
- ResponseClass：`ClanChatLogResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Channel` | `string?` | 频道。 |
| `FromDate` | `DateTime` | 起始日期。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClanChatLog` | `string?` | 社团聊天记录。 |

### Clan_Check

- 协议号：`28019`
- 作用：社团：检查状态
- RequestClass：`ClanCheckRequest`
- ResponseClass：`ClanCheckResponse`
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Clan_AllAssistList

- 协议号：`28020`
- 作用：社团：全部助战列表
- RequestClass：`ClanAllAssistListRequest`
- ResponseClass：`ClanAllAssistListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EchelonType` | `EchelonType` | 编队类型。 |
| `PendingAssistUseInfo` | `List<ClanAssistUseInfo>?` | PendingAssistUse信息数据列表。 |
| `IsPractice` | `bool` | 布尔状态。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AssistCharacterDBs` | `List<AssistCharacterDB>?` | AssistCharacter 数据列表。 |
| `AssistCharacterRentHistoryDBs` | `List<ClanAssistRentHistoryDB>?` | AssistCharacterRentHistory 数据列表。 |
| `ClanDBId` | `long` | 社团DB ID。 |
