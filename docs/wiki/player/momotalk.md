# MomoTalk

MomoTalk 面向外部调用方提供“当前可处理状态”，而不是要求调用方自己先知道学生 ID。用户看到的是红点，服务端给的是当前位置，中间那坨判断 SDK 来做，不要让调用方拿学生 ID 一个个扫。

学生名称主用 `https://blue-archive.io/config/json/students.json`，失败时备用 `https://schaledb.com/data/cn/students.min.json`，并缓存为本地 `id -> name` 映射。缓存只用于展示，不参与封包；如果缓存不存在或拉取失败，SDK 会返回学生 ID。

## 状态

```python
status = await client.momotalk.status()
```

`status()` 默认返回全量拥有学生，并附带 `actionable`。这个接口走轻量路径：读取 `MomoTalk_OutLine`、拥有学生和好感剧情记录，再结合本地 `AcademyMessanger` / `AcademyFavorSchedule` 主数据计算红点；不会对每个学生逐个调用 `MomoTalk_MessageList`。

| 字段 | 说明 |
| --- | --- |
| `characters` | 全量学生 MomoTalk 状态摘要。 |
| `actionable.messages` | 当前可处理的未读消息、选择回复、羁绊剧情入口。 |
| `actionable.unread_total_count` | 根据本地主数据推导出的未读段数合计。 |
| `actionable.favor_stories` | 已精确确认可领取的羁绊剧情。 |
| `actionable.favor_story_candidates` | 按 `AcademyFavorSchedule` 推导出的候选，`verified=True` 才代表当前可领取。 |
| `exact_unread_count_available` | 本地 Academy 主数据可用时为 `True`。 |

学生状态字段：

| 字段 | 说明 |
| --- | --- |
| `character_id` | 学生 ID。 |
| `character_name` | 学生名；名称表没有时退回 ID 字符串。 |
| `character_db_id` | 发 `MomoTalk_MessageList` / `MomoTalk_Read` 需要的角色 DB ID。 |
| `favor_rank` | 当前好感等级。 |
| `has_outline` | 当前学生是否存在服务端 MomoTalk outline。 |
| `latest_message_group_id` | 当前服务端记录的最新消息组。 |
| `chosen_message_id` | 当前 outline 里的选择消息 ID。 |
| `completed_favor_schedule_ids` | 已完成的羁绊剧情 schedule。 |
| `unread_count` | 当前学生可处理的未读段数。 |
| `unread_items` | 未读项列表，类型可能是 `message`、`choice`、`favor_story`。 |
| `favor_story_candidates` | 该学生可能存在的后续 schedule 候选。 |

`MomoTalk_OutLine` 不直接返回游戏 UI 里的未读红点数。逆向客户端流程显示，游戏在 `Account_LoginSync` 后把 `MomotalkOutlineResponse` 和 `FavorScheduleRecords` 同步进本地 `MomotalkInfoComponent`，列表红点通过本地 `GetUnreadMessageCount(serverId)` 计算；`MomoTalk_MessageList` 只在打开某个学生对话时单独请求。SDK 现在复刻这个轻量路径：用 outline 的 `LatestMessageGroupId` 作为当前位置，沿 `AcademyMessanger.next_group_id` 检查后续消息条件，并用 `AcademyFavorSchedule` 判断羁绊剧情是否已达成。

如果需要调试单个或少量学生的消息明细，可以显式调用慢路径：

```python
detail = await client.momotalk.scan_messages(character_ids=[10134, 16019])
```

不要把 `scan_messages()` 当成常规全量状态接口。全量扫描会逐个学生发包，速度慢，并且 live session 下并发过高会触发 `ErrorCode=8 FailedToLockAccount`。

如果学生已拥有但没有出现在 `MomoTalk_OutLineDBs` 里，`status()` 仍会返回该学生，并标记 `has_outline=False`。

## 推进对话

```python
status = await client.momotalk.status()

for item in status["actionable"]["messages"]:
    if item.get("advance_args"):
        result = await client.momotalk.advance_dialog(**item["advance_args"])
    elif item.get("complete_args"):
        result = await client.momotalk.complete_favor_schedule(**item["complete_args"])
    elif item.get("choice_required"):
        print(item["choices"])
```

`advance_args` 代表 SDK 已经能直接推进这一段，包括普通新消息，以及 outline 里已经带 `ChosenMessageId` 的旧选择节点。

`choice_required=True` 代表当前卡在新选择节点，调用方需要先从 `choices` 里选出一个 `chosen_message_id`。如果只有一个选项，也建议由外部显式确认后再调用，避免 SDK 私自替用户选择。

推进或领取剧情后需要重新调用 `status()`，因为游戏客户端也是刷新后进入下一段。

## 羁绊剧情奖励

精确判断“哪些羁绊剧情可领取”需要 `AcademyFavorSchedule` / `AcademyMessanger` 主数据。SDK 已提供官方 TableBundles 下载和解析入口，见 `docs/wiki/base/official-data.md`。主数据可用时，结果会放在：

```python
status["actionable"]["favor_story_candidates"]
status["actionable"]["favor_stories"]
```

单个 schedule 领取：

```python
result = await client.momotalk.complete_favor_schedule(schedule_id)
```

不建议外部自己猜 schedule。调试期如果确认要让 SDK 用候选尝试，可以显式打开：

```python
result = await client.momotalk.claim_available_favor_stories(
    allow_heuristic=True,
    include_errors=True,
)
```

默认不允许启发式批量领取，避免把大量不存在的候选发给服务器。

live 验证中，`16019 时（武装）` 的 `160192 / 160193 / 160195 / 160196` 均可领取成功，`20006 纱绫（便服）` 的 `200063 / 200065 / 200066 / 2000620` 均可领取成功。已完成 schedule 会返回 `ErrorCode=22004 AcademyAlreadyAttendedFavorSchedule`，不存在的 schedule 会返回 `ErrorCode=22001 AcademyScheduleTableNotFound`。
