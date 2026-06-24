# 扫荡

扫荡 = 对**已通关、已解锁扫荡**的关卡跳过战斗、直接消耗资源领取产出。本页覆盖全部扫荡入口，并逐一说明每个形参的取值来源与填法。

- 能做：单关 / 多关扫荡（主线、悬赏通缉、学院交流会、活动），以及总力战、大决战、综合战术考试、部分小游戏的扫荡；维护多扫荡预设与历史。
- 前提：目标关卡/房间在当前账号已通关解锁扫荡；所有写操作需 `confirm=True`，消耗 AP / 扫荡券 / 次数。
- ID 一律从对应模块的 `list()` 读取，不要手填。

## 一、全部扫荡入口

| 方法 | 扫什么 | 关键形参 | confirm |
| --- | --- | --- | :--: |
| `client.sweep.request(content=, stage_id=, count=, event_content_id=0)` | 主线 / 悬赏 / 交流会 / 活动（单关） | `content`(ContentType) + `stage_id` | 是 |
| `client.sweep.multi_sweep(parameters)` | 上述内容的**多关**（一次多个目标） | `parameters`=`[{content_type, stage_id, sweep_count, event_content_id}]` | 是 |
| `client.raid.sweep(unique_id=, sweep_count=)` | 总力战（指定房间） | `unique_id` | 是 |
| `client.eliminate_raid.sweep(unique_id=, sweep_count=)` | 大决战（打过一次即可扫，不进战斗） | `unique_id` | 是 |
| `client.time_attack_dungeon.sweep(sweep_count=)` | 综合战术考试 | 仅 `sweep_count`（无法指定关卡） | 是 |
| `client.mini_game.shooting_sweep(event_content_id=, unique_id=, sweep_count=)` | 射击小游戏 | `event_content_id` + `unique_id` | 是 |
| `client.mini_game.ccg_sweep(event_content_id=, sweep_count=)` | 卡牌对战小游戏 | `event_content_id` | 是 |
| `client.mini_game.table_board_sweep(event_content_id=, preserve_item_effect_unique_ids=)` | 桌游小游戏 | `event_content_id`（+ 可选保留道具效果 id） | 是 |
| `client.sweep.preset_list()` / `skip_history_list()` | 读多扫荡预设 / 扫荡历史 | — | 否 |
| `client.sweep.set_multi_sweep_preset(...)` / `set_multi_sweep_preset_name(...)` / `save_skip_history(...)` | 维护预设 / 历史 | — | 是 |

## 二、单关 vs 多关

- **指定单关**：用 `sweep.request(...)`（内容类）或对应模块的 `sweep(unique_id=...)`，传入你要扫的那一个 `stage_id` / `unique_id`。
- **一次扫多关**：用 `sweep.multi_sweep([...])`，`parameters` 是非空列表，每项指定一个目标。总力战/大决战/小游戏的扫荡是按各自方法逐个调用，或用 `sweep_count` 重复扫同一目标。

## 三、每个形参从哪来、怎么填

| 形参 | 含义 | 来源 / 怎么填 |
| --- | --- | --- |
| `content` / `content_type` | `ContentType` 枚举，标识 `stage_id` 属于哪类内容（必须与关卡匹配） | 整数值见 [参数取值参考 · ContentType](../reference.md)：主线`1`、悬赏`3`、交流会`8`、活动`4`等 |
| `stage_id` | 已通关、可扫荡关卡的 `StageUniqueId` | 取自对应模块 `list()` 的关卡记录（见下「四、各内容的 stage_id」） |
| `event_content_id` | 活动 / 小游戏的活动内容 ID | 普通主线/悬赏/交流会填 `0`；活动与小游戏用 `event.list()` / `event_content.permanent_list()` 里当前开放活动的 ID |
| `unique_id` | 总力战房间 / 大决战 / 射击小游戏的目标唯一 ID | 总力战、大决战：各自 `lobby()` / `complete_list()` / 房间列表里的 `UniqueId`；射击小游戏：`shooting_lobby(event_content_id)` 返回里的对应 id |
| `count` / `sweep_count` | 扫荡次数（必须 > 0） | 调用方自定，受 AP / 扫荡券 / 每日次数限制；先 `account.currency()` 看资源 |
| `preserve_item_effect_unique_ids` | 桌游扫荡时要保留的道具效果 id（可选） | 取自 `table_board_sync(event_content_id)` 返回；不需要则留空 |

> **推荐复用游戏内预设**：`sweep.preset_list()` 返回玩家在游戏内配好的多扫荡预设，本身就是合法的 `{content_type, stage_id}` 组合，可直接喂给 `multi_sweep`，无需自己查 ContentType 枚举。空预设的账号需先在游戏内创建。

## 四、各内容的 stage_id 取自哪里

| 内容 | `content` | `stage_id` 取自 | 判断「已通关」的字段 |
| --- | --- | --- | --- |
| 主线 | `1` | `campaign.list()["stage_history"][].StageUniqueId` | `Star1Flag` |
| 悬赏通缉 | `3` | `week_dungeon.list()["stage_history"][].StageUniqueId` | `IsCleardEver` |
| 学院交流会 | `8` | `school_dungeon.list()["stage_history"][].StageUniqueId` | `Star1Flag` / `IsClearedEver` |
| 活动关卡 | `4` 等 | `event_content` 的关卡读接口里的 `StageUniqueId`（并带 `event_content_id`） | 活动专属 |

三类（主线/悬赏/交流会）填法一致：`list() → stage_history → 取已通关那条的 StageUniqueId`。

## 五、关于「25-1」这种区域-关卡记法

**不能直接传 `"25-1"`，要传 `StageUniqueId`。** 原因：`campaign.list()` 只返回 `StageUniqueId`（如 1-1 是 `1011101`）和 `ChapterUniqueId`，没有 `"25-1"` 这个显示名；显示名 ↔ ID 的对照表在游戏数据（`CampaignStageExcel`）里，SDK 不解析它。所以没有可靠的 `"25-1" → StageUniqueId` 自动转换，请从 `campaign.list()` 取目标关卡的 `StageUniqueId` 后填入。`ChapterUniqueId` 可用来按区域分组筛选你要的那一关。

## 六、示例

单关（主线，从已通关关卡取 `stage_id`）：
```python
campaign = await client.campaign.list()
stage_id = next(s["StageUniqueId"] for s in campaign["stage_history"] if s.get("Star1Flag"))
await client.sweep.request(content=1, stage_id=stage_id, count=1, confirm=True)   # content=1：主线
```

多关（一次扫多个目标）：
```python
await client.sweep.multi_sweep(
    [{"content_type": 1, "stage_id": stage_id, "sweep_count": 1, "event_content_id": 0}],
    confirm=True,
)
```

总力战 / 大决战（按房间 `unique_id` 指定）：
```python
await client.raid.sweep(unique_id=<房间id>, sweep_count=1, confirm=True)
await client.eliminate_raid.sweep(unique_id=<目标id>, sweep_count=1, confirm=True)
```

综合战术考试（无法指定关卡，只给次数）：
```python
await client.time_attack_dungeon.sweep(sweep_count=1, confirm=True)
```

## 七、注意

- 写操作必须显式 `confirm=True`，否则抛 `UnsafeOperationError` 且不发包；`count` / `sweep_count` 必须 > 0。
- 只能扫已通关、已解锁扫荡的关卡/房间；困难图通常需 3 星才解锁扫荡。
- ID 一律从对应 `list()` 读取，不要手填。
- `preset_list` / `skip_history_list` / `request` / `multi_sweep` 返回整理后的 `dict`（业务字段 + 部分 `count` + `extra`）；`set_multi_sweep_preset` / `set_multi_sweep_preset_name` / `save_skip_history` 返回服务端原始负载。
- 逐协议接入状态见仓库根 [`docs/protocols.md`](../../protocols.md)。
