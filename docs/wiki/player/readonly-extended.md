# 扩展只读接口

本页是扩展只读接口的 SDK API 文档。这批接口只读取服务器状态或公开查询结果，不执行领奖、购买、进入战斗、提交成绩、抽卡、好友申请、社团加入、票券选择等状态变更。

调用前需要先完成 `client.login(...)`，或用已持久化的 `session/profile` 调用 `client.restore_session(...)`。示例只展示方法形态，不包含账号凭据、session、profile 或 token 输出。

## 通用约定

所有方法都是异步方法，返回值统一是 `dict`。能从协议文档确定含义的字段会整理成蛇形命名；无法归类的顶层字段放进 `extra`。

返回结构通常长这样：

```python
{
    "业务字段": ...,
    "count": 0,          # 列表类常见
    "extra": {},         # 未显式整理的顶层返回字段
}
```

`extra` 不是错误。服务端经常会附带 `ServerTime`、版本、活动期信息等额外字段，SDK 会保留它们但不把它们当稳定 API 承诺。

## 账号与基础资料

### `client.account.tutorial()`

读取账号教程进度。

| 项 | 内容 |
| --- | --- |
| 协议 | `Account_GetTutorial` |
| 参数 | 无 |
| 返回 | `tutorial_ids`, `count`, `extra` |
| live | 已通过 |

```python
result = await client.account.tutorial()
print(result["tutorial_ids"], result["count"])
```

返回示例：

```python
{
    "tutorial_ids": [100, 101],
    "count": 2,
    "extra": {},
}
```

### `client.attachment.get()`

读取账号当前附件/头像框挂载状态。

| 项 | 内容 |
| --- | --- |
| 协议 | `Attachment_Get` |
| 参数 | 无 |
| 返回 | `account_attachment`, `extra` |
| live | 已通过 |

```python
attachment = await client.attachment.get()
```

### `client.attachment.emblem_list()`

读取已拥有的 Emblem 列表。

| 项 | 内容 |
| --- | --- |
| 协议 | `Attachment_EmblemList` |
| 参数 | 无 |
| 返回 | `emblems`, `count`, `extra` |
| live | 已通过 |

```python
emblems = await client.attachment.emblem_list()
print(emblems["count"])
```

### `client.character_gear.list()`

读取爱用品/角色装备列表。

| 项 | 内容 |
| --- | --- |
| 协议 | `CharacterGear_List` |
| 参数 | 无 |
| 返回 | `character_gears`, `count`, `extra` |
| live | 已通过 |

```python
gears = await client.character_gear.list()
```

### `client.equipment.list()`

读取装备道具列表。

| 项 | 内容 |
| --- | --- |
| 协议 | `Equipment_List` |
| 参数 | 无 |
| 返回 | `equipment_items`, `count`, `extra` |
| live | 已通过 |

```python
equipment = await client.equipment.list()
```

### `client.item.list()`

读取账号物品、限时物品、装备和爱用品数据。

| 项 | 内容 |
| --- | --- |
| 协议 | `Item_List` |
| 参数 | 无 |
| 返回 | `items`, `expiry_items`, `equipment_items`, `character_gears`, `count`, `expiry_count`, `equipment_count`, `character_gear_count`, `extra` |
| live | 已通过 |

```python
items = await client.item.list()
print(items["count"], items["expiry_count"])
```

### `client.echelon.list()`

读取编队和编队预设。

| 项 | 内容 |
| --- | --- |
| 协议 | `Echelon_List` |
| 参数 | 无 |
| 返回 | `echelons`, `presets`, `count`, `preset_count`, `extra` |
| live | 已通过 |

```python
echelons = await client.echelon.list()
```

### `client.memory_lobby.list()`

读取记忆大厅解锁列表。

| 项 | 内容 |
| --- | --- |
| 协议 | `MemoryLobby_List` |
| 参数 | 无 |
| 返回 | `memory_lobbies`, `count`, `extra` |
| live | 已通过 |

```python
memory_lobbies = await client.memory_lobby.list()
```

### `client.scenario.list()`

读取剧情历史、剧情组历史和收藏数据。

| 项 | 内容 |
| --- | --- |
| 协议 | `Scenario_List` |
| 参数 | 无 |
| 返回 | `scenario_history`, `scenario_group_history`, `scenario_collections`, `count`, `group_count`, `collection_count`, `extra` |
| live | 已通过 |

```python
scenario = await client.scenario.list()
```

### `client.school_dungeon.list()`

读取学院交流会/日常副本状态。

| 项 | 内容 |
| --- | --- |
| 协议 | `SchoolDungeon_List` |
| 参数 | 无 |
| 返回 | `stage_history`, `best_teams`, `stage_count`, `best_team_count`, `extra` |
| live | 大号通过；小号未开放时会返回 `OpenConditionClosed` |

```python
school = await client.school_dungeon.list()
```

### `client.system.version()`

读取系统版本信息。该接口不带基础默认字段。

| 项 | 内容 |
| --- | --- |
| 协议 | `System_Version` |
| 参数 | 无 |
| 返回 | `current_version`, `minimum_version`, `is_development`, `extra` |
| live | 已通过 |

```python
version = await client.system.version()
```

### `client.toast.list()`

读取 Toast 提示列表。

| 项 | 内容 |
| --- | --- |
| 协议 | `Toast_List` |
| 参数 | 无 |
| 返回 | `toasts`, `count`, `extra` |
| live | 已通过 |

```python
toasts = await client.toast.list()
```

## 活动与活动内容

### `client.event.list()`

读取当前账号可见的活动列表。

| 项 | 内容 |
| --- | --- |
| 协议 | `Event_GetList` |
| 参数 | 无 |
| 返回 | `events`, `count`, `extra` |
| live | 已通过 |

```python
events = await client.event.list()
```

### `client.event.image(event_id)`

读取活动图片信息。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `event_id` | `int` | 活动 ID。通常应来自活动配置或 `event.list()` 可见活动。 |

返回：`event_image`, `images`, `count`, `extra`。

```python
images = await client.event.image(event_id)
```

### `client.event_content.permanent_list()`

读取永久化活动内容列表。

| 项 | 内容 |
| --- | --- |
| 协议 | `EventContent_PermanentList` |
| 参数 | 无 |
| 返回 | `permanent`, `count`, `extra` |
| live | 已通过 |

```python
permanent = await client.event_content.permanent_list()
```

### 活动内容通用参数

以下接口都需要 `event_content_id`。这个 ID 必须来自当前账号可见、当前开放或永久化且类型匹配的活动内容；不要随便硬填。活动类型不匹配时，服务端会返回 `DataEntityNotFound`、`DataClassNotFound` 或玩法专属错误。

| 方法 | 用途 | 参数 | 返回 |
| --- | --- | --- | --- |
| `adventure_list(event_content_id)` | 活动关卡/冒险状态 | `event_content_id: int` | `stage_history`, `strategy_object_history`, `bonus_rewards`, `already_receive_reward_ids`, `stage_point`, `stage_count`, `extra` |
| `shop_list(event_content_id, category_list=None)` | 活动商店列表 | `event_content_id: int`, `category_list: list[int] \| None` | `shop_infos`, `eligma_history`, `count`, `extra` |
| `box_gacha_shop_list(event_content_id)` | 活动 Box Gacha 商店状态 | `event_content_id: int` | `box_gacha`, `box_gacha_group_id_by_count`, `extra` |
| `collection_list(event_content_id, group_id=None)` | 活动 CG/收藏解锁列表 | `event_content_id: int`, `group_id: int \| None` | `collections`, `count`, `extra` |
| `collection_for_mission(event_content_id)` | 活动任务相关收藏状态 | `event_content_id: int` | `collections`, `count`, `extra` |
| `location_get_info(event_content_id)` | Location 类活动状态 | `event_content_id: int` | `location`, `extra` |
| `sub_event_lobby(event_content_id)` | SubEvent 大厅状态 | `event_content_id: int` | `event_content_change`, `is_on_sub_event`, `extra` |
| `dice_race_lobby(event_content_id)` | DiceRace 大厅状态 | `event_content_id: int` | `dice_race`, `extra` |
| `treasure_lobby(event_content_id)` | Treasure 大厅状态 | `event_content_id: int` | `board_history`, `hidden_image`, `variation_id`, `extra` |
| `clue_search_get_info(event_content_id)` | ClueSearch 活动信息 | `event_content_id: int` | `payload`, `extra` |

```python
permanent = await client.event_content.permanent_list()
event_content_id = permanent["permanent"][0]["EventContentId"]

adventure = await client.event_content.adventure_list(event_content_id)
collections = await client.event_content.collection_list(event_content_id)
missions = await client.event_content.collection_for_mission(event_content_id)
```

`clue_search_get_info()` 当前协议文档没有稳定 Response 字段，因此 SDK 会把原始顶层响应放到 `payload`，不做字段猜测。

## 商店和招募只读

这些接口只读招募状态，不购买、不抽卡、不保存结果。

### `client.shop.gacha_recruit_list()`

读取当前招募列表和免费招募历史。

| 项 | 内容 |
| --- | --- |
| 协议 | `Shop_GachaRecruitList` |
| 参数 | 无 |
| 返回 | `shop_recruits`, `free_recruit_history`, `account_currency`, `count`, `free_history_count`, `extra` |
| live | 已通过 |

```python
recruits = await client.shop.gacha_recruit_list()
```

### `client.shop.beforehand_gacha_get()`

读取 Beforehand Gacha 状态。

| 项 | 内容 |
| --- | --- |
| 协议 | `Shop_BeforehandGachaGet` |
| 参数 | 无 |
| 返回 | `beforehand_gacha`, `beforehand_gacha_history`, `extra` |
| live | 已通过 |

```python
beforehand = await client.shop.beforehand_gacha_get()
```

### `client.shop.pickup_selection_gacha_get(shop_recruit_id)`

读取自选 Pickup 招募状态。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `shop_recruit_id` | `int` | 当前开放自选 Pickup 招募的 ID，应来自招募列表。 |

返回：`pickup_selection_gacha`, `shop_recruit`, `extra`。

```python
recruits = await client.shop.gacha_recruit_list()
shop_recruit_id = recruits["shop_recruits"][0]["ShopRecruitId"]
state = await client.shop.pickup_selection_gacha_get(shop_recruit_id)
```

本轮 live 账号没有有效自选 Pickup 招募，错误为 `ShopInfoNotFound`。

## 好友查询

好友查询接口不会发送、接受、拒绝或取消好友申请。状态变更好友接口见 `state-changing.md`。

### `client.friend.list()`

读取好友、收到的申请、已发送申请、屏蔽列表和名片背景。

返回：`id_card_backgrounds`, `friends`, `received_requests`, `sent_requests`, `blocked_friends`, `friend_id_card`, `count`, `received_count`, `sent_count`, `blocked_count`, `extra`。

```python
friends = await client.friend.list()
print(friends["count"], friends["received_count"])
```

### `client.friend.detailed_info(friend_account_id)`

读取某个账号的详细信息。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `friend_account_id` | `int` | 好友或目标账号 ID。 |

返回：`detailed_account_info`, `friend`, `extra`。

```python
friends = await client.friend.list()
friend_account_id = friends["friends"][0]["AccountId"]
info = await client.friend.detailed_info(friend_account_id)
```

### `client.friend.id_card()`

读取自己的好友名片。

返回：`id_card`, `extra`。

```python
id_card = await client.friend.id_card()
```

### `client.friend.search(friend_code=None, level_option=None)`

搜索好友。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `friend_code` | `str \| None` | 好友码。不传则按服务端默认搜索行为。 |
| `level_option` | `int \| None` | 等级筛选枚举值。 |

返回：`friends`, `count`, `extra`。

```python
result = await client.friend.search(friend_code="ABCDEF")
```

### `client.friend.list_by_ids(target_account_ids)`

按账号 ID 批量查询好友信息。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `target_account_ids` | `list[int] \| tuple[int, ...]` | 目标账号 ID 列表，不能为空。 |

返回：`friends`, `count`, `extra`。

```python
result = await client.friend.list_by_ids([target_account_id])
```

## 社团查询

### `client.clan.lobby()`

读取社团大厅、当前账号社团、成员和默认展示社团。

返回：`irc_config`, `account_clan`, `default_exposed_clans`, `account_clan_member`, `clan_members`, `member_count`, `default_exposed_count`, `extra`。

```python
lobby = await client.clan.lobby()
```

### `client.clan.search(...)`

搜索社团。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `clan_join_option` | `int \| None` | 加入条件筛选。 |
| `clan_unique_code` | `str \| None` | 社团唯一码。 |
| `search_string` | `str \| None` | 搜索文本。 |

返回：`clans`, `count`, `extra`。

```python
clans = await client.clan.search(search_string="test")
```

### `client.clan.member(clan_db_id, member_account_id)`

读取社团单个成员信息。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `clan_db_id` | `int` | 社团 DB ID。 |
| `member_account_id` | `int` | 成员账号 ID。 |

返回：`clan`, `clan_member`, `detailed_account_info`, `extra`。

```python
lobby = await client.clan.lobby()
clan_db_id = lobby["account_clan"]["ServerId"]
member_account_id = lobby["clan_members"][0]["AccountId"]
member = await client.clan.member(clan_db_id, member_account_id)
```

### `client.clan.member_list(clan_db_id)`

读取社团成员列表。

返回：`clan`, `clan_members`, `count`, `extra`。

```python
members = await client.clan.member_list(clan_db_id)
```

### `client.clan.my_assist_list()`

读取自己的社团助战槽位。

返回：`assist_slots`, `count`, `extra`。

```python
my_assists = await client.clan.my_assist_list()
```

### `client.clan.all_assist_list(...)`

读取社团全部助战列表。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `echelon_type` | `int` | 编队/玩法类型枚举，必填。 |
| `is_practice` | `bool` | 是否练习模式。默认 `False`。 |
| `pending_assist_use_info` | `list[dict] \| tuple[dict, ...] \| None` | 待使用助战信息。通常传空列表。 |

返回：`assist_characters`, `assist_character_rent_history`, `clan_db_id`, `count`, `extra`。

```python
assists = await client.clan.all_assist_list(
    echelon_type=0,
    is_practice=False,
    pending_assist_use_info=[],
)
```

## Raid 与排行查询

### `client.raid.list(...)`

读取可见 Raid 房间列表。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `raid_boss_group` | `str \| None` | Boss 组筛选。 |
| `raid_difficulty` | `int \| None` | 难度筛选。 |
| `raid_room_sort_option` | `int \| None` | 排序选项。 |

返回：`create_raids`, `enter_raids`, `list_raids`, `count`, `extra`。

```python
raids = await client.raid.list()
```

### `client.raid.complete_list()`

读取已完成 Raid 列表和赛季摘要。

返回：`raids`, `stacked_damage`, `receive_reward_ids`, `current_season_unique_id`, `count`, `extra`。

```python
completed = await client.raid.complete_list()
```

### `client.raid.search(secret_code=None, tags=None)`

搜索 Raid 房间。

返回：`raids`, `count`, `extra`。

```python
result = await client.raid.search(secret_code=None, tags=[])
```

### `client.raid.lobby()`

读取 Raid 大厅信息。

返回：`season_type`, `raid_give_up`, `raid_lobby_info`, `account_currency`, `parcel_result`, `extra`。

```python
lobby = await client.raid.lobby()
```

### `client.raid.opponent_list(...)`

读取 Raid 排名邻近玩家列表。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `is_first_request` | `bool \| None` | 是否首次请求。 |
| `is_upper` | `bool \| None` | 是否查询上方排名。 |
| `rank` | `int \| None` | 基准排名。 |
| `score` | `int \| None` | 基准分数。 |
| `search_type` | `int \| None` | 搜索类型。 |

返回：`opponents`, `count`, `extra`。

```python
opponents = await client.raid.opponent_list(
    is_first_request=True,
    is_upper=False,
    rank=0,
    score=0,
    search_type=0,
)
```

### `client.raid.get_best_team(search_account_id)`

读取指定账号的 Raid 最佳队伍。

返回：`team_settings`, `count`, `extra`。

```python
team = await client.raid.get_best_team(search_account_id)
```

### `client.raid.ranking_index()`

读取 Raid 排名分段索引。

返回：`rank_brackets`, `count`, `extra`。

```python
index = await client.raid.ranking_index()
```

### 制约解除决战

| 方法 | 用途 | 参数 | 返回 |
| --- | --- | --- | --- |
| `client.eliminate_raid.lobby()` | 制约解除决战大厅 | 无 | `lobby_info`, `give_up`, `season_type`, `account_currency`, `parcel_result`, `extra` |
| `client.eliminate_raid.opponent_list(...)` | 排名邻近玩家 | `boss_group_index`, `is_first_request`, `is_upper`, `rank`, `score`, `search_type` 均可选 | `opponents`, `count`, `extra` |
| `client.eliminate_raid.get_best_team(search_account_id)` | 指定账号最佳队伍 | `search_account_id: int` | `team_settings_by_key`, `team_settings`, `count`, `extra` |
| `client.eliminate_raid.ranking_index()` | 排名分段索引 | 无 | `rank_brackets`, `count`, `extra` |

```python
lobby = await client.eliminate_raid.lobby()
ranking = await client.eliminate_raid.ranking_index()
```

### `client.permanent_raid.lobby()`

读取常驻 Raid 大厅信息。

返回：`lobby_infos`, `seasons`, `account_currency`, `count`, `season_count`, `extra`。

```python
permanent_raid = await client.permanent_raid.lobby()
```

### WorldRaid

WorldRaid 需要当前开放的 `content_type` 和 `season_id`。

| 方法 | 用途 | 参数 | 返回 |
| --- | --- | --- | --- |
| `client.world_raid.lobby(content_type, season_id)` | 世界 Raid 大厅 | `content_type: int`, `season_id: int` | `clear_history`, `local_bosses`, `boss_groups`, `clear_history_count`, `local_boss_count`, `boss_group_count`, `extra` |
| `client.world_raid.boss_list(content_type, season_id, request_only_world_boss_data=False)` | 世界 Raid Boss 列表 | `content_type: int`, `season_id: int`, `request_only_world_boss_data: bool` | `boss_list_info`, `count`, `extra` |

```python
lobby = await client.world_raid.lobby(content_type, season_id)
bosses = await client.world_raid.boss_list(content_type, season_id)
```

本轮 live 没有拿到 WorldRaid 候选参数。

## 其他玩法和系统查询

### `client.battle_pass.get_info(battle_pass_id)`

读取 BattlePass 信息。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `battle_pass_id` | `int` | BattlePass ID。需要来自当前活动/配置。 |

返回：`battle_pass_info`, `extra`。

```python
info = await client.battle_pass.get_info(battle_pass_id)
```

### `client.battle_pass.mission_list(battle_pass_id)`

读取 BattlePass 任务列表。

返回：`mission_history_unique_ids`, `progress`, `count`, `extra`。

```python
missions = await client.battle_pass.mission_list(battle_pass_id)
```

### `client.cafe.trophy_history()`

读取咖啡厅奖杯历史。

返回：`trophy_history`, `count`, `extra`。

```python
trophy = await client.cafe.trophy_history()
```

### `client.conquest.get_info(event_content_id)`

读取占领战活动信息。

返回：`conquest_info`, `conquered_tiles`, `echelons`, `event_objects`, `difficulty_to_step`, `is_first_enter`, `display_infos`, `conquered_tile_count`, `echelon_count`, `event_object_count`, `extra`。

```python
conquest = await client.conquest.get_info(event_content_id)
```

### `client.conquest.main_story_get_info(event_content_id)`

读取占领战主线型活动信息。

返回：`main_stories`, `count`, `extra`。

```python
story = await client.conquest.main_story_get_info(event_content_id)
```

### `client.craft.list()`

读取制造和转化制造状态。

返回：`craft_infos`, `shifting_craft_infos`, `craft_nodes`, `craft_slots`, `count`, `shifting_count`, `node_count`, `slot_count`, `extra`。

```python
craft = await client.craft.list()
```

### `client.management.banner_list()`

读取管理公告/横幅列表。

返回：`banners`, `count`, `extra`。

```python
banners = await client.management.banner_list()
```

### `client.management.protocol_lock_list()`

读取协议锁列表。

返回：`protocol_locks`, `count`, `extra`。

```python
locks = await client.management.protocol_lock_list()
```

### `client.mission.guide_season_list()`

读取指南任务赛季列表。

返回：`guide_mission_seasons`, `count`, `extra`。

```python
seasons = await client.mission.guide_season_list()
```

## 小游戏查询

小游戏接口都需要 `event_content_id`，必须对应当前有效的小游戏活动。

| 方法 | 用途 | 返回 |
| --- | --- | --- |
| `stage_list(event_content_id)` | 小游戏关卡/历史列表 | `stages`, `count`, `extra` |
| `mission_list(event_content_id)` | 小游戏任务列表 | `mission_history_unique_ids`, `progress`, `count`, `extra` |
| `shooting_lobby(event_content_id)` | Shooting 小游戏大厅 | `shooting_lobby`, `stage_history`, `account_currency`, `stage_count`, `extra` |
| `table_board_sync(event_content_id)` | TableBoard 同步 | `table_board`, `stages`, `account_currency`, `stage_count`, `extra` |
| `dream_maker_get_info(event_content_id)` | DreamMaker 信息 | `dream_maker`, `schedules`, `account_currency`, `schedule_count`, `extra` |
| `defense_get_info(event_content_id)` | Defense 信息 | `defense`, `stage_history`, `account_currency`, `stage_count`, `extra` |
| `road_puzzle_get_info(event_content_id)` | RoadPuzzle 信息 | `road_puzzle`, `stage_history`, `account_currency`, `stage_count`, `extra` |
| `ccg_lobby(event_content_id)` | CCG 大厅 | `ccg`, `decks`, `account_currency`, `deck_count`, `extra` |

```python
stages = await client.mini_game.stage_list(event_content_id)
missions = await client.mini_game.mission_list(event_content_id)
shooting = await client.mini_game.shooting_lobby(event_content_id)
```

本轮 live 中 `stage_list`、`mission_list`、`shooting_lobby` 有成功样本；其它小游戏接口需要对应开放赛季。

## Live 验证

2026-06-16 使用小号优先、大号兜底做过 live 验证。验证过程只输出接口名、计数和错误码摘要，不保存请求包、响应包或 dump，不输出 session/profile/token。

已在至少一个账号上 live 通过的 54 个接口：

```text
account.tutorial
attachment.get
attachment.emblem_list
battle_pass.get_info
battle_pass.mission_list
cafe.trophy_history
character_gear.list
clan.lobby
clan.search
clan.member
clan.member_list
clan.my_assist_list
clan.all_assist_list
craft.list
echelon.list
eliminate_raid.lobby
eliminate_raid.opponent_list
eliminate_raid.get_best_team
eliminate_raid.ranking_index
equipment.list
event.list
event.image
event_content.adventure_list
event_content.collection_list
event_content.collection_for_mission
event_content.dice_race_lobby
event_content.permanent_list
friend.list
friend.detailed_info
friend.id_card
friend.search
friend.list_by_ids
item.list
management.banner_list
management.protocol_lock_list
memory_lobby.list
mini_game.stage_list
mini_game.mission_list
mini_game.shooting_lobby
mission.guide_season_list
permanent_raid.lobby
raid.list
raid.complete_list
raid.search
raid.lobby
raid.opponent_list
raid.get_best_team
raid.ranking_index
scenario.list
school_dungeon.list
shop.gacha_recruit_list
shop.beforehand_gacha_get
system.version
toast.list
```

当前账号或当前活动上下文不足，已封装但本轮 live 未得到成功响应的 16 个接口：

| 方法 | 本轮 live 结果 | 后续验证条件 |
| --- | --- | --- |
| `conquest.get_info(event_content_id)` | `ErrorCode=16 DataEntityNotFound` | 需要当前开放且账号可访问的占领战活动 ID。 |
| `conquest.main_story_get_info(event_content_id)` | `ErrorCode=16 DataEntityNotFound` | 需要当前开放且账号可访问的占领战主线活动 ID。 |
| `event_content.shop_list(event_content_id)` | `ErrorCode=16 DataEntityNotFound` | 需要带活动商店的有效活动内容 ID。 |
| `event_content.box_gacha_shop_list(event_content_id)` | `ErrorCode=15 DataClassNotFound` | 需要带箱式抽奖商店的有效活动内容 ID。 |
| `event_content.location_get_info(event_content_id)` | `ErrorCode=16 DataEntityNotFound` | 需要带地点玩法的有效活动内容 ID。 |
| `event_content.sub_event_lobby(event_content_id)` | `ErrorCode=15 DataClassNotFound` | 需要带 SubEvent 的有效活动内容 ID。 |
| `event_content.treasure_lobby(event_content_id)` | `ErrorCode=500 ServerFailedToHandleRequest` | 需要带 Treasure 玩法的有效活动内容 ID。 |
| `event_content.clue_search_get_info(event_content_id)` | `ErrorCode=16 DataEntityNotFound` | 需要带 ClueSearch 玩法的有效活动内容 ID。 |
| `mini_game.table_board_sync(event_content_id)` | `ErrorCode=37012 MiniGameTableBoardInvalidSeason` | 需要当前有效 TableBoard 小游戏赛季。 |
| `mini_game.dream_maker_get_info(event_content_id)` | `ErrorCode=500 ServerFailedToHandleRequest` | 需要当前有效 DreamMaker 小游戏活动。 |
| `mini_game.defense_get_info(event_content_id)` | `ErrorCode=15 DataClassNotFound` | 需要当前有效 Defense 小游戏活动。 |
| `mini_game.road_puzzle_get_info(event_content_id)` | `ErrorCode=16 DataEntityNotFound` | 需要当前有效 RoadPuzzle 小游戏活动。 |
| `mini_game.ccg_lobby(event_content_id)` | `ErrorCode=500 ServerFailedToHandleRequest` | 需要当前有效 CCG 小游戏活动。 |
| `shop.pickup_selection_gacha_get(shop_recruit_id)` | `ErrorCode=10005 ShopInfoNotFound` | 需要当前开放自选 Pickup 招募，并从招募列表取得有效 `ShopRecruitId`。 |
| `world_raid.lobby(content_type, season_id)` | 无候选参数 | 需要当前开放 WorldRaid 的 `ContentType` 和 `SeasonId`。 |
| `world_raid.boss_list(content_type, season_id)` | 无候选参数 | 需要当前开放 WorldRaid 的 `ContentType` 和 `SeasonId`。 |
