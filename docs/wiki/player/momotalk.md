# MomoTalk

这一页对应游戏里的 MomoTalk：学生消息红点、对话列表、回复选择、羁绊剧情入口和羁绊剧情奖励。SDK 的目标是让调用方拿到“游戏 UI 上现在有哪些可处理项”，而不是要求调用方自己拿学生 ID 一个个试。

学生名称主用 `https://blue-archive.io/config/json/students.json`，失败时备用 `https://schaledb.com/data/cn/students.min.json`。名称缓存只用于展示，不参与发包；如果缓存不存在或拉取失败，SDK 会返回学生 ID。

## MomoTalk 红点状态

对应游戏 MomoTalk 列表页：哪些学生有新消息、哪些对话卡在选择回复、哪些羁绊剧情可领取。

```python
status = await client.momotalk.status()
```

默认返回全量拥有学生，并附带 `actionable`。这个方法走轻量路径：读取 `MomoTalk_OutLine`、拥有学生和好感剧情记录，再结合本地 `AcademyMessanger` / `AcademyFavorSchedule` 主数据计算红点；不会对每个学生逐个打开消息详情。

返回结构：

```python
{
    "characters": [...],  # 每个拥有学生的 MomoTalk 摘要
    "actionable": {
        "messages": [...],                 # 当前可处理消息/选择/剧情入口
        "unread_total_count": 0,           # 推导出的未读段数合计
        "favor_stories": [...],            # 已精确确认可领取的羁绊剧情
        "favor_story_candidates": [...],   # 候选羁绊剧情，verified=True 才代表当前可领取
    },
    "exact_unread_count_available": True,
}
```

学生摘要常见字段：

```python
{
    "character_id": 10134,
    "character_name": "学生名",
    "character_db_id": 123456,
    "favor_rank": 10,
    "has_outline": True,
    "latest_message_group_id": 100000,
    "chosen_message_id": 0,
    "completed_favor_schedule_ids": [...],
    "unread_count": 1,
    "unread_items": [...],
    "favor_story_candidates": [...],
}
```

常见用法：

```python
status = await client.momotalk.status()
for item in status["actionable"]["messages"]:
    print(item["character_name"], item["type"])
```

## 查看少量学生的消息详情

对应游戏里点进某个学生的 MomoTalk 对话。这个路径会逐个学生请求消息明细，适合调试或处理少量学生，不适合作为全量轮询。

```python
detail = await client.momotalk.scan_messages(character_ids=[10134, 16019])
```

不要把 `scan_messages()` 当常规全量刷新。全量扫描会发很多请求，live session 下并发过高可能触发 `ErrorCode=8 FailedToLockAccount`。

## 推进对话

对应游戏里阅读下一段消息、点击已经选择好的回复，或领取羁绊剧情入口。

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

`choice_required=True` 代表当前卡在新选择节点，调用方需要让用户从 `choices` 中选择 `chosen_message_id`。即使只有一个选项，也建议由外部显式确认后再调用，避免 SDK 私自替用户选择。

推进或领取剧情后需要重新调用 `status()`，因为游戏客户端也是刷新后进入下一段。

## 羁绊剧情奖励

对应游戏里学生 MomoTalk 触发的羁绊剧情奖励。精确判断“哪些羁绊剧情可领取”需要 `AcademyFavorSchedule` / `AcademyMessanger` 主数据。官方 TableBundles 准备方式见 [官方资源数据](../base/official-data.md)。

主数据可用时，结果会放在：

```python
status["actionable"]["favor_story_candidates"]
status["actionable"]["favor_stories"]
```

领取单个 schedule：

```python
result = await client.momotalk.complete_favor_schedule(schedule_id)
```

不建议调用方自己猜 schedule。调试期如果确认要让 SDK 用候选尝试，可以显式打开：

```python
result = await client.momotalk.claim_available_favor_stories(
    allow_heuristic=True,
    include_errors=True,
)
```

默认不允许启发式批量领取，避免把大量不存在的候选发给服务器。

live 验证中，`16019 时（武装）` 的 `160192 / 160193 / 160195 / 160196` 均可领取成功，`20006 纱绫（便服）` 的 `200063 / 200065 / 200066 / 2000620` 均可领取成功。已完成 schedule 会返回 `ErrorCode=22004 AcademyAlreadyAttendedFavorSchedule`，不存在的 schedule 会返回 `ErrorCode=22001 AcademyScheduleTableNotFound`。
