# MomoTalk

对应游戏里的 MomoTalk：学生消息红点、对话列表、回复选择、羁绊剧情入口和奖励。能看哪些学生有新消息、哪些对话卡在选择回复、哪些羁绊剧情可领取；能做的是推进对话、点选已经选好的回复、领取羁绊剧情奖励。调用方应通过 `status()` 的 `actionable` 获取当前可处理项，而不是自行遍历学生 ID 逐个尝试。

学生名称缓存来自 `https://blue-archive.io/config/json/students.json`（失败时备用 `https://schaledb.com/data/cn/students.min.json`），只用于展示、不参与发包；缓存缺失或拉取失败时返回学生 ID。精确判断未读 / 可领羁绊剧情还需要 `AcademyMessanger` / `AcademyFavorSchedule` 主数据（准备方式见 [官方资源数据](../base/official-data.md)），缺失时退化为启发式候选。

## SDK 入口

所有方法均为异步方法。

| 方法 | 用途 | 类型 |
| --- | --- | --- |
| `status(character_ids=…, include_message_details=False, include_owned_without_outline=True)` | 轻量算红点：每个拥有学生的 MomoTalk 摘要 + `actionable` | 只读 |
| `unread_candidates(character_ids=…, include_message_details=False)` | 只取 `actionable` 里可处理的消息项 | 只读 |
| `outline()` | 读 MomoTalk 列表大纲与好感剧情记录 | 只读 |
| `messages(character_db_id)` | 读单个学生的消息明细 | 只读 |
| `scan_messages(character_ids=…, …)` | 逐学生拉消息明细（调试 / 少量用，勿全量轮询） | 只读（重） |
| `refresh_student_names()` | 刷新本地学生名缓存 | 只读（本地） |
| `read(character_db_id, last_read_message_group_id, chosen_message_id=…)` | 推进 / 已读对话，可带已选回复 | 写 |
| `advance_dialog(…)` | `read(…)` 的别名 | 写 |
| `favor_schedule(schedule_id, refresh=True)` | 领取单个羁绊剧情奖励 | 写 |
| `complete_favor_schedule(schedule_id, refresh=True)` | `favor_schedule(…)` 的别名 | 写 |
| `claim_available_favor_stories(allow_heuristic=False, include_errors=False, character_ids=…)` | 批量领取已确认可领的羁绊剧情 | 写 |

`status()` 走轻量路径：读取大纲、拥有学生和好感剧情记录，再结合本地 Academy 主数据计算红点，不会对每个学生逐个打开消息详情。`actionable` 里把可处理项整理成 `messages`，并区分能直接推进的（带 `advance_args`）、卡在选择的（`choice_required=True` + `choices`）、可领羁绊剧情的（带 `complete_args`）。

```python
status = await client.momotalk.status()

for item in status["actionable"]["messages"]:
    if item.get("advance_args"):
        await client.momotalk.advance_dialog(**item["advance_args"])
    elif item.get("complete_args"):
        await client.momotalk.complete_favor_schedule(**item["complete_args"])
    elif item.get("choice_required"):
        print(item["choices"])  # 由外部确认 chosen_message_id 后再 advance_dialog
```

推进或领取后需要重新调用 `status()`，游戏客户端也是刷新后才进入下一段。

## 返回说明

- 只读方法返回整理后的 dict：`status` / `unread_candidates` 给学生摘要 / 可处理项列表 + `count` + `actionable`（`messages` / `unread_total_count` / `favor_stories` / `favor_story_candidates` 等），并带 `exact_unread_count_available` 标记主数据是否就绪；`outline` / `messages` 经 `format_*` 整理（大纲列表与好感记录 / `choices`、`can_read_next` 等），均含 `extra`。
- 写方法（`read` / `advance_dialog`、`favor_schedule` / `complete_favor_schedule`、`claim_available_favor_stories`）也返回整理后的 dict，并附 `needs_refresh` / `next_step` 提示，指明下一步该重新 `status()` / `outline()`。

具体键名以服务端返回和主数据为准，这里只描述形状。

## 注意

- MomoTalk 的写操作不走 `confirm=True` 守卫，但应由 `status()` 的 `actionable` 数据驱动：直接 `advance_dialog(**advance_args)` 或 `complete_favor_schedule(**complete_args)`，不要自己猜 `character_db_id` / `last_read_message_group_id` / `schedule_id`。
- `choice_required=True` 表示卡在新选择节点：即便只有一个选项，也应由外部显式确认 `chosen_message_id` 后再调用，SDK 不替用户选择。
- `claim_available_favor_stories` 默认 `allow_heuristic=False`：主数据不可用时不会用猜测候选批量发请求（否则抛 `UnsafeOperationError`），避免把大量不存在的 schedule 发给服务器。已完成的 schedule 服务端返回 `ErrorCode=22004 AcademyAlreadyAttendedFavorSchedule`，不存在的返回 `ErrorCode=22001 AcademyScheduleTableNotFound`。
- `scan_messages()` 不要当常规全量刷新：全量扫描会发很多请求，live session 下并发过高可能触发 `ErrorCode=8 FailedToLockAccount`。

---

逐协议接入状态见 [协议总表](../../protocols.md)。
