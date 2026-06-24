# 好友、社团、活动、Raid、贴纸等扩展只读

按游戏里能打开的页面整理 SDK 的只读方法：老师资料/仓库/编队、活动与活动商店、招募页状态、好友、社团、总力战/大决战/常驻/多层/世界 Raid、活动小游戏、占领战、战斗通行证、制造、公告，以及贴纸、红点、语音、服务器时间等握手类同步。

这一页都是“打开页面看状态”，不会领奖、购买、进入战斗、提交成绩、抽卡、发送好友申请、加入社团或选择票券。账号资源和教程见 [账号资源页](game-account.md)；学生/主线/扫荡见 [通用只读页](game-readonly.md)。

调用前需要先完成 `client.login(...)`，或用已持久化的 `session/profile` 调用 `client.restore_session(...)`。

## 阅读方式

每个小节先说明它对应游戏里哪个页面，再给出方法表。所有方法都是 `async`，返回 `dict`。返回分两种形状，本页在每个方法的“返回”列标注：

- **整理后的 dict**：方法源码里有对应的 `format_*`，返回 `{业务字段..., count（列表类）, extra}`。列表里的单条记录通常仍是服务端原始 DB dict。
- **原始负载**：只读握手/检查/同步类方法直接返回服务端模块响应（PascalCase 键），SDK 没做字段整理。

本页只描述返回形状，不逐一列出键名（键名可能随服务端数据变化）。`extra` 用于存放服务端附带、SDK 尚未单独整理的顶层字段（如 `ServerTime`、版本、活动期信息），不是错误。

参数里写成 `int` 的会经过整数校验，写成 `list[int]` 的会逐项转整数。涉及活动、赛季、招募、社团、好友、Raid 房间的 ID，必须来自当前账号能看到的页面数据或游戏数据配置，不能硬填。

这些页面里的写操作（领奖、装配、购买、社团管理等）全部需要 `confirm=True`，放在 [显式确认变更页面](state-changing.md)。逐协议接入状态见仓库根 [`docs/protocols.md`](../../protocols.md)。

## 老师资料、仓库和编队

对应资料页装饰、装备仓库、道具仓库、爱用品、编队、记忆大厅、剧情回放、学院交流会，以及客户端版本/Toast。

| 方法 | 游戏里对应 | 参数 | 返回 |
| --- | --- | --- | --- |
| `client.attachment.get()` | 资料页头像框/称号挂载状态 | 无 | 整理后的 dict |
| `client.attachment.emblem_list()` | 可选 Emblem 列表 | 无 | 整理后的 dict |
| `client.character_gear.list()` | 学生爱用品记录 | 无 | 整理后的 dict |
| `client.equipment.list()` | 装备仓库 | 无 | 整理后的 dict |
| `client.item.list()` | 道具仓库（普通/限时/装备/爱用品一次返回） | 无 | 整理后的 dict |
| `client.echelon.list()` | 编队和预设编队 | 无 | 整理后的 dict |
| `client.echelon.preset_list(...)` | 预设编队组列表 | `echelon_extension_type: int \| None` | 整理后的 dict |
| `client.memory_lobby.list()` | 记忆大厅设置页 | 无 | 整理后的 dict |
| `client.scenario.list()` | 剧情回放/故事收藏 | 无 | 整理后的 dict |
| `client.school_dungeon.list()` | 学院交流会 | 无 | 整理后的 dict |
| `client.system.version()` | 客户端版本检查 | 无 | 整理后的 dict |
| `client.toast.list()` | 服务端下发的轻量提示 | 无 | 整理后的 dict |

```python
items = await client.item.list()
print(items["count"], items["expiry_count"])

echelons = await client.echelon.list()
preset_groups = await client.echelon.preset_list()
```

`school_dungeon.list()` 在未开放该功能的账号上会返回 `OpenConditionClosed`，属账号状态而非接口缺陷。装饰的装配（`attachment.emblem_acquire/emblem_attach`）和编队保存（`echelon.save/preset_save/...`）是写操作，见 [显式确认变更页面](state-changing.md)。

## 活动页、活动关卡和活动商店

对应活动入口、活动 Banner、永久化活动、活动关卡、活动商店、箱式商店、活动收藏、DiceRace、Treasure、ClueSearch 等。除 `event.list()` 外，下列活动内容方法都需要 `event_content_id`。

### 活动内容 ID 怎么取

`event_content_id` 必须来自当前账号可见、当前开放或永久化且类型匹配的活动内容，不要硬填。类型不匹配时服务端会返回 `DataEntityNotFound`、`DataClassNotFound` 或玩法专属错误。常见取法：

```python
permanent = await client.event_content.permanent_list()
event_content_id = permanent["permanent"][0]["EventContentId"]
```

| 方法 | 游戏里对应 | 参数 | 返回 |
| --- | --- | --- | --- |
| `client.event.list()` | 活动入口/活动列表 | 无 | 整理后的 dict |
| `client.event.image(event_id)` | 活动 Banner/图片资源 | `event_id: int` | 整理后的 dict |
| `client.event_content.permanent_list()` | 常驻化/永久化活动列表 | 无 | 整理后的 dict |
| `client.event_content.adventure_list(event_content_id)` | 活动关卡页（历史/奖励/活动点数） | `event_content_id: int` | 整理后的 dict |
| `client.event_content.shop_list(event_content_id, category_list=None)` | 活动商店货架和兑换历史 | `event_content_id: int`, `category_list: list[int] \| None` | 整理后的 dict |
| `client.event_content.box_gacha_shop_list(event_content_id)` | 箱式商店/Box Gacha 状态 | `event_content_id: int` | 整理后的 dict |
| `client.event_content.collection_list(event_content_id, group_id=None)` | 活动收藏/CG 回收 | `event_content_id: int`, `group_id: int \| None` | 整理后的 dict |
| `client.event_content.collection_for_mission(event_content_id)` | 活动任务里的收藏类进度 | `event_content_id: int` | 整理后的 dict |
| `client.event_content.location_get_info(event_content_id)` | Location 类活动页 | `event_content_id: int` | 整理后的 dict |
| `client.event_content.sub_event_lobby(event_content_id)` | SubEvent 子活动大厅 | `event_content_id: int` | 整理后的 dict |
| `client.event_content.dice_race_lobby(event_content_id)` | DiceRace 骰子赛跑页 | `event_content_id: int` | 整理后的 dict |
| `client.event_content.treasure_lobby(event_content_id)` | Treasure 寻宝/翻图页 | `event_content_id: int` | 整理后的 dict |
| `client.event_content.clue_search_get_info(event_content_id)` | ClueSearch 线索搜索页 | `event_content_id: int` | 整理后的 dict |

```python
adventure = await client.event_content.adventure_list(event_content_id)
shops = await client.event_content.shop_list(event_content_id, category_list=[1, 2])
```

活动商店的购买/刷新、活动关卡奖励领取、DiceRace 转动等都是写操作，见 [显式确认变更页面](state-changing.md)。

## 招募页面状态

对应招募页面、预抽卡页面和自选 Pickup 状态，只读列表和状态，不购买、不抽卡、不保存结果。商店购买/AP 补充见 [商店页面](shop.md)。

| 方法 | 游戏里对应 | 参数 | 返回 |
| --- | --- | --- | --- |
| `client.shop.gacha_recruit_list()` | 招募列表（开放卡池/免费招募历史/货币摘要） | 无 | 整理后的 dict |
| `client.shop.beforehand_gacha_get()` | 预抽卡/Beforehand Gacha 状态 | 无 | 整理后的 dict |
| `client.shop.pickup_selection_gacha_get(shop_recruit_id)` | 自选 Pickup 招募状态 | `shop_recruit_id: int` | 整理后的 dict |

```python
recruits = await client.shop.gacha_recruit_list()
shop_recruit_id = recruits["shop_recruits"][0]["ShopRecruitId"]
state = await client.shop.pickup_selection_gacha_get(shop_recruit_id)
```

## 好友页和玩家名片

对应好友页、好友搜索、玩家详情和自己的名片。这里只查看；好友申请的发送/接受/拒绝/取消是写操作，见 [显式确认变更页面](state-changing.md)。

| 方法 | 游戏里对应 | 参数 | 返回 |
| --- | --- | --- | --- |
| `client.friend.list()` | 好友/收发申请/屏蔽/名片背景 | 无 | 整理后的 dict |
| `client.friend.detailed_info(friend_account_id)` | 玩家详情页 | `friend_account_id: int` | 整理后的 dict |
| `client.friend.id_card()` | 自己的好友名片 | 无 | 整理后的 dict |
| `client.friend.search(friend_code=None, level_option=None)` | 好友搜索 | `friend_code: str \| None`, `level_option: int \| None` | 整理后的 dict |
| `client.friend.list_by_ids(target_account_ids)` | 已持有账号 ID 时批量查玩家 | `target_account_ids: list[int]`（非空） | 整理后的 dict |
| `client.friend.check()` | 好友红点/状态检查 | 无 | 原始负载 |

```python
friends = await client.friend.list()
info = await client.friend.detailed_info(friends["friends"][0]["AccountId"])
```

## 社团页和社团助战

对应社团大厅、搜索、成员列表和助战页。这里只查看；申请加入/退出/解散/管理是写操作，见 [显式确认变更页面](state-changing.md)。

| 方法 | 游戏里对应 | 参数 | 返回 |
| --- | --- | --- | --- |
| `client.clan.lobby()` | 社团大厅（社团/成员/IRC 配置） | 无 | 整理后的 dict |
| `client.clan.login()` | 社团模块登录同步 | 无 | 整理后的 dict |
| `client.clan.search(...)` | 社团搜索 | `clan_join_option: int \| None`, `clan_unique_code: str \| None`, `search_string: str \| None` | 整理后的 dict |
| `client.clan.member(clan_db_id, member_account_id)` | 社团成员详情 | `clan_db_id: int`, `member_account_id: int` | 整理后的 dict |
| `client.clan.member_list(clan_db_id)` | 社团成员列表 | `clan_db_id: int` | 整理后的 dict |
| `client.clan.my_assist_list()` | 自己的助战设置 | 无 | 整理后的 dict |
| `client.clan.all_assist_list(...)` | 助战选择页（可用助战/租借历史） | `echelon_type: int`（必填）, `is_practice: bool=False`, `pending_assist_use_info: list[dict] \| None` | 整理后的 dict |
| `client.clan.check()` | 社团红点/状态检查 | 无 | 原始负载 |
| `client.clan.applicant(offset=None)` | 入团申请者列表（需在社团内且有权限） | `offset: int \| None` | 原始负载 |
| `client.clan.chat_log(channel=None, from_date=None)` | 社团聊天记录（需在社团内） | `channel: str \| None`, `from_date: str \| None` | 原始负载 |

```python
lobby = await client.clan.lobby()
members = await client.clan.member_list(lobby["account_clan"]["ServerId"])
```

## 总力战、大决战、常驻、多层和世界 Raid

对应总力战/大决战大厅、房间列表、排行榜、最佳队伍、常驻 Raid、多层总力战和 WorldRaid。这里只看大厅、排行和队伍数据，不进入战斗、不提交成绩、不领奖（领奖见 [显式确认变更页面](state-changing.md)）。

| 方法 | 游戏里对应 | 参数 | 返回 |
| --- | --- | --- | --- |
| `client.raid.list(...)` | 总力战房间列表 | `raid_boss_group: str \| None`, `raid_difficulty: int \| None`, `raid_room_sort_option: int \| None` | 整理后的 dict |
| `client.raid.complete_list()` | 已完成 Raid 记录和赛季摘要 | 无 | 整理后的 dict |
| `client.raid.search(secret_code=None, tags=None)` | 按房间码/标签搜索房间 | `secret_code: str \| None`, `tags: list[str] \| None` | 整理后的 dict |
| `client.raid.lobby()` | 总力战大厅 | 无 | 整理后的 dict |
| `client.raid.detail(raid_server_id, raid_unique_id)` | 房间详情 | `raid_server_id: int`, `raid_unique_id: int` | 原始负载 |
| `client.raid.login()` | Raid 模块登录 | 无 | 原始负载 |
| `client.raid.opponent_list(...)` | 排行榜邻近玩家 | `is_first_request/is_upper: bool \| None`, `rank/score/search_type: int \| None` | 整理后的 dict |
| `client.raid.get_best_team(search_account_id)` | 查看某玩家最佳队伍 | `search_account_id: int` | 整理后的 dict |
| `client.raid.ranking_index()` | 排行榜分段索引 | 无 | 整理后的 dict |
| `client.eliminate_raid.lobby()` | 制约解除决战大厅 | 无 | 整理后的 dict |
| `client.eliminate_raid.login()` | 大决战模块登录 | 无 | 原始负载 |
| `client.eliminate_raid.opponent_list(...)` | 大决战排行榜邻近玩家 | `boss_group_index: int \| None` 等 | 整理后的 dict |
| `client.eliminate_raid.get_best_team(search_account_id)` | 大决战某玩家最佳队伍 | `search_account_id: int` | 整理后的 dict |
| `client.eliminate_raid.ranking_index()` | 大决战排行榜分段索引 | 无 | 整理后的 dict |
| `client.permanent_raid.lobby()` | 常驻 Raid 大厅和赛季列表 | 无 | 整理后的 dict |
| `client.world_raid.lobby(content_type, season_id)` | WorldRaid 大厅 | `content_type: int`, `season_id: int` | 整理后的 dict |
| `client.world_raid.boss_list(content_type, season_id, request_only_world_boss_data=False)` | WorldRaid Boss 列表 | `content_type: int`, `season_id: int`, `request_only_world_boss_data: bool` | 整理后的 dict |
| `client.multi_floor_raid.login()` | 多层总力战登录 | 无 | 原始负载 |
| `client.multi_floor_raid.sync(season_id)` | 多层总力战同步 | `season_id: int` | 原始负载 |

```python
raids = await client.raid.list()
opponents = await client.raid.opponent_list(is_first_request=True, is_upper=False, rank=0, score=0, search_type=0)
```

WorldRaid 和多层总力战需要当前开放的 `content_type`/`season_id`，没有候选参数时无法调用。

## 战斗通行证、咖啡厅、占领战、制造、公告和任务

| 方法 | 游戏里对应 | 参数 | 返回 |
| --- | --- | --- | --- |
| `client.battle_pass.get_info(battle_pass_id)` | 战斗通行证赛季总览 | `battle_pass_id: int` | 整理后的 dict |
| `client.battle_pass.mission_list(battle_pass_id)` | 战斗通行证任务页 | `battle_pass_id: int` | 整理后的 dict |
| `client.battle_pass.check(battle_pass_id)` | 战斗通行证领取状态 | `battle_pass_id: int` | 整理后的 dict |
| `client.cafe.trophy_history()` | 咖啡厅奖杯历史 | 无 | 整理后的 dict |
| `client.cafe.list_preset()` | 咖啡厅预设列表 | 无 | 原始负载 |
| `client.cafe.preset_detail(preset_type, slot_id)` | 咖啡厅预设详情 | `preset_type: int`, `slot_id: int` | 原始负载 |
| `client.conquest.get_info(event_content_id)` | 占领战活动页 | `event_content_id: int` | 整理后的 dict |
| `client.conquest.main_story_get_info(event_content_id)` | 占领战主线活动页 | `event_content_id: int` | 整理后的 dict |
| `client.conquest.check(event_content_id)` | 占领战状态检查 | `event_content_id: int` | 原始负载 |
| `client.conquest.main_story_check(event_content_id)` | 占领战主线状态检查 | `event_content_id: int` | 原始负载 |
| `client.craft.list()` | 制造页（普通/转化/节点/槽位） | 无 | 整理后的 dict |
| `client.management.banner_list()` | 公告横幅列表 | 无 | 整理后的 dict |
| `client.management.protocol_lock_list()` | 服务端协议开放限制列表 | 无 | 整理后的 dict |
| `client.mission.guide_season_list()` | 指南任务赛季列表 | 无 | 整理后的 dict |
| `client.mission.sync()` | 任务同步 | 无 | 原始负载 |

占领战活动页只有在当前开放且账号可访问对应活动 ID 时才会成功。咖啡厅日常互动/收益、战斗通行证领奖、制造领取、任务领奖等写操作见对应功能页或 [显式确认变更页面](state-changing.md)；咖啡厅完整页见 [咖啡厅页面](cafe.md)，任务页见 [任务页面](mission.md)，战斗通行证见 [战斗通行证页面](battle-pass.md)。

## 活动小游戏页面

对应 Shooting、TableBoard、DreamMaker、Defense、RoadPuzzle、CCG 等活动小游戏。都需要对应当前有效小游戏活动的 `event_content_id`，只读大厅/关卡/任务状态，不进入对局、不结算、不提交成绩。全部返回整理后的 dict。

| 方法 | 游戏里对应 |
| --- | --- |
| `client.mini_game.stage_list(event_content_id)` | 小游戏关卡列表/游玩历史 |
| `client.mini_game.mission_list(event_content_id)` | 小游戏任务页 |
| `client.mini_game.shooting_lobby(event_content_id)` | Shooting 大厅 |
| `client.mini_game.table_board_sync(event_content_id)` | TableBoard 棋盘同步 |
| `client.mini_game.dream_maker_get_info(event_content_id)` | DreamMaker 页 |
| `client.mini_game.defense_get_info(event_content_id)` | Defense 页 |
| `client.mini_game.road_puzzle_get_info(event_content_id)` | RoadPuzzle 页 |
| `client.mini_game.ccg_lobby(event_content_id)` | CCG 卡牌大厅 |

```python
stages = await client.mini_game.stage_list(event_content_id)
```

## 其它只读同步和握手

对应开放条件、可重置内容、内容存档、场景同步、综合战术考试、通关编队记录、贴纸、红点、语音/假名读音、服务器时间等。这一批以登录/检查/同步握手为主，多数直接返回原始负载，少数有 `format_*` 整理。

| 方法 | 游戏里对应 | 参数 | 返回 |
| --- | --- | --- | --- |
| `client.open_condition.list()` | 开放条件列表 | 无 | 整理后的 dict |
| `client.open_condition.event_list(...)` | 占领战/WorldRaid 开放条件 | `conquest_event_ids: list[int] \| None`, `world_raid_season_and_group_ids: list[int] \| None` | 整理后的 dict |
| `client.resetable_content.get()` | 可重置内容 | 无 | 整理后的 dict |
| `client.content_save.get()` | 内容存档 | 无 | 原始负载 |
| `client.field.sync()` | 场景/地图同步（需活跃 Field 上下文） | 无 | 原始负载 |
| `client.time_attack_dungeon.lobby()` | 综合战术考试大厅 | 无 | 原始负载 |
| `client.time_attack_dungeon.login()` | 综合战术考试登录 | 无 | 原始负载 |
| `client.clear_deck.list(clear_deck_key=None)` | 通关编队记录 | `clear_deck_key: int \| None` | 原始负载 |
| `client.clear_deck.grouped_list(clear_deck_key=None)` | 通关编队记录（分组） | `clear_deck_key: int \| None` | 原始负载 |
| `client.sticker.login()` | 贴纸模块登录 | 无 | 原始负载 |
| `client.sticker.lobby(acquire_sticker_unique_ids=None)` | 贴纸册大厅 | `acquire_sticker_unique_ids: list[int] \| None` | 整理后的 dict |
| `client.notification.lobby_check()` | 大厅红点检查 | 无 | 原始负载 |
| `client.notification.event_content_reddot_check()` | 活动内容红点检查 | 无 | 整理后的 dict |
| `client.tts.get_file()` | 语音文件查询 | 无 | 原始负载 |
| `client.tts.get_kana(call_name)` | 称呼假名读音 | `call_name: str` | 整理后的 dict |
| `client.network_time.sync()` | 服务器时间同步 | 无 | 整理后的 dict |

`field.sync()` 需要当前确实处于活跃 Field 上下文；`time_attack_dungeon.lobby()` 在部分账号上需要 NGS-X 校验才会返回数据。贴纸装配（`sticker.use_sticker`）、开放条件设置（`open_condition.set`）、内容存档丢弃（`content_save.discard`）、场景状态变更（`field.scene_changed/end_date`）都是写操作，需要 `confirm=True`，见 [显式确认变更页面](state-changing.md)。

## 注意

- 需 `confirm=True` 的写操作不传确认会抛 `UnsafeOperationError` 且不发包。
- 活动、赛季、关卡、社团、好友、Raid 房间等 ID 一律来自当前账号可见数据或游戏数据配置，不要手填。
- 部分方法因当前账号未开放对应功能或缺少活动上下文，会返回 `OpenConditionClosed`、`DataEntityNotFound`、`DataClassNotFound` 等账号状态类结果，属账号状态而非接口缺陷。
- 逐协议接入状态见仓库根 [`docs/protocols.md`](../../protocols.md)。
