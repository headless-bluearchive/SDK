# MomoTalk 协议

MomoTalk 模块相关协议。

字段结构只作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `MomoTalk_OutLine` | `33000` | 获取 MomoTalk 概览 | `MomoTalkOutLineRequest` | `MomoTalkOutLineResponse` |
| `MomoTalk_MessageList` | `33001` | 获取单个学生的 MomoTalk 消息列表 | `MomoTalkMessageListRequest` | `MomoTalkMessageListResponse` |
| `MomoTalk_Read` | `33002` | 推进/标记已读 MomoTalk 内容 | `MomoTalkReadRequest` | `MomoTalkReadResponse` |
| `MomoTalk_Reply` | `33003` | Reply 流程 |  |  |
| `MomoTalk_FavorSchedule` | `33004` | 完成羁绊剧情并领取奖励 | `MomoTalkFavorScheduleRequest` | `MomoTalkFavorScheduleResponse` |

## MomoTalk_OutLine

- 状态：已封装为 `client.momotalk.outline()` / `client.momotalk.status()`，live 验证通过。
- Request：无字段。

Response：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MomoTalkOutLineDBs` | `List<MomoTalkOutLineDB>?` | MomoTalk 概览列表。 |
| `FavorScheduleRecords` | `Dictionary<long, List<long>>?` | 羁绊剧情完成记录，key 是学生 ID。 |

注意：该协议不直接返回 UI 未读红点数。客户端红点需要结合 `AcademyMessanger` 和 `AcademyFavorSchedule` 主数据计算。SDK 的 `client.momotalk.status()` 会走这条轻量路径，不需要对每个学生逐个调用 `MomoTalk_MessageList`。

`client.momotalk.status()` 额外整理出的主要字段：

| 字段 | 说明 |
| --- | --- |
| `characters[].unread_count` | 当前学生可处理的未读段数。 |
| `characters[].unread_items` | 未读项列表，类型包括 `message`、`choice`、`favor_story`。 |
| `actionable.messages` | 当前需要外部处理的 MomoTalk 项。 |
| `actionable.unread_total_count` | 所有学生未读段数合计。 |
| `exact_unread_count_available` | 本地 Academy 主数据可用时为 `true`。 |

当 `actionable.messages[]` 内存在 `advance_args` 时，可以直接调用 `client.momotalk.advance_dialog(**advance_args)`。当存在 `choice_required=True` 且没有 `advance_args` 时，需要调用方从 `choices` 中选择一个 `chosen_message_id` 后再推进。

## MomoTalk_MessageList

- 状态：已封装为 `client.momotalk.messages(character_db_id)`，live 验证通过。

Request：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterDBId` | `long` | 角色 DB ID。 |

Response：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MomoTalkOutLineDB` | `MomoTalkOutLineDB?` | 当前学生 MomoTalk 概览。 |
| `MomoTalkChoiceDBs` | `List<MomoTalkChoiceDB>?` | 已记录的选择历史。 |

## MomoTalk_Read

- 状态：已封装为 `client.momotalk.read(...)` / `client.momotalk.advance_dialog(...)`，live 验证通过。

Request：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterDBId` | `long` | 角色 DB ID。 |
| `LastReadMessageGroupId` | `long` | 本次推进到的 MessageGroup ID。 |
| `ChosenMessageId` | `Nullable<long>` | 需要选择时传入的选项消息 ID。 |

Response：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MomoTalkOutLineDB` | `MomoTalkOutLineDB?` | 更新后的 MomoTalk 概览。 |
| `MomoTalkChoiceDBs` | `List<MomoTalkChoiceDB>?` | 更新后的选择历史。 |

## MomoTalk_Reply

- 状态：不封装稳定 API。当前 `core/data` 没有 RequestClass/schema；实际对话推进使用 `MomoTalk_Read`。

## MomoTalk_FavorSchedule

- 状态：已封装为 `client.momotalk.complete_favor_schedule(schedule_id)`，live 可领取样本验证通过。已完成 schedule 会返回 `ErrorCode=22004 AcademyAlreadyAttendedFavorSchedule`。

Request：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ScheduleId` | `long` | 羁绊剧情 schedule ID。 |

Response：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `FavorScheduleRecords` | `Dictionary<long, List<long>>?` | 羁绊剧情完成记录。 |
